"""
Secure GitHub PAT Storage
Stores GitHub Personal Access Token encrypted in database
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from .encryption import encryption_manager
from ..models.api_key_models import UserApiKey

logger = logging.getLogger(__name__)

# Use a special system user ID for admin-level GitHub PAT
SYSTEM_USER_ID = "system_github_pat"
GITHUB_PAT_PROVIDER = "github_pat_system"


def store_github_pat(db: Session, pat_token: str) -> bool:
    """
    Store GitHub PAT encrypted in database
    
    Args:
        db: Database session
        pat_token: GitHub Personal Access Token
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Clean the token
        pat_token = pat_token.strip()
        
        # Encrypt the token
        encrypted_token = encryption_manager.encrypt(pat_token)
        
        # Check if already exists
        existing = db.query(UserApiKey).filter(
            UserApiKey.user_id == SYSTEM_USER_ID,
            UserApiKey.provider == GITHUB_PAT_PROVIDER
        ).first()
        
        if existing:
            # Update existing
            existing.encrypted_key = encrypted_token
            existing.is_active = True
        else:
            # Create new
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).isoformat()
            
            new_pat = UserApiKey(
                user_id=SYSTEM_USER_ID,
                provider=GITHUB_PAT_PROVIDER,
                encrypted_key=encrypted_token,
                is_active=True,
                created_at=now,
                updated_at=now
            )
            db.add(new_pat)
        
        db.commit()
        logger.info("✅ GitHub PAT stored securely in database")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to store GitHub PAT: {e}")
        db.rollback()
        return False


def get_github_pat(db: Session) -> Optional[str]:
    """
    Retrieve GitHub PAT from database (decrypted)
    
    Args:
        db: Database session
        
    Returns:
        Decrypted PAT token or None if not found
    """
    try:
        pat_record = db.query(UserApiKey).filter(
            UserApiKey.user_id == SYSTEM_USER_ID,
            UserApiKey.provider == GITHUB_PAT_PROVIDER,
            UserApiKey.is_active == True
        ).first()
        
        if not pat_record:
            logger.warning("⚠️ GitHub PAT not found in database")
            return None
        
        # Decrypt and return
        decrypted_token = encryption_manager.decrypt(pat_record.encrypted_key)
        return decrypted_token
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve GitHub PAT: {e}")
        return None


def delete_github_pat(db: Session) -> bool:
    """
    Delete GitHub PAT from database
    
    Args:
        db: Database session
        
    Returns:
        True if successful, False otherwise
    """
    try:
        pat_record = db.query(UserApiKey).filter(
            UserApiKey.user_id == SYSTEM_USER_ID,
            UserApiKey.provider == GITHUB_PAT_PROVIDER
        ).first()
        
        if pat_record:
            db.delete(pat_record)
            db.commit()
            logger.info("✅ GitHub PAT deleted from database")
            return True
        else:
            logger.warning("⚠️ GitHub PAT not found - nothing to delete")
            return False
        
    except Exception as e:
        logger.error(f"❌ Failed to delete GitHub PAT: {e}")
        db.rollback()
        return False


def is_github_pat_configured(db: Session) -> bool:
    """
    Check if GitHub PAT is configured in database
    
    Args:
        db: Database session
        
    Returns:
        True if PAT exists and is active, False otherwise
    """
    try:
        pat_record = db.query(UserApiKey).filter(
            UserApiKey.user_id == SYSTEM_USER_ID,
            UserApiKey.provider == GITHUB_PAT_PROVIDER,
            UserApiKey.is_active == True
        ).first()
        
        return pat_record is not None
        
    except Exception as e:
        logger.error(f"❌ Failed to check GitHub PAT status: {e}")
        return False
