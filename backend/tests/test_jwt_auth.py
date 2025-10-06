"""
Tests for JWT Authentication

Tests für JWT Token Generation, Validation und Auth Flow
"""

import pytest
from datetime import datetime, timedelta
import jwt
import os
from app.core.auth import create_access_token, decode_access_token, get_password_hash, verify_password
from app.core.config import settings


class TestJWTAuthentication:
    """Test Suite für JWT Authentication"""
    
    def test_create_access_token(self):
        """Test: JWT Token wird korrekt erstellt"""
        user_id = "test_user_123"
        token = create_access_token(data={"sub": user_id})
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Test: Gültiger Token wird korrekt dekodiert"""
        user_id = "test_user_456"
        token = create_access_token(data={"sub": user_id})
        
        # Dekodiere Token
        payload = decode_access_token(token)
        
        assert payload is not None
        assert payload.get("sub") == user_id
    
    def test_decode_expired_token(self):
        """Test: Abgelaufener Token wird erkannt"""
        user_id = "test_user_789"
        
        # Erstelle Token mit sehr kurzer Expiry (bereits abgelaufen)
        token_data = {
            "sub": user_id,
            "exp": datetime.utcnow() - timedelta(hours=1)  # 1 Stunde in Vergangenheit
        }
        
        token = jwt.encode(
            token_data,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Dekodierung sollte fehlschlagen
        with pytest.raises((jwt.ExpiredSignatureError, Exception)):
            decode_access_token(token)
    
    def test_decode_invalid_signature(self):
        """Test: Token mit falscher Signatur wird abgelehnt"""
        user_id = "test_user_999"
        
        # Token mit falschem Secret erstellen
        wrong_secret = "wrong_secret_key_12345"
        token_data = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        token = jwt.encode(
            token_data,
            wrong_secret,
            algorithm="HS256"
        )
        
        # Dekodierung sollte fehlschlagen
        with pytest.raises((jwt.InvalidSignatureError, Exception)):
            decode_access_token(token)
    
    def test_decode_malformed_token(self):
        """Test: Malformed Token wird abgelehnt"""
        malformed_tokens = [
            "not.a.token",
            "incomplete",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
        ]
        
        for token in malformed_tokens:
            with pytest.raises((jwt.DecodeError, jwt.InvalidTokenError, Exception)):
                decode_access_token(token)
    
    def test_token_contains_expiry(self):
        """Test: Token enthält Expiry Timestamp"""
        user_id = "test_user_exp"
        token = create_access_token(data={"sub": user_id})
        
        # Dekodiere ohne Verify für Inspektion
        payload = jwt.decode(token, options={"verify_signature": False})
        
        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))
    
    def test_token_algorithm(self):
        """Test: Korrekter Algorithm wird verwendet"""
        user_id = "test_user_alg"
        token = create_access_token(data={"sub": user_id})
        
        # Dekodiere Header
        header = jwt.get_unverified_header(token)
        
        assert header["alg"] == settings.JWT_ALGORITHM
        assert header["typ"] == "JWT"
    
    def test_token_with_additional_claims(self):
        """Test: Token mit zusätzlichen Claims"""
        user_id = "test_user_claims"
        additional_data = {
            "sub": user_id,
            "role": "admin",
            "permissions": ["read", "write"]
        }
        
        token = create_access_token(data=additional_data)
        payload = decode_access_token(token)
        
        assert payload.get("sub") == user_id
        assert payload.get("role") == "admin"
        assert "permissions" in payload


class TestPasswordHashing:
    """Tests für Password Hashing (bcrypt)"""
    
    def test_hash_password(self):
        """Test: Password wird korrekt gehasht"""
        password = "secure_password_123!"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password  # Sollte nicht Plain sein
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_verify_correct_password(self):
        """Test: Korrektes Password wird verifiziert"""
        password = "my_secure_password"
        hashed = get_password_hash(password)
        
        # Verifikation sollte True zurückgeben
        assert verify_password(password, hashed) is True
    
    def test_verify_incorrect_password(self):
        """Test: Falsches Password wird abgelehnt"""
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        
        hashed = get_password_hash(correct_password)
        
        # Verifikation sollte False zurückgeben
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_different_passwords_produce_different_hashes(self):
        """Test: Verschiedene Passwords ergeben verschiedene Hashes"""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2
    
    def test_same_password_produces_different_hashes(self):
        """Test: Gleicher Password mehrfach gehasht ergibt unterschiedliche Hashes (Salt)"""
        password = "same_password"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Durch Salt sollten Hashes unterschiedlich sein
        assert hash1 != hash2
        
        # Aber beide sollten verifizierbar sein
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_hash_empty_password(self):
        """Test: Leerer Password wird behandelt"""
        password = ""
        
        # Sollte auch leeren Password hashen (aber nicht empfohlen)
        hashed = get_password_hash(password)
        assert hashed is not None
        assert verify_password(password, hashed) is True
    
    def test_hash_special_characters(self):
        """Test: Password mit Sonderzeichen"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_hash_unicode_password(self):
        """Test: Password mit Unicode-Zeichen"""
        password = "pässwörd_中文_🔐"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True


