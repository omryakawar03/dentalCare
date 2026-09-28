from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=40, max_length=256)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class ClinicSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    timezone: str


class RoleGrantSummary(BaseModel):
    key: str
    clinic_id: UUID | None


class MembershipSummary(BaseModel):
    id: UUID
    organization_id: UUID
    organization_name: str
    roles: list[RoleGrantSummary]
    clinic_ids: list[UUID]


class MeResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    is_platform_admin: bool
    memberships: list[MembershipSummary]
