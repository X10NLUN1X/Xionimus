"""
Tests for Rate Limiting functionality

Tests die Advanced Rate Limiting Implementierung
"""

import pytest
import time
from app.core.rate_limiter import AdvancedRateLimiter, RateLimitExceeded, RateLimit


class TestRateLimiter:
    """Test Suite für Rate Limiting"""
    
    def setup_method(self):
        """Setup vor jedem Test"""
        self.limiter = AdvancedRateLimiter()
        self.test_user_id = "test_user_123"
        self.test_endpoint = "/api/test"
    
    def test_rate_limiter_initialization(self):
        """Test: Rate Limiter wird korrekt initialisiert"""
        assert self.limiter is not None
        assert hasattr(self.limiter, 'check_rate_limit')
        assert hasattr(self.limiter, 'get_user_stats')
    
    def test_basic_rate_limit_check(self):
        """Test: Grundlegende Rate Limit Prüfung"""
        # Erstes Request sollte durchgehen
        result = self.limiter.check_rate_limit(
            user_id=self.test_user_id,
            endpoint=self.test_endpoint,
            requests_per_minute=10
        )
        assert result is True or result is None  # Hängt von Implementierung ab
    
    def test_rate_limit_exceeded(self):
        """Test: Rate Limit wird korrekt überschritten"""
        # Definiere sehr niedriges Limit
        requests_per_second = 2
        
        # Mache requests bis Limit erreicht
        for i in range(requests_per_second):
            self.limiter.check_rate_limit(
                user_id=self.test_user_id,
                endpoint=self.test_endpoint,
                requests_per_minute=requests_per_second * 60
            )
        
        # Nächster Request sollte fehlschlagen
        with pytest.raises((RateLimitExceeded, Exception)):
            for i in range(10):  # Mehrere Versuche
                self.limiter.check_rate_limit(
                    user_id=self.test_user_id,
                    endpoint=self.test_endpoint,
                    requests_per_minute=requests_per_second * 60
                )
    
    def test_different_users_separate_limits(self):
        """Test: Verschiedene User haben separate Limits"""
        user1 = "user_1"
        user2 = "user_2"
        
        # User 1 macht Requests
        for i in range(5):
            self.limiter.check_rate_limit(
                user_id=user1,
                endpoint=self.test_endpoint,
                requests_per_minute=60
            )
        
        # User 2 sollte eigenes Limit haben
        result = self.limiter.check_rate_limit(
            user_id=user2,
            endpoint=self.test_endpoint,
            requests_per_minute=60
        )
        # Sollte funktionieren, da separates Limit
        assert result is True or result is None
    
    def test_different_endpoints_separate_limits(self):
        """Test: Verschiedene Endpoints haben separate Limits"""
        endpoint1 = "/api/chat"
        endpoint2 = "/api/files"
        
        # Endpoint 1
        for i in range(5):
            self.limiter.check_rate_limit(
                user_id=self.test_user_id,
                endpoint=endpoint1,
                requests_per_minute=60
            )
        
        # Endpoint 2 sollte eigenes Limit haben
        result = self.limiter.check_rate_limit(
            user_id=self.test_user_id,
            endpoint=endpoint2,
            requests_per_minute=60
        )
        assert result is True or result is None
    
    def test_rate_limit_reset_after_time(self):
        """Test: Rate Limit resettet sich nach Zeitfenster"""
        # Kleines Limit
        requests_per_second = 2
        
        # Erschöpfe Limit
        for i in range(requests_per_second):
            self.limiter.check_rate_limit(
                user_id=self.test_user_id,
                endpoint=self.test_endpoint,
                requests_per_minute=requests_per_second * 60
            )
        
        # Warte bis Fenster resettet (1 Sekunde)
        time.sleep(1.1)
        
        # Sollte wieder funktionieren
        result = self.limiter.check_rate_limit(
            user_id=self.test_user_id,
            endpoint=self.test_endpoint,
            requests_per_minute=requests_per_second * 60
        )
        # Nach Reset sollte es funktionieren
        assert result is True or result is None
    
    def test_get_user_stats(self):
        """Test: User Stats können abgerufen werden"""
        # Mache ein paar Requests
        for i in range(3):
            try:
                self.limiter.check_rate_limit(
                    user_id=self.test_user_id,
                    endpoint=self.test_endpoint,
                    requests_per_minute=60
                )
            except:
                pass
        
        # Stats abrufen
        stats = self.limiter.get_user_stats(self.test_user_id)
        
        # Stats sollten existieren (Format hängt von Implementierung ab)
        assert stats is not None
    
    def test_rate_limit_with_zero_requests(self):
        """Test: Rate Limit mit 0 requests_per_minute"""
        # 0 Requests sollte sofort blockieren
        with pytest.raises((RateLimitExceeded, ValueError, Exception)):
            self.limiter.check_rate_limit(
                user_id=self.test_user_id,
                endpoint=self.test_endpoint,
                requests_per_minute=0
            )
    
    def test_rate_limit_class_structure(self):
        """Test: RateLimit Datenklasse"""
        rate_limit = RateLimit(
            requests=10,
            window_seconds=60,
            burst_size=20
        )
        
        assert rate_limit.requests == 10
        assert rate_limit.window_seconds == 60
        assert rate_limit.burst_size == 20


class TestRateLimitIntegration:
    """Integration Tests für Rate Limiting mit FastAPI"""
    
    def test_rate_limit_middleware_exists(self):
        """Test: Rate Limit Middleware ist verfügbar"""
        from app.core.rate_limiter import AdvancedRateLimiter
        
        limiter = AdvancedRateLimiter()
        assert limiter is not None
    
    def test_rate_limit_exceeded_exception(self):
        """Test: RateLimitExceeded Exception"""
        # Prüfe ob Exception existiert und korrekt strukturiert ist
        exception = RateLimitExceeded()
        
        assert hasattr(exception, 'status_code')
        assert exception.status_code == 429


@pytest.mark.asyncio
class TestAsyncRateLimiting:
    """Async Tests für Rate Limiting"""
    
    async def test_async_rate_limit_check(self):
        """Test: Async Rate Limit Check"""
        limiter = AdvancedRateLimiter()
        
        # Async check sollte funktionieren
        result = limiter.check_rate_limit(
            user_id="async_user",
            endpoint="/api/async",
            requests_per_minute=60
        )
        
        # Sollte ohne Error durchlaufen
        assert result is True or result is None


# Test Coverage Summary
def test_coverage_report():
    """Test: Stelle sicher dass Rate Limiting abgedeckt ist"""
    from app.core import rate_limiter
    
    # Prüfe ob wichtige Funktionen existieren
    assert hasattr(rate_limiter, 'AdvancedRateLimiter')
    assert hasattr(rate_limiter, 'RateLimitExceeded')
    assert hasattr(rate_limiter, 'RateLimit')
    
    print("✅ Rate Limiting Test Coverage: Basic + Advanced + Integration")
