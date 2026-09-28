import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Principal, current_principal, membership_roles
from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    hash_refresh_token,
    hash_password,
    new_refresh_token,
    verify_password,
)
from app.models import AuditEvent, Clinic, ClinicGrant, Membership, Organization, RefreshSession, User
from app.schemas.auth import (
    LoginRequest,
    MeResponse,
    MembershipSummary,
    RefreshRequest,
    RoleGrantSummary,
    TokenPair,
)
from app.schemas.common import Success

router = APIRouter(prefix="/auth", tags=["authentication"])
DUMMY_PASSWORD_HASH = hash_password("unused-dummy-credential-value")


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "INVALID_CREDENTIALS", "message": "Email or password is incorrect"},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def _issue_tokens(
    db: AsyncSession,
    user: User,
    family_id=None,
    family_expires_at: datetime | None = None,
) -> TokenPair:
    refresh_token = new_refresh_token()
    expires_at = family_expires_at or datetime.now(UTC) + timedelta(days=settings.refresh_token_days)
    session = RefreshSession(
        user_id=user.id,
        family_id=family_id or uuid4(),
        family_expires_at=expires_at,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=expires_at,
    )
    db.add(session)
    await db.flush()
    access_token = create_access_token(user.id, session.id)
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_minutes * 60,
    )


async def _enforce_login_limit(request: Request, email: str) -> None:
    client_ip = request.client.host if request.client else "unknown"
    keys = [
        "auth:login:pair:" + hmac.new(
            settings.jwt_secret.get_secret_value().encode(),
            f"{client_ip}:{email.lower()}".encode(),
            hashlib.sha256,
        ).hexdigest(),
        "auth:login:ip:" + hmac.new(
            settings.jwt_secret.get_secret_value().encode(), client_ip.encode(), hashlib.sha256
        ).hexdigest(),
    ]
    try:
        redis = request.app.state.redis
        counts = []
        for key in keys:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, 900)
            counts.append(count)
    except RedisError:
        raise HTTPException(
            status_code=503,
            detail={"code": "AUTH_TEMPORARILY_UNAVAILABLE", "message": "Sign-in is temporarily unavailable"},
        ) from None
    if counts[0] > 10 or counts[1] > 60:
        raise HTTPException(
            status_code=429,
            detail={"code": "LOGIN_RATE_LIMITED", "message": "Too many sign-in attempts. Try again later."},
            headers={"Retry-After": "900"},
        )
@router.post("/login", response_model=Success[TokenPair])
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    await _enforce_login_limit(request, body.email)
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    user = result.scalar_one_or_none()
    password_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
    password_valid = verify_password(body.password, password_hash)
    if user is None or not user.is_active or not password_valid:
        db.add(
            AuditEvent(
                action="auth.login_denied",
                entity_type="login_attempt",
                request_id=getattr(request.state, "request_id", None),
                outcome="denied",
            )
        )
        await db.commit()
        raise _unauthorized()
    tokens = await _issue_tokens(db, user)
    db.add(
        AuditEvent(
            actor_user_id=user.id,
            action="auth.login",
            entity_type="user_session",
            entity_id=str(user.id),
            request_id=getattr(request.state, "request_id", None),
        )
    )
    await db.commit()
    return Success(data=tokens, message="Signed in successfully")


@router.post("/refresh", response_model=Success[TokenPair])
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RefreshSession)
        .where(RefreshSession.token_hash == hash_refresh_token(body.refresh_token))
        .with_for_update()
    )
    session = result.scalar_one_or_none()
    now = datetime.now(UTC)
    if session is None or session.expires_at <= now or session.family_expires_at <= now:
        raise _unauthorized()
    if session.revoked_at is not None:
        # A rotated refresh token was replayed. Revoke the account's outstanding sessions.
        if session.replaced_by_id is not None:
            await db.execute(
                RefreshSession.__table__.update()
                .where(
                    RefreshSession.family_id == session.family_id,
                    RefreshSession.revoked_at.is_(None),
                )
                .values(revoked_at=now)
            )
            await db.commit()
        raise _unauthorized()
    user = await db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise _unauthorized()
    session.revoked_at = now
    tokens = await _issue_tokens(
        db,
        user,
        family_id=session.family_id,
        family_expires_at=session.family_expires_at,
    )
    # Link rotation while retaining the prior session for reuse detection/audit.
    await db.flush()
    latest = await db.scalar(
        select(RefreshSession).where(RefreshSession.token_hash == hash_refresh_token(tokens.refresh_token))
    )
    session.replaced_by_id = latest.id if latest else None
    await db.commit()
    return Success(data=tokens, message="Session refreshed")


@router.post("/logout", response_model=Success[dict])
async def logout(
    principal: Principal = Depends(current_principal), db: AsyncSession = Depends(get_db)
):
    session = await db.get(RefreshSession, principal.session_id)
    if session and session.revoked_at is None:
        session.revoked_at = datetime.now(UTC)
        db.add(
            AuditEvent(
                actor_user_id=principal.user.id,
                action="auth.logout",
                entity_type="user_session",
                entity_id=str(principal.session_id),
            )
        )
        await db.commit()
    return Success(data={"revoked": True}, message="Signed out")


@router.get("/me", response_model=Success[MeResponse])
async def me(
    principal: Principal = Depends(current_principal), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Membership, Organization)
        .join(Organization, Organization.id == Membership.organization_id)
        .where(
            Membership.user_id == principal.user.id,
            Membership.is_active.is_(True),
            Organization.is_active.is_(True),
        )
    )
    memberships: list[MembershipSummary] = []
    for membership, organization in result.all():
        clinic_rows = await db.execute(
            select(ClinicGrant.clinic_id)
            .join(Clinic, Clinic.id == ClinicGrant.clinic_id)
            .where(ClinicGrant.membership_id == membership.id, Clinic.is_active.is_(True))
        )
        memberships.append(
            MembershipSummary(
                id=membership.id,
                organization_id=organization.id,
                organization_name=organization.name,
                roles=[
                    RoleGrantSummary(key=role_key, clinic_id=clinic_id)
                    for role_key, clinic_id in await membership_roles(db, membership.id)
                ],
                clinic_ids=list(clinic_rows.scalars()),
            )
        )
    return Success(
        data=MeResponse(
            id=principal.user.id,
            email=principal.user.email,
            full_name=principal.user.full_name,
            is_platform_admin=principal.user.is_platform_admin,
            memberships=memberships,
        )
    )
