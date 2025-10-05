"""
Unit tests for security utilities
Tests API key masking and sensitive data handling
"""
import pytest
from app.core.security_utils import mask_api_key, mask_sensitive_data, sanitize_log_message


class TestMaskApiKey:
    """Test API key masking functionality"""
    
    def test_mask_openai_key(self):
        """Test masking OpenAI API key"""
        key = "sk-proj-abc123def456ghi789"
        masked = mask_api_key(key)
        assert masked == "********...i789"
        assert "abc123" not in masked
    
    def test_mask_anthropic_key(self):
        """Test masking Anthropic API key"""
        key = "sk-ant-api03-xyz789abc123"
        masked = mask_api_key(key)
        assert masked == "********...c123"
        assert "xyz789" not in masked
    
    def test_mask_short_key(self):
        """Test masking short keys"""
        key = "short"
        masked = mask_api_key(key)
        assert masked == "****"
    
    def test_mask_empty_key(self):
        """Test masking empty key"""
        key = ""
        masked = mask_api_key(key)
        assert masked == "****"
    
    def test_mask_none_key(self):
        """Test masking None key"""
        masked = mask_api_key(None)
        assert masked == "****"


class TestMaskSensitiveData:
    """Test sensitive data masking in dictionaries"""
    
    def test_mask_api_key_field(self):
        """Test masking api_key field"""
        data = {"api_key": "sk-proj-secret123"}
        masked = mask_sensitive_data(data)
        assert "sk-proj-secret123" not in str(masked)
        assert masked["api_key"] == "********...t123"
    
    def test_mask_password_field(self):
        """Test masking password field"""
        data = {"password": "supersecret"}
        masked = mask_sensitive_data(data)
        assert masked["password"] == "********...cret"
    
    def test_mask_token_field(self):
        """Test masking token field"""
        data = {"auth_token": "bearer_token_123"}
        masked = mask_sensitive_data(data)
        assert "bearer_token" not in str(masked)
    
    def test_preserve_non_sensitive_fields(self):
        """Test non-sensitive fields are preserved"""
        data = {"username": "john", "email": "john@example.com"}
        masked = mask_sensitive_data(data)
        assert masked["username"] == "john"
        assert masked["email"] == "john@example.com"
    
    def test_nested_dictionary(self):
        """Test masking in nested dictionaries"""
        data = {
            "user": {
                "name": "john",
                "api_key": "sk-secret123"
            }
        }
        masked = mask_sensitive_data(data)
        assert masked["user"]["name"] == "john"
        assert "sk-secret123" not in str(masked)
    
    def test_list_of_dicts(self):
        """Test masking in list of dictionaries"""
        data = {
            "keys": [
                {"api_key": "key1"},
                {"api_key": "key2"}
            ]
        }
        masked = mask_sensitive_data(data)
        assert "key1" not in str(masked)
        assert "key2" not in str(masked)


class TestSanitizeLogMessage:
    """Test log message sanitization"""
    
    def test_sanitize_openai_key(self):
        """Test sanitizing OpenAI key from log message"""
        message = "Configuring with key: sk-proj-abc123def456"
        sanitized = sanitize_log_message(message)
        assert "sk-proj-abc123def456" not in sanitized
        assert "[REDACTED]" in sanitized
    
    def test_sanitize_anthropic_key(self):
        """Test sanitizing Anthropic key from log message"""
        message = "Using key sk-ant-api03-xyz789"
        sanitized = sanitize_log_message(message)
        assert "sk-ant-api03-xyz789" not in sanitized
        assert "[REDACTED]" in sanitized
    
    def test_sanitize_perplexity_key(self):
        """Test sanitizing Perplexity key from log message"""
        message = "Token: pplx-abcd1234"
        sanitized = sanitize_log_message(message)
        assert "pplx-abcd1234" not in sanitized
        assert "[REDACTED]" in sanitized
    
    def test_preserve_non_sensitive_content(self):
        """Test non-sensitive content is preserved"""
        message = "User logged in successfully"
        sanitized = sanitize_log_message(message)
        assert sanitized == message
    
    def test_multiple_keys_in_message(self):
        """Test sanitizing multiple keys in one message"""
        message = "Keys: sk-proj-abc123 and pplx-xyz789"
        sanitized = sanitize_log_message(message)
        assert "sk-proj-abc123" not in sanitized
        assert "pplx-xyz789" not in sanitized
        assert "[REDACTED]" in sanitized


if __name__ == "__main__":
    pytest.main([__file__, "-v"])