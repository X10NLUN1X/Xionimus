"""
Encryption utilities for secure API key storage
Uses Fernet symmetric encryption
"""
from cryptography.fernet import Fernet
import os
import base64
from typing import Optional
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# CRITICAL: Load .env before anything else to ensure ENCRYPTION_KEY is available
def _load_env_if_needed():
    """Ensure .env is loaded with absolute path"""
    if not os.getenv("ENCRYPTION_KEY"):
        # Calculate backend directory from this file's location
        # encryption.py is in: /app/backend/app/core/encryption.py
        current_file = Path(__file__).resolve()
        backend_dir = current_file.parent.parent.parent  # Go up 3 levels
        env_file = backend_dir / ".env"
        
        if env_file.exists():
            load_dotenv(dotenv_path=env_file, override=True)
            logger.debug(f"Loaded .env from: {env_file}")

# Load .env immediately when module is imported
_load_env_if_needed()

class EncryptionManager:
    """Manages encryption/decryption of sensitive data"""
    
    def __init__(self):
        # Get encryption key from environment or generate one
        self.encryption_key = self._get_or_generate_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_generate_key(self) -> bytes:
        """Get encryption key from environment or generate new one"""
        key = os.getenv("ENCRYPTION_KEY")
        
        if key:
            # Validate and use existing key
            try:
                key_bytes = key.encode() if isinstance(key, str) else key
                # Test if it's a valid Fernet key
                Fernet(key_bytes)
                logger.info("✅ Using encryption key from environment")
                return key_bytes
            except Exception as e:
                logger.warning(f"⚠️ Invalid ENCRYPTION_KEY in environment: {e}")
        
        # Generate new key
        new_key = Fernet.generate_key()
        logger.warning("⚠️ Generated new encryption key. Set ENCRYPTION_KEY in .env for persistence!")
        logger.info(f"   ENCRYPTION_KEY={new_key.decode()}")
        return new_key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return ""
        
        try:
            encrypted_bytes = self.fernet.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt encrypted string
        
        Args:
            encrypted_text: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
        """
        if not encrypted_text:
            return ""
        
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    def mask_key(self, api_key: str, visible_chars: int = 4) -> str:
        """
        Mask API key for display (show only last N characters)
        
        Args:
            api_key: Full API key
            visible_chars: Number of characters to show at end
            
        Returns:
            Masked key like "sk-...xyz123"
        """
        if not api_key:
            return ""
        
        if len(api_key) <= visible_chars:
            return "*" * len(api_key)
        
        prefix = api_key[:3] if len(api_key) > 10 else ""
        suffix = api_key[-visible_chars:]
        
        if prefix:
            return f"{prefix}...{suffix}"
        else:
            return f"...{suffix}"


# Global instance
encryption_manager = EncryptionManager()