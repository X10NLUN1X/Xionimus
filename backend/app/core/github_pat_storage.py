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


# OAuth Credentials Storage
GITHUB_OAUTH_CLIENT_ID_PROVIDER = "github_oauth_client_id"
GITHUB_OAUTH_CLIENT_SECRET_PROVIDER = "github_oauth_client_secret"
GITHUB_OAUTH_CALLBACK_PROVIDER = "github_oauth_callback_url"


def store_github_oauth_credentials(
    db: Session, 
    client_id: str, 
    client_secret: str,
    callback_url: str = None
) -> bool:
    """
    Store GitHub OAuth credentials encrypted in database
    """
    try:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        
        # Store Client ID (not encrypted, not secret)
        existing_client_id = db.query(UserApiKey).filter(
            UserApiKey.user_id == SYSTEM_USER_ID,
            UserApiKey.provider == GITHUB_OAUTH_CLIENT_ID_PROVIDER
        ).first()
        
        if existing_client_id:
            existing_client_id.encrypted_key = client_id  # Not actually encrypted
            existing_client_id.is_active = True
            existing_client_id.updated_at = now
        else:
            new_client_id = UserApiKey(
                user_id=SYSTEM_USER_ID,
                provider=GITHUB_OAUTH_CLIENT_ID_PROVIDER,
                encrypted_key=client_id,
                is_active=True,
                created_at=now,
                updated_at=now
            )
            db.add(new_client_id)
        
        # Store Client Secret (encrypted)
        encrypted_secret = encryption_manager.encrypt(client_secret.strip())
        existing_secret = db.query(UserApiKey).filter(
            UserApiKey.user_id == SYSTEM_USER_ID,
            UserApiKey.provider == GITHUB_OAUTH_CLIENT_SECRET_PROVIDER
        ).first()
        
        if existing_secret:
            existing_secret.encrypted_key = encrypted_secret
            existing_secret.is_active = True
            existing_secret.updated_at = now
        else:
            new_secret = UserApiKey(
                user_id=SYSTEM_USER_ID,
                provider=GITHUB_OAUTH_CLIENT_SECRET_PROVIDER,
                encrypted_key=encrypted_secret,
                is_active=True,
                created_at=now,
                updated_at=now
            )
            db.add(new_secret)
        
        # Store Callback URL (not encrypted)
        if callback_url:
            existing_callback = db.query(UserApiKey).filter(
                UserApiKey.user_id == SYSTEM_USER_ID,
                UserApiKey.provider == GITHUB_OAUTH_CALLBACK_PROVIDER
            ).first()
            
            if existing_callback:
                existing_callback.encrypted_key = callback_url
                existing_callback.updated_at = now
            else:
                new_callback = UserApiKey(
                    user_id=SYSTEM_USER_ID,
                    provider=GITHUB_OAUTH_CALLBACK_PROVIDER,
                    encrypted_key=callback_url,
                    is_active=True,
                    created_at=now,
                    updated_at=now
                )
                db.add(new_callback)
        
        db.commit()
        logger.info("✅ GitHub OAuth credentials stored securely")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to store OAuth credentials: {e}")
        db.rollback()
        return False


def get_github_oauth_credentials(db: Session) -> dict:
    """
    Retrieve GitHub OAuth credentials from database
    """
    try:
        client_id_record = db.query(UserApiKey).filter(
            UserApiKey.user_id == SYSTEM_USER_ID,
            UserApiKey.provider == GITHUB_OAUTH_CLIENT_ID_PROVIDER,
            UserApiKey.is_active == True
        ).first()
        
        secret_record = db.query(UserApiKey).filter(
            UserApiKey.user_id == SYSTEM_USER_ID,
            UserApiKey.provider == GITHUB_OAUTH_CLIENT_SECRET_PROVIDER,
            UserApiKey.is_active == True
        ).first()
        
        callback_record = db.query(UserApiKey).filter(
            UserApiKey.user_id == SYSTEM_USER_ID,
            UserApiKey.provider == GITHUB_OAUTH_CALLBACK_PROVIDER
        ).first()
        
        if not client_id_record or not secret_record:
            return None
        
        return {
            "client_id": client_id_record.encrypted_key,
            "client_secret": encryption_manager.decrypt(secret_record.encrypted_key),
            "callback_url": callback_record.encrypted_key if callback_record else None
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve OAuth credentials: {e}")
        return None


def is_github_oauth_configured(db: Session) -> bool:
    """
    Check if GitHub OAuth is configured in database
    """
    try:
        client_id = db.query(UserApiKey).filter(
            UserApiKey.user_id == SYSTEM_USER_ID,
            UserApiKey.provider == GITHUB_OAUTH_CLIENT_ID_PROVIDER,
            UserApiKey.is_active == True
        ).first()
        
        secret = db.query(UserApiKey).filter(
            UserApiKey.user_id == SYSTEM_USER_ID,
            UserApiKey.provider == GITHUB_OAUTH_CLIENT_SECRET_PROVIDER,
            UserApiKey.is_active == True
        ).first()
        
        return client_id is not None and secret is not None
        
    except Exception as e:
        logger.error(f"❌ Failed to check OAuth status: {e}")
        return False
