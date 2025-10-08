"""
Tests for CORS Configuration

Tests environment-aware CORS setup for dev and production.
"""

import pytest
import os
from app.core.cors_config import CORSConfig


class TestCORSConfig:
    """Test Suite für CORS Configuration"""
    
    def setup_method(self):
        """Setup vor jedem Test"""
        # Save original env vars
        self.original_debug = os.getenv("DEBUG")
        self.original_cors_origins = os.getenv("CORS_ORIGINS")
    
    def teardown_method(self):
        """Cleanup nach jedem Test"""
        # Restore original env vars
        if self.original_debug:
            os.environ["DEBUG"] = self.original_debug
        elif "DEBUG" in os.environ:
            del os.environ["DEBUG"]
        
        if self.original_cors_origins:
            os.environ["CORS_ORIGINS"] = self.original_cors_origins
        elif "CORS_ORIGINS" in os.environ:
            del os.environ["CORS_ORIGINS"]
    
    def test_development_mode_default_origins(self):
        """Test: Development mode includes default localhost origins"""
        os.environ["DEBUG"] = "true"
        os.environ["CORS_ORIGINS"] = ""
        
        origins = CORSConfig.get_allowed_origins()
        
        # Should include localhost variants
        assert "http://localhost:3000" in origins
        assert "http://127.0.0.1:3000" in origins
        assert "http://localhost:5173" in origins  # Vite
        assert len(origins) >= 10  # Multiple localhost variants
    
    def test_development_mode_custom_origins(self):
        """Test: Development mode allows custom origins on top of defaults"""
        os.environ["DEBUG"] = "true"
        os.environ["CORS_ORIGINS"] = "https://example.com,https://test.com"
        
        origins = CORSConfig.get_allowed_origins()
        
        # Should include both defaults and custom
        assert "http://localhost:3000" in origins
        assert "https://example.com" in origins
        assert "https://test.com" in origins
    
    def test_production_mode_requires_explicit_origins(self):
        """Test: Production mode requires explicit CORS_ORIGINS"""
        os.environ["DEBUG"] = "false"
        os.environ["CORS_ORIGINS"] = "https://yourdomain.com"
        
        origins = CORSConfig.get_allowed_origins()
        
        # Should only include specified origin
        assert origins == ["https://yourdomain.com"]
        
        # Should NOT include localhost
        assert "http://localhost:3000" not in origins
    
    def test_production_mode_multiple_origins(self):
        """Test: Production mode with multiple domains"""
        os.environ["DEBUG"] = "false"
        os.environ["CORS_ORIGINS"] = "https://app.com,https://www.app.com,https://api.app.com"
        
        origins = CORSConfig.get_allowed_origins()
        
        assert len(origins) == 3
        assert "https://app.com" in origins
        assert "https://www.app.com" in origins
        assert "https://api.app.com" in origins
    
    def test_production_mode_fallback_when_no_origins(self):
        """Test: Production mode falls back to minimal config when CORS_ORIGINS not set"""
        os.environ["DEBUG"] = "false"
        os.environ["CORS_ORIGINS"] = ""
        
        origins = CORSConfig.get_allowed_origins()
        
        # Should have a fallback
        assert len(origins) > 0
        # Fallback is minimal (localhost for emergency)
        assert origins == ["http://localhost:3000"]
    
    def test_get_cors_config_structure(self):
        """Test: get_cors_config returns proper structure"""
        os.environ["DEBUG"] = "true"
        
        config = CORSConfig.get_cors_config()
        
        assert "allow_origins" in config
        assert "allow_credentials" in config
        assert "allow_methods" in config
        assert "allow_headers" in config
        assert "expose_headers" in config
        assert "max_age" in config
        
        assert config["allow_credentials"] is True
        assert isinstance(config["allow_origins"], list)
        assert len(config["allow_origins"]) > 0
    
    def test_development_allows_all_methods(self):
        """Test: Development mode allows all HTTP methods"""
        os.environ["DEBUG"] = "true"
        
        config = CORSConfig.get_cors_config()
        
        assert config["allow_methods"] == ["*"]
        assert config["allow_headers"] == ["*"]
        assert config["expose_headers"] == ["*"]
    
    def test_production_restricts_methods(self):
        """Test: Production mode restricts HTTP methods"""
        os.environ["DEBUG"] = "false"
        os.environ["CORS_ORIGINS"] = "https://example.com"
        
        config = CORSConfig.get_cors_config()
        
        # Should be specific list, not wildcard
        assert config["allow_methods"] != ["*"]
        assert "GET" in config["allow_methods"]
        assert "POST" in config["allow_methods"]
        assert "DELETE" in config["allow_methods"]
        
        # Headers should be specific
        assert config["allow_headers"] != ["*"]
        assert "Content-Type" in config["allow_headers"]
        assert "Authorization" in config["allow_headers"]


