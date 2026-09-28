from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Success(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: str | None = None
    meta: dict = Field(default_factory=dict)


class ErrorBody(BaseModel):
    code: str
    message: str
    fields: dict[str, str] | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorBody
    request_id: str | None = None
