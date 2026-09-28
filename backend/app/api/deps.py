from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import (
    Clinic,
    ClinicGrant,
    Membership,
    MembershipRole,
    Organization,
    Permission,
    RefreshSession,
    Role,
    RolePermission,
    User,
)
from app.services.rbac import has_permission

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    user: User
    session_id: UUID


async def current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> Principal:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "AUTHENTICATION_REQUIRED", "message": "Sign in to continue"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise unauthorized
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
        session_id = UUID(payload["sid"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauthorized from None
    session = await db.get(RefreshSession, session_id)
    if (
        session is None
        or session.user_id != user_id
        or session.revoked_at is not None
        or session.expires_at <= datetime.now(UTC)
    ):
        raise unauthorized
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized
    return Principal(user=user, session_id=session_id)


async def require_clinic_access(
    clinic_id: UUID,
    principal: Principal = Depends(current_principal),
    db: AsyncSession = Depends(get_db),
) -> tuple[UUID, UUID]:
    grants = await db.execute(
        select(Membership.organization_id, ClinicGrant.clinic_id)
        .join(
            ClinicGrant,
            and_(
                ClinicGrant.membership_id == Membership.id,
                ClinicGrant.organization_id == Membership.organization_id,
            ),
        )
        .join(
            Clinic,
            and_(Clinic.organization_id == ClinicGrant.organization_id, Clinic.id == ClinicGrant.clinic_id),
        )
        .join(Organization, Organization.id == Membership.organization_id)
        .where(
            Membership.user_id == principal.user.id,
            Membership.is_active.is_(True),
            ClinicGrant.clinic_id == clinic_id,
            Clinic.is_active.is_(True),
            Organization.is_active.is_(True),
        )
    )
    result = grants.first()
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "CLINIC_NOT_FOUND", "message": "Clinic not found"},
        )
    return result.organization_id, result.clinic_id


def require_clinic_permission(permission_key: str):
    async def dependency(
        clinic_id: UUID,
        principal: Principal = Depends(current_principal),
        db: AsyncSession = Depends(get_db),
    ) -> tuple[UUID, UUID]:
        organization_id, granted_clinic_id = await require_clinic_access(clinic_id, principal, db)
        if not await has_permission(db, principal.user.id, organization_id, granted_clinic_id, permission_key):
            raise HTTPException(
                status_code=403,
                detail={"code": "PERMISSION_DENIED", "message": "You do not have permission to do this"},
            )
        return organization_id, granted_clinic_id

    return dependency


async def membership_roles(db: AsyncSession, membership_id: UUID) -> list[tuple[str, UUID | None]]:
    rows = await db.execute(
        select(Role.key, MembershipRole.clinic_id)
        .join(MembershipRole, MembershipRole.role_id == Role.id)
        .where(MembershipRole.membership_id == membership_id)
    )
    return list(rows.tuples())


def clinic_list_permission_query(user_id: UUID):
    """Return an authorization predicate for clinic directory visibility."""
    return (
        select(Clinic.id)
        .join(
            ClinicGrant,
            and_(ClinicGrant.clinic_id == Clinic.id, ClinicGrant.organization_id == Clinic.organization_id),
        )
        .join(Organization, Organization.id == Clinic.organization_id)
        .join(
            Membership,
            and_(
                Membership.id == ClinicGrant.membership_id,
                Membership.organization_id == ClinicGrant.organization_id,
            ),
        )
        .join(
            MembershipRole,
            and_(
                MembershipRole.membership_id == Membership.id,
                MembershipRole.organization_id == Membership.organization_id,
                or_(MembershipRole.clinic_id.is_(None), MembershipRole.clinic_id == Clinic.id),
            ),
        )
        .join(Role, Role.id == MembershipRole.role_id)
        .join(RolePermission, RolePermission.role_id == Role.id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .where(
            Membership.user_id == user_id,
            Membership.is_active.is_(True),
            Organization.is_active.is_(True),
            Permission.key == "clinics.read",
        )
        .correlate(Clinic)
        .exists()
    )