class TestCORSValidation:
    """Tests für CORS Security Validation"""
    
    def test_validate_production_origins_wildcard(self, caplog):
        """Test: Warnung bei Wildcard in Production"""
        origins = ["https://example.com", "*"]
        
        CORSConfig._validate_production_origins(origins)
        
        # Should log error about wildcard
        assert "INSECURE" in caplog.text or "wildcard" in caplog.text.lower()
    
    def test_validate_production_origins_localhost(self, caplog):
        """Test: Warnung bei localhost in Production"""
        origins = ["https://example.com", "http://localhost:3000"]
        
        CORSConfig._validate_production_origins(origins)
        
        # Should log warning about localhost
        assert "localhost" in caplog.text.lower()
    
    def test_validate_production_origins_http(self, caplog):
        """Test: Warnung bei HTTP (nicht HTTPS) in Production"""
        origins = ["http://example.com"]
        
        CORSConfig._validate_production_origins(origins)
        
        # Should log warning about non-HTTPS
        assert "non-https" in caplog.text.lower() or "warning" in caplog.text.lower()
    
    def test_validate_production_origins_all_https(self, caplog):
        """Test: Keine Warnung bei sicheren HTTPS Origins"""
        origins = ["https://example.com", "https://www.example.com"]
        
        # Clear any previous logs
        caplog.clear()
        
        CORSConfig._validate_production_origins(origins)
        
        # Should not have critical errors (warnings about localhost are OK since we don't have them)
        error_logs = [record for record in caplog.records if record.levelname == "ERROR"]
        assert len(error_logs) == 0


class TestCORSIntegration:
    """Integration Tests für CORS"""
    
    def test_dev_to_prod_switch(self):
        """Test: Switching from dev to prod mode"""
        # Start in dev
        os.environ["DEBUG"] = "true"
        os.environ["CORS_ORIGINS"] = ""
        
        dev_origins = CORSConfig.get_allowed_origins()
        assert len(dev_origins) >= 10  # Many localhost variants
        
        # Switch to prod
        os.environ["DEBUG"] = "false"
        os.environ["CORS_ORIGINS"] = "https://prod.com"
        
        prod_origins = CORSConfig.get_allowed_origins()
        assert len(prod_origins) == 1
        assert prod_origins == ["https://prod.com"]
    
    def test_convenience_function(self):
        """Test: get_cors_middleware_config convenience function"""
        from app.core.cors_config import get_cors_middleware_config
        
        os.environ["DEBUG"] = "true"
        
        config = get_cors_middleware_config()
        
        # Should return complete config
        assert "allow_origins" in config
        assert isinstance(config, dict)


# Coverage Summary
def test_cors_coverage_summary():
    """Test: CORS Configuration Test Coverage Summary"""
    print("\n" + "="*70)
    print("✅ CORS CONFIGURATION TEST COVERAGE")
    print("="*70)
    print("✓ Development Mode (localhost variants)")
    print("✓ Production Mode (explicit origins)")
    print("✓ Environment switching")
    print("✓ Security validation (wildcard, localhost, http warnings)")
    print("✓ Configuration structure")
    print("✓ Method & Header restrictions")
    print("="*70)
