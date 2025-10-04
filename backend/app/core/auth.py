"""
Authentication and Authorization Core Module
Provides JWT token validation and user dependency injection
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import logging
from datetime import datetime, timezone

from .config import settings
from .database import get_database
from ..models.user_models import User as UserModel

logger = logging.getLogger(__name__)
security = HTTPBearer()

class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class User:
    """Current user data structure"""
    def __init__(self, user_id: str, username: str, email: str, role: str = "user"):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.is_admin = role == "admin"

async def verify_token(token: str) -> dict:
    """Verify JWT token and extract payload"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Token missing user ID")
        
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
            raise AuthenticationError("Token expired")
            
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise AuthenticationError("Invalid token")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_database)
) -> User:
    """
    Dependency to get current authenticated user
    Usage: user = Depends(get_current_user)
    """
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Authentication token required")
    
    # Verify token
    payload = await verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    # Fetch user from database
    try:
        user_record = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user_record:
            logger.warning(f"Token valid but user {user_id} not found in database (deleted or test user)")
            raise AuthenticationError("User not found")
            
        if not user_record.is_active:
            logger.warning(f"User {user_id} is inactive")
            raise AuthenticationError("User inactive")
            
        return User(
            user_id=user_record.id,
            username=user_record.username,
            email=user_record.email,
            role=user_record.role or "user"
        )
        
    except AuthenticationError:
        raise  # Re-raise authentication errors
    except Exception as e:
        logger.error(f"Database error fetching user {user_id}: {e}")
        raise AuthenticationError("User validation failed")


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_database)
) -> Optional[User]:
    """
    Dependency to get current user (optional - returns None if not authenticated)
    Usage: user = Depends(get_current_user_optional)
    """
    try:
        if not credentials or not credentials.credentials:
            return None
        
        # Verify token
        payload = await verify_token(credentials.credentials)
        user_id = payload.get("sub")
        username = payload.get("username")
        
        # Fetch user from database
        user_record = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user_record or not user_record.is_active:
            return None
            
        return User(
            user_id=user_record.id,
            username=user_record.username,
            email=user_record.email,
            role=user_record.role or "user"
        )
    except Exception:
        # Silently return None for any auth errors
        return None

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency for admin-only endpoints
    Usage: admin = Depends(get_current_admin_user)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Optional authentication - returns None if no token provided
    Usage: user = Depends(get_optional_user)
    """
    if not credentials or not credentials.credentials:
        return None
        
    try:
        payload = await verify_token(credentials.credentials)
        user_id = payload.get("sub")
        username = payload.get("username")
        
        # For optional auth, we can return basic info without DB lookup
        return User(user_id=user_id, username=username, email="", role="user")
    except AuthenticationError:
        # Invalid token but optional auth - return None
        return None

# API Key Authentication (for service-to-service)
async def verify_api_key(api_key: str) -> bool:
    """Verify API key for service-to-service communication"""
    valid_keys = [
        settings.SECRET_KEY,  # Master key
        "dev-api-key",        # Development key
        # Add more service keys as needed
    ]
    return api_key in valid_keys

class APIKeyAuth:
    def __init__(self, required: bool = True):
        self.required = required
    
    async def __call__(self, request) -> Optional[str]:
        api_key = request.headers.get("X-API-Key")
        
        if not api_key and self.required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )
        
        if api_key and not await verify_api_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key"
            )
        
        return api_key