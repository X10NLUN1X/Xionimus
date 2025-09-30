"""
Standardized Error Handling for Xionimus AI
Provides consistent error responses across all API endpoints
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Error Response Models
# ============================================================================

class ErrorDetail(BaseModel):
    """Standard error detail structure"""
    code: str
    message: str
    field: Optional[str] = None
    timestamp: str = datetime.utcnow().isoformat()

class ErrorResponse(BaseModel):
    """Standard error response structure"""
    success: bool = False
    error: ErrorDetail
    request_id: Optional[str] = None

# ============================================================================
# Custom Exception Classes
# ============================================================================

class XionimusException(HTTPException):
    """Base exception for all custom Xionimus errors"""
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        field: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.field = field
        super().__init__(status_code=status_code, detail=message, headers=headers)

class AuthenticationError(XionimusException):
    """Authentication failed"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_REQUIRED",
            message=message
        )

class AuthorizationError(XionimusException):
    """Insufficient permissions"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message=message
        )

class ResourceNotFoundError(XionimusException):
    """Resource not found"""
    def __init__(self, resource: str = "Resource", resource_id: str = ""):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=message
        )

class ValidationError(XionimusException):
    """Validation error"""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            field=field
        )

class DatabaseError(XionimusException):
    """Database operation failed"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="DATABASE_ERROR",
            message=message
        )

class ExternalServiceError(XionimusException):
    """External service (AI, GitHub, etc.) error"""
    def __init__(self, service: str, message: str):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="EXTERNAL_SERVICE_ERROR",
            message=f"{service}: {message}"
        )

class RateLimitError(XionimusException):
    """Rate limit exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT",
            message=message
        )

# ============================================================================
# Error Handlers
# ============================================================================

async def xionimus_exception_handler(request: Request, exc: XionimusException):
    """Handle custom Xionimus exceptions"""
    logger.warning(f"XionimusException: {exc.code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.detail,
                "field": exc.field,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": errors,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    # Don't expose internal errors in production
    message = "An internal error occurred"
    if request.app.debug:
        message = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

# ============================================================================
# Success Response Helper
# ============================================================================

def success_response(data: Any = None, message: Optional[str] = None) -> Dict:
    """Create a standardized success response"""
    response = {
        "success": True
    }
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
    
    return response
