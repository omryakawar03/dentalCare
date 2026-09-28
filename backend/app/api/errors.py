from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorBody, ErrorResponse


async def http_error_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    body = ErrorResponse(
        error=ErrorBody(
            code=detail.get("code", "REQUEST_ERROR"),
            message=detail.get("message", str(exc.detail)),
            fields=detail.get("fields"),
        ),
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump(exclude_none=True), headers=exc.headers)
