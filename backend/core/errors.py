from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from .logger import setup_logger

logger = setup_logger("cad_copilot.errors")

class ErrorDetail(BaseModel):
    type: str
    message: str
    details: Optional[str] = None

class ErrorResponse(BaseModel):
    status: str
    code: str
    stl_url: Optional[str] = None
    error: ErrorDetail

class CopilotException(Exception):
    """Base exception for Copilot errors."""
    def __init__(self, error_type: str, message: str, code: str, status_code: int = 400, details: Optional[str] = None):
        self.error_type = error_type
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class ValidationError(CopilotException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__("validation_error", message, "ERR_VALIDATION", 400, details)

class ExecutionError(CopilotException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__("execution_error", message, "ERR_EXECUTION", 500, details)

class TimeoutError(CopilotException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__("timeout", message, "ERR_TIMEOUT", 408, details)

class LLMError(CopilotException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__("llm_error", message, "ERR_LLM", 502, details)

async def copilot_exception_handler(request: Request, exc: CopilotException):
    logger.error(f"[{exc.error_type.upper()}] {exc.message} | Details: {exc.details}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status="error",
            code=exc.code,
            error=ErrorDetail(
                type=exc.error_type,
                message=exc.message,
                details=exc.details
            )
        ).model_dump()
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status="error",
            code="ERR_INTERNAL",
            error=ErrorDetail(
                type="internal_error",
                message="An unexpected server error occurred.",
                details=str(exc)  # Expose for debugging
            )
        ).model_dump()
    )
