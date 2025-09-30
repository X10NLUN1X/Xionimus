# ⚠️ DEPRECATED - Not currently used
"""
Authentication and Authorization Middleware
Provides secure JWT-based authentication for all protected endpoints
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from datetime import datetime, timezone
import logging

from .config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

class AuthenticationError(HTTPException):
    """Raised when authentication fails"""
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationError(HTTPException):
    """Raised when user lacks permissions"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

def create_access_token(user_id: str, username: str) -> str:
    """Create JWT access token for authenticated user"""
    from datetime import timedelta
    
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": exp.timestamp(),
        "iat": datetime.now(timezone.utc).timestamp(),
        "type": "access"
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Validate token type
        if payload.get("type") != "access":
            raise AuthenticationError("Invalid token type")
        
        # Check expiration
        exp = payload.get("exp")
        if not exp or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise AuthenticationError("Token expired")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise AuthenticationError("Invalid token")

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Dependency to get current authenticated user from JWT token
    
    Returns:
        user_id: ID of authenticated user
    
    Raises:
        AuthenticationError: If token is missing or invalid
    """
    if not credentials:
        raise AuthenticationError("Missing authentication token")
    
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise AuthenticationError("Invalid token payload")
        
        return user_id
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise AuthenticationError("Authentication failed")

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Optional authentication - returns user_id if authenticated, None otherwise
    Useful for endpoints that work with or without authentication
    """
    if not credentials:
        return None
    
    try:
        payload = decode_token(credentials.credentials)
        return payload.get("user_id")
    except:
        return None

def require_permissions(*permissions: str):
    """
    Decorator to require specific permissions for an endpoint
    (Future enhancement for role-based access control)
    """
    async def dependency(user_id: str = Depends(get_current_user)):
        # TODO: Implement permission checking
        # For now, just ensure user is authenticated
        return user_id
    return Depends(dependency)
