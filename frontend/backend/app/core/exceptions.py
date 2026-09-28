from typing import Any, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "BAD_REQUEST",
        message: str = "An error occurred",
        details: Optional[Any] = None
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.details = details


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, code="NOT_FOUND", message=message, details=details)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication credentials were invalid", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, code="UNAUTHORIZED", message=message, details=details)


class ForbiddenException(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, code="FORBIDDEN", message=message, details=details)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, code="VALIDATION_ERROR", message=message, details=details)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id
            }
        }
    )
