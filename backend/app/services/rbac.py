from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Membership, MembershipRole, Permission, Role, RolePermission


async def has_permission(
    db: AsyncSession, user_id: UUID, organization_id: UUID, clinic_id: UUID, permission_key: str
) -> bool:
    """Resolve an effective permission only through an active organization membership."""
    result = await db.execute(
        select(Permission.id)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(MembershipRole, MembershipRole.role_id == Role.id)
        .join(Membership, Membership.id == MembershipRole.membership_id)
        .where(
            Membership.user_id == user_id,
            Membership.organization_id == organization_id,
            Membership.is_active.is_(True),
            (MembershipRole.clinic_id == clinic_id) | (MembershipRole.clinic_id.is_(None)),
            Permission.key == permission_key,
        )
        .limit(1)
    )
    return result.scalar_one_or_none() is not None
