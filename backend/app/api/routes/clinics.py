from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Principal, clinic_list_permission_query, current_principal
from app.core.database import get_db
from app.models import Clinic
from app.schemas.auth import ClinicSummary
from app.schemas.common import Success

router = APIRouter(prefix="/clinics", tags=["clinics"])


@router.get("", response_model=Success[list[ClinicSummary]])
async def list_clinics(
    organization_id: UUID | None = None,
    principal: Principal = Depends(current_principal),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Clinic)
        .where(
            Clinic.is_active.is_(True),
            clinic_list_permission_query(principal.user.id),
        )
        .order_by(Clinic.name)
    )
    if organization_id:
        query = query.where(Clinic.organization_id == organization_id)
    rows = await db.execute(query)
    return Success(data=[ClinicSummary.model_validate(clinic) for clinic in rows.scalars()])
