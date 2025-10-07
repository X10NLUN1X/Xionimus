"""
CORS Configuration

Environment-aware CORS setup for development and production.
"""

import os
from typing import List
import logging

logger = logging.getLogger(__name__)


class CORSConfig:
    """
    CORS Configuration Manager
    
    Production Deployment Instructions:
    ====================================
    1. Set DEBUG=false in production environment
    2. Set CORS_ORIGINS environment variable with comma-separated allowed origins
       Example: CORS_ORIGINS=https://app.example.com,https://api.example.com
    3. Use HTTPS origins only (http:// will trigger warnings)
    4. Never use wildcard (*) in production
    5. Avoid localhost/127.0.0.1 in production
    
    Environment Variables:
    - DEBUG: Set to "false" for production mode
    - CORS_ORIGINS: Comma-separated list of allowed origins (production only)
    
    Security Features:
    - Automatic validation of production origins
    - Warnings for insecure patterns (wildcards, localhost, http://)
    - Strict origin checking in production
    - Permissive localhost variants in development
    """
    
    # Development origins (localhost variants)
    DEV_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1",
    ]
    
    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        """
        Get allowed CORS origins based on environment
        
        Returns:
            List of allowed origins
        """
        debug_mode = os.getenv("DEBUG", "false").lower() == "true"
        cors_origins_env = os.getenv("CORS_ORIGINS", "")
        
        if debug_mode:
            # Development mode - allow localhost variants
            origins = cls.DEV_ORIGINS.copy()
            
            # Also add any custom origins from env
            if cors_origins_env:
                custom_origins = [o.strip() for o in cors_origins_env.split(",")]
                origins.extend(custom_origins)
            
            logger.info(f"🔓 CORS: Development mode - {len(origins)} origins allowed")
            logger.debug(f"   Allowed origins: {', '.join(origins[:3])}... (+{len(origins)-3} more)")
            
            return origins
        else:
            # Production mode - strict origins from env only
            if not cors_origins_env:
                logger.warning(
                    "⚠️  CORS_ORIGINS not set in production! "
                    "Falling back to localhost (INSECURE)"
                )
                return ["http://localhost:3000"]  # Minimal fallback
            
            origins = [o.strip() for o in cors_origins_env.split(",")]
            
            # Validate production origins
            cls._validate_production_origins(origins)
            
            logger.info(f"🔒 CORS: Production mode - {len(origins)} origins allowed")
            logger.info(f"   Allowed origins: {', '.join(origins)}")
            
            return origins
    
    @classmethod
    def _validate_production_origins(cls, origins: List[str]) -> None:
        """
        Validate production CORS origins for security
        
        Args:
            origins: List of origins to validate
            
        Raises:
            Warning if insecure patterns detected
        """
        insecure_patterns = ["*", "localhost", "127.0.0.1"]
        
        for origin in origins:
            origin_lower = origin.lower()
            
            # Check for wildcard
            if "*" in origin_lower:
                logger.error(
                    f"❌ INSECURE: Wildcard in production CORS origin: {origin}"
                )
            
            # Check for localhost/127.0.0.1
            if any(pattern in origin_lower for pattern in ["localhost", "127.0.0.1"]):
                logger.warning(
                    f"⚠️  WARNING: Localhost in production CORS: {origin}"
                )
            
            # Check for http (not https) in production
            if origin_lower.startswith("http://") and not any(
                pattern in origin_lower for pattern in ["localhost", "127.0.0.1"]
            ):
                logger.warning(
                    f"⚠️  WARNING: Non-HTTPS origin in production: {origin}"
                )
    
    @classmethod
    def get_cors_config(cls) -> dict:
        """
        Get complete CORS middleware configuration
        
        Returns:
            Dict with CORS configuration
        """
        debug_mode = os.getenv("DEBUG", "false").lower() == "true"
        
        config = {
            "allow_origins": cls.get_allowed_origins(),
            "allow_credentials": True,
            "allow_methods": ["*"] if debug_mode else ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["*"] if debug_mode else [
                "Content-Type",
                "Authorization",
                "Accept",
                "Origin",
                "User-Agent",
                "DNT",
                "Cache-Control",
                "X-Requested-With",
            ],
            "expose_headers": ["*"] if debug_mode else [
                "Content-Length",
                "Content-Range",
                "X-Content-Type-Options",
            ],
            "max_age": 600,  # 10 minutes
        }
        
        return config
    
    @classmethod
    def print_config_summary(cls) -> None:
        """Print CORS configuration summary"""
        debug_mode = os.getenv("DEBUG", "false").lower() == "true"
        origins = cls.get_allowed_origins()
        
        print("\n" + "="*70)
        print("🌐 CORS CONFIGURATION")
        print("="*70)
        print(f"Mode: {'🔓 Development' if debug_mode else '🔒 Production'}")
        print(f"Allowed Origins: {len(origins)}")
        
        if debug_mode or len(origins) <= 5:
            for origin in origins:
                print(f"   • {origin}")
        else:
            for origin in origins[:3]:
                print(f"   • {origin}")
            print(f"   ... and {len(origins)-3} more")
        
        print("="*70 + "\n")


def get_cors_middleware_config() -> dict:
    """
    Convenience function to get CORS config
    
    Returns:
        CORS middleware configuration dict
    """
    return CORSConfig.get_cors_config()
