from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import jwt
import uuid
import bcrypt
import logging

from ..core.database import get_database
from ..core.config import settings
from ..models.user_models import User

logger = logging.getLogger(__name__)
router = APIRouter()

# Password hashing
import bcrypt

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt directly"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash using bcrypt directly"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str

class User(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: Optional[str]
    created_at: datetime
    is_active: bool = True

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=Token)
async def register_user(
    user_data: UserCreate,
    db = Depends(get_database)
):
    """Register a new user"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Check if user exists using SQLAlchemy
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_data.password)
        timestamp = datetime.now(timezone.utc).isoformat()
        
        new_user = User(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            created_at=timestamp,
            is_active=True,
            role="user"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user_id, "username": user_data.username}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            username=user_data.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Register error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    db = Depends(get_database)
):
    """Login user"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Find user using SQLAlchemy
        user = db.query(User).filter(User.username == login_data.username).first()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last login
        user.last_login = datetime.now(timezone.utc).isoformat()
        db.commit()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.id, "username": user.username}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            username=user.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
        raise HTTPException(status_code=500, detail="Login failed")

@router.get("/me", response_model=User)
async def get_current_user(
    db = Depends(get_database),
    # TODO: Add JWT token dependency here
):
    """Get current user info"""
    # For MVP, return demo user
    return User(
        user_id="demo-user",
        username="demo",
        email="demo@xionimus-ai.com",
        full_name="Demo User",
        created_at=datetime.now(timezone.utc),
        is_active=True
    )