from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from ..schemas.user import ErrorResponse, HTTPValidationError, ValidationError

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions and return a standardized error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=str(exc.detail),
            detail=None
        ).model_dump()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and return a standardized error response."""
    validation_errors = []
    for error in exc.errors():
        validation_errors.append(
            ValidationError(
                loc=error["loc"],
                msg=error["msg"],
                type=error["type"]
            )
        )
    
    return JSONResponse(
        status_code=422,
        content=HTTPValidationError(
            detail=validation_errors
        ).model_dump()
    ) 