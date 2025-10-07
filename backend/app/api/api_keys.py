"""
API Keys Management API
Secure storage and retrieval of user API keys
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timezone
import logging

from ..core.auth import get_current_user, User
from ..core.database import get_database
from sqlalchemy.orm import Session
from ..core.encryption import encryption_manager
from ..models.api_key_models import UserApiKey

logger = logging.getLogger(__name__)
router = APIRouter()


class SaveApiKeyRequest(BaseModel):
    provider: str = Field(..., pattern="^(anthropic|openai|perplexity|github)$")
    api_key: str = Field(..., min_length=10, max_length=500)


class ApiKeyResponse(BaseModel):
    provider: str
    masked_key: str
    is_active: bool
    last_used_at: Optional[str] = None
    last_test_status: Optional[str] = None
    last_test_at: Optional[str] = None
    created_at: str
    updated_at: str


class ApiKeysListResponse(BaseModel):
    api_keys: List[ApiKeyResponse]


class DeleteApiKeyResponse(BaseModel):
    success: bool
    message: str


class TestConnectionRequest(BaseModel):
    provider: str = Field(..., pattern="^(anthropic|openai|perplexity|github)$")


class TestConnectionResponse(BaseModel):
    success: bool
    provider: str
    message: str
    tested_at: str


@router.post("/save", response_model=ApiKeyResponse)
async def save_api_key(
    request: SaveApiKeyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Save or update user's API key (encrypted)
    """
    try:
        # Encrypt the API key
        encrypted_key = encryption_manager.encrypt(request.api_key)
        
        # Check if key already exists
        existing_key = db.query(UserApiKey).filter(
            UserApiKey.user_id == current_user.user_id,
            UserApiKey.provider == request.provider
        ).first()
        
        now = datetime.now(timezone.utc).isoformat()
        
        if existing_key:
            # Update existing key
            existing_key.encrypted_key = encrypted_key
            existing_key.updated_at = now
            existing_key.is_active = True
            existing_key.last_test_status = None  # Reset test status
            db.commit()
            db.refresh(existing_key)
            
            logger.info(f"✅ Updated API key for user {current_user.username}, provider {request.provider}")
            api_key_record = existing_key
        else:
            # Create new key
            new_key = UserApiKey(
                user_id=current_user.user_id,
                provider=request.provider,
                encrypted_key=encrypted_key,
                is_active=True,
                created_at=now,
                updated_at=now
            )
            db.add(new_key)
            db.commit()
            db.refresh(new_key)
            
            logger.info(f"✅ Saved new API key for user {current_user.username}, provider {request.provider}")
            api_key_record = new_key
        
        # Return masked key
        masked_key = encryption_manager.mask_key(request.api_key)
        
        return ApiKeyResponse(
            provider=api_key_record.provider,
            masked_key=masked_key,
            is_active=api_key_record.is_active,
            last_used_at=api_key_record.last_used_at,
            last_test_status=api_key_record.last_test_status,
            last_test_at=api_key_record.last_test_at,
            created_at=api_key_record.created_at,
            updated_at=api_key_record.updated_at
        )
        
    except Exception as e:
        logger.error(f"❌ Error saving API key: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=ApiKeysListResponse)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Get list of user's configured API keys (masked)
    Handles decryption errors gracefully by marking keys as requiring re-entry
    """
    try:
        
        # Get all keys for user
        keys = db.query(UserApiKey).filter(
            UserApiKey.user_id == current_user.user_id
        ).all()
        
        api_keys_list = []
        keys_to_delete = []
        
        for key in keys:
            try:
                # Try to decrypt to mask (don't return decrypted key!)
                decrypted_key = encryption_manager.decrypt(key.encrypted_key)
                masked_key = encryption_manager.mask_key(decrypted_key)
                
                api_keys_list.append(ApiKeyResponse(
                    provider=key.provider,
                    masked_key=masked_key,
                    is_active=key.is_active,
                    last_used_at=key.last_used_at,
                    last_test_status=key.last_test_status,
                    last_test_at=key.last_test_at,
                    created_at=key.created_at,
                    updated_at=key.updated_at
                ))
            except Exception as decrypt_error:
                # Decryption failed - encryption key has changed
                # Mark this key for deletion and show as requiring re-entry
                logger.warning(f"⚠️ Failed to decrypt {key.provider} key for user {current_user.username}: {decrypt_error}")
                keys_to_delete.append(key)
                
                # Show this key as corrupted but still visible
                api_keys_list.append(ApiKeyResponse(
                    provider=key.provider,
                    masked_key="[Key requires re-entry]",
                    is_active=False,
                    last_used_at=key.last_used_at,
                    last_test_status="error",
                    last_test_at=key.last_test_at,
                    created_at=key.created_at,
                    updated_at=key.updated_at
                ))
        
        # Delete corrupted keys
        for key in keys_to_delete:
            logger.info(f"🗑️ Deleting corrupted {key.provider} key for user {current_user.username}")
            db.delete(key)
        
        if keys_to_delete:
            db.commit()
            logger.warning(f"⚠️ Deleted {len(keys_to_delete)} corrupted API keys. User needs to re-enter them.")
        
        logger.info(f"📋 Retrieved {len(api_keys_list)} API keys for user {current_user.username}")
        
        return ApiKeysListResponse(api_keys=api_keys_list)
        
    except Exception as e:
        logger.error(f"❌ Error listing API keys: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{provider}", response_model=DeleteApiKeyResponse)
async def delete_api_key(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Delete user's API key for specified provider
    """
    try:
        
        # Find and delete key
        key = db.query(UserApiKey).filter(
            UserApiKey.user_id == current_user.user_id,
            UserApiKey.provider == provider
        ).first()
        
        if not key:
            raise HTTPException(status_code=404, detail=f"API key not found for provider {provider}")
        
        db.delete(key)
        db.commit()
        
        logger.info(f"🗑️ Deleted API key for user {current_user.username}, provider {provider}")
        
        return DeleteApiKeyResponse(
            success=True,
            message=f"API key for {provider} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting API key: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-connection", response_model=TestConnectionResponse)
async def test_connection(
    request: TestConnectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Test connection to API provider (validates API key)
    Uses async httpx client with timeouts to prevent blocking
    """
    try:
        
        # Get user's API key
        key_record = db.query(UserApiKey).filter(
            UserApiKey.user_id == current_user.user_id,
            UserApiKey.provider == request.provider
        ).first()
        
        if not key_record:
            raise HTTPException(status_code=404, detail=f"No API key configured for {request.provider}")
        
        # Decrypt API key
        api_key = encryption_manager.decrypt(key_record.encrypted_key)
        
        # Test connection based on provider using async httpx
        success = False
        message = ""
        
        import httpx
        
        if request.provider == "anthropic":
            # Test Anthropic API with async httpx (fast timeout)
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": api_key,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json"
                        },
                        json={
                            "model": "claude-3-5-haiku-20241022",
                            "max_tokens": 1,
                            "messages": [{"role": "user", "content": "hi"}]
                        }
                    )
                    success = response.status_code == 200
                    message = "✅ Connection successful" if success else f"❌ Connection failed: HTTP {response.status_code}"
            except httpx.TimeoutException:
                message = "❌ Connection failed: Timeout (>5s)"
            except Exception as e:
                message = f"❌ Connection failed: {str(e)[:100]}"
        
        elif request.provider == "openai":
            # Test OpenAI API with async httpx (fast timeout)
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "gpt-3.5-turbo",
                            "messages": [{"role": "user", "content": "hi"}],
                            "max_tokens": 1
                        }
                    )
                    success = response.status_code == 200
                    message = "✅ Connection successful" if success else f"❌ Connection failed: HTTP {response.status_code}"
            except httpx.TimeoutException:
                message = "❌ Connection failed: Timeout (>5s)"
            except Exception as e:
                message = f"❌ Connection failed: {str(e)[:100]}"
        
        elif request.provider == "perplexity":
            # Test Perplexity API - try minimal request first
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    # Use the correct model name format for Perplexity API
                    response = await client.post(
                        "https://api.perplexity.ai/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-sonar-small-128k-online",
                            "messages": [{"role": "user", "content": "hi"}],
                            "max_tokens": 1
                        }
                    )
                    
                    # Log full response for debugging
                    logger.info(f"Perplexity test: status={response.status_code}")
                    if response.status_code != 200:
                        logger.error(f"Perplexity error response: {response.text}")
                    
                    # Check status
                    if response.status_code == 200:
                        success = True
                        message = "✅ Connection successful"
                    elif response.status_code == 401:
                        success = False
                        message = "❌ Invalid API key"
                    elif response.status_code == 403:
                        success = False
                        message = "❌ Access forbidden - check API key permissions"
                    elif response.status_code == 429:
                        success = False
                        message = "❌ Rate limit exceeded"
                    else:
                        success = False
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                            message = f"❌ API error: {error_msg[:100]}"
                        except:
                            message = f"❌ Connection failed: HTTP {response.status_code}"
                            
            except httpx.TimeoutException:
                message = "❌ Connection failed: Timeout (>5s)"
                logger.error("Perplexity API test timeout")
            except httpx.ConnectError as e:
                message = "❌ Connection failed: Cannot reach Perplexity API"
                logger.error(f"Perplexity connection error: {e}")
            except Exception as e:
                message = f"❌ Connection failed: {str(e)[:100]}"
                logger.error(f"Perplexity API test error: {type(e).__name__}: {e}")
        
        elif request.provider == "github":
            # Test GitHub API with async httpx (fast timeout)
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(
                        "https://api.github.com/user",
                        headers={
                            "Authorization": f"token {api_key}",
                            "Accept": "application/vnd.github.v3+json"
                        }
                    )
                    success = response.status_code == 200
                    message = "✅ Connection successful" if success else f"❌ Connection failed: HTTP {response.status_code}"
            except httpx.TimeoutException:
                message = "❌ Connection failed: Timeout (>5s)"
            except Exception as e:
                message = f"❌ Connection failed: {str(e)[:100]}"
        
        # Update test status
        now = datetime.now(timezone.utc).isoformat()
        key_record.last_test_status = "success" if success else "failed"
        key_record.last_test_at = now
        db.commit()
        
        logger.info(f"🧪 API key test for {request.provider}: {'success' if success else 'failed'}")
        
        return TestConnectionResponse(
            success=success,
            provider=request.provider,
            message=message,
            tested_at=now
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error testing connection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_keys_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Get quick status of which providers are configured
    """
    try:
        
        keys = db.query(UserApiKey).filter(
            UserApiKey.user_id == current_user.user_id,
            UserApiKey.is_active == True
        ).all()
        
        status = {
            "anthropic": False,
            "openai": False,
            "perplexity": False,
            "github": False
        }
        
        for key in keys:
            status[key.provider] = True
        
        return {
            "configured_providers": status,
            "total_configured": sum(status.values())
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))