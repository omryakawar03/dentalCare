from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, status


@dataclass(frozen=True)
class Principal:
    subject_id: UUID
    organization_id: UUID
    role: str
    ward_id: UUID | None = None


def require_scope(
    principal: Principal,
    organization_id: UUID,
    ward_id: UUID | None = None,
    *,
    assigned_to_principal: bool = False,
) -> None:
    """Fail closed for cross-tenant and out-of-ward requests."""
    if principal.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    if principal.role == "WARD_OFFICER" and (ward_id is None or principal.ward_id != ward_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    if principal.role == "FIELD_OFFICER" and not assigned_to_principal:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Assigned work only")