class TestAuthenticationFlow:
    """Integration Tests für kompletten Auth-Flow"""
    
    def test_complete_registration_flow(self):
        """Test: Kompletter Registrierungs-Flow (Hash + Token)"""
        username = "new_user"
        password = "secure_password_123"
        
        # 1. Password hashen (bei Registration)
        hashed_password = get_password_hash(password)
        
        # 2. User würde in DB gespeichert mit hashed_password
        # (Simuliert durch Assertions)
        assert hashed_password is not None
        
        # 3. Token erstellen (bei erfolgreichem Login)
        token = create_access_token(data={"sub": username})
        
        assert token is not None
        
        # 4. Token dekodieren (bei geschützter Route)
        payload = decode_access_token(token)
        
        assert payload.get("sub") == username
    
    def test_complete_login_flow(self):
        """Test: Kompletter Login-Flow"""
        username = "existing_user"
        password = "user_password"
        
        # 1. User existiert bereits mit gehashtem Password
        stored_hash = get_password_hash(password)
        
        # 2. User versucht Login mit Plain Password
        login_password = "user_password"
        
        # 3. Password Verifikation
        is_valid = verify_password(login_password, stored_hash)
        assert is_valid is True
        
        # 4. Token generieren bei erfolgreicher Verifikation
        if is_valid:
            token = create_access_token(data={"sub": username})
            assert token is not None
    
    def test_failed_login_wrong_password(self):
        """Test: Fehlerhafter Login mit falschem Password"""
        username = "user"
        correct_password = "correct"
        wrong_password = "wrong"
        
        # Stored hash
        stored_hash = get_password_hash(correct_password)
        
        # Login Versuch mit falschem Password
        is_valid = verify_password(wrong_password, stored_hash)
        assert is_valid is False
        
        # Kein Token sollte erstellt werden
        # (In echter Implementierung würde Exception geworfen)
    
    def test_token_refresh_scenario(self):
        """Test: Token Refresh Szenario"""
        username = "refresh_user"
        
        # Ursprünglicher Token
        original_token = create_access_token(data={"sub": username})
        
        # Token dekodieren
        payload = decode_access_token(original_token)
        
        # Neuen Token generieren (Refresh)
        new_token = create_access_token(data={"sub": payload.get("sub")})
        
        assert new_token is not None
        assert new_token != original_token  # Sollte unterschiedlich sein
    
    def test_protected_endpoint_simulation(self):
        """Test: Simulation einer geschützten Route"""
        user_id = "protected_user"
        
        # User hat Token
        token = create_access_token(data={"sub": user_id})
        
        # Endpoint erhält Token und validiert
        try:
            payload = decode_access_token(token)
            authenticated_user = payload.get("sub")
            
            # Access granted
            assert authenticated_user == user_id
            access_granted = True
        except Exception:
            access_granted = False
        
        assert access_granted is True


class TestAuthConfiguration:
    """Tests für Auth Configuration"""
    
    def test_secret_key_exists(self):
        """Test: SECRET_KEY ist konfiguriert"""
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 0
    
    def test_jwt_algorithm_configured(self):
        """Test: JWT Algorithm ist konfiguriert"""
        assert settings.JWT_ALGORITHM is not None
        assert settings.JWT_ALGORITHM in ["HS256", "HS384", "HS512"]
    
    def test_jwt_expire_minutes_configured(self):
        """Test: JWT Expiry ist konfiguriert"""
        assert settings.JWT_EXPIRE_MINUTES is not None
        assert settings.JWT_EXPIRE_MINUTES > 0


# Test Coverage Summary
def test_auth_coverage_summary():
    """Test: Auth Test Coverage Summary"""
    print("\n" + "="*70)
    print("✅ JWT AUTHENTICATION TEST COVERAGE")
    print("="*70)
    print("✓ Token Creation & Validation")
    print("✓ Password Hashing (bcrypt)")
    print("✓ Token Expiry Handling")
    print("✓ Invalid Token Detection")
    print("✓ Complete Auth Flow (Register + Login)")
    print("✓ Configuration Validation")
    print("="*70)
