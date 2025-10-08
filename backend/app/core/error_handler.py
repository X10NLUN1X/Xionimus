"""
Enhanced Error Handler
Proper error handling without bare except clauses
"""

import logging
import traceback
from typing import Any, Dict, Optional, Type
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    Centralized error handling utility
    Replaces bare except clauses with proper error handling
    """
    
    @staticmethod
    def handle_exception(
        e: Exception,
        context: str = "Operation",
        status_code: int = 500,
        log_traceback: bool = True,
        raise_http: bool = False
    ) -> Dict[str, Any]:
        """
        Handle an exception with proper logging and response
        
        Args:
            e: Exception to handle
            context: Context description for logging
            status_code: HTTP status code
            log_traceback: Whether to log full traceback
            raise_http: Whether to raise HTTPException
            
        Returns:
            Dict with error information
            
        Raises:
            HTTPException: If raise_http is True
        """
        error_type = type(e).__name__
        error_msg = str(e)
        
        # Log the error
        if log_traceback:
            logger.error(f"{context} failed: {error_type}: {error_msg}")
            logger.error(traceback.format_exc())
        else:
            logger.error(f"{context} failed: {error_type}: {error_msg}")
        
        # Prepare error response
        error_response = {
            'success': False,
            'error': error_msg,
            'error_type': error_type,
            'context': context
        }
        
        # Raise HTTP exception if requested
        if raise_http:
            raise HTTPException(status_code=status_code, detail=error_msg)
        
        return error_response
    
    @staticmethod
    def safe_execute(
        func: callable,
        *args,
        context: str = "Operation",
        default_return: Any = None,
        log_traceback: bool = True,
        **kwargs
    ) -> Any:
        """
        Safely execute a function with error handling
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            context: Context description
            default_return: Value to return on error
            log_traceback: Whether to log full traceback
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result or default_return on error
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_exception(e, context, log_traceback=log_traceback)
            return default_return
    
    @staticmethod
    async def safe_execute_async(
        func: callable,
        *args,
        context: str = "Operation",
        default_return: Any = None,
        log_traceback: bool = True,
        **kwargs
    ) -> Any:
        """
        Safely execute an async function with error handling
        
        Args:
            func: Async function to execute
            *args: Positional arguments for function
            context: Context description
            default_return: Value to return on error
            log_traceback: Whether to log full traceback
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result or default_return on error
        """
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_exception(e, context, log_traceback=log_traceback)
            return default_return
    
    @staticmethod
    def create_error_response(
        message: str,
        status_code: int = 500,
        error_type: str = "ServerError",
        details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        Create a standard error response
        
        Args:
            message: Error message
            status_code: HTTP status code
            error_type: Type of error
            details: Optional additional details
            
        Returns:
            JSONResponse with error
        """
        content = {
            'error': message,
            'error_type': error_type,
            'status_code': status_code
        }
        
        if details:
            content['details'] = details
        
        return JSONResponse(
            status_code=status_code,
            content=content
        )


class SafeAPICall:
    """
    Context manager for safe API calls with automatic error handling
    """
    
    def __init__(
        self,
        context: str = "API Call",
        status_code: int = 500,
        log_traceback: bool = True
    ):
        self.context = context
        self.status_code = status_code
        self.log_traceback = log_traceback
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type: Type[Exception], exc_val: Exception, exc_tb):
        if exc_type is not None:
            ErrorHandler.handle_exception(
                exc_val,
                context=self.context,
                status_code=self.status_code,
                log_traceback=self.log_traceback,
                raise_http=True
            )
        return False  # Don't suppress the exception


# Convenience functions for common error scenarios

def handle_database_error(e: Exception, operation: str = "Database operation") -> Dict[str, Any]:
    """Handle database errors"""
    return ErrorHandler.handle_exception(e, context=operation, status_code=500)


def handle_validation_error(e: Exception, field: str = "input") -> Dict[str, Any]:
    """Handle validation errors"""
    return ErrorHandler.handle_exception(e, context=f"Validation of {field}", status_code=400)


def handle_not_found_error(resource: str = "Resource") -> Dict[str, Any]:
    """Handle not found errors"""
    return {
        'success': False,
        'error': f'{resource} not found',
        'error_type': 'NotFoundError',
        'status_code': 404
    }


def handle_auth_error(e: Exception) -> Dict[str, Any]:
    """Handle authentication errors"""
    return ErrorHandler.handle_exception(e, context="Authentication", status_code=401)