"""
Unit tests for health check endpoint
Tests monitoring and observability features
"""
import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_endpoint_exists(self):
        """Test health endpoint is accessible"""
        response = client.get("/api/health")
        assert response.status_code == 200
    
    def test_health_response_structure(self):
        """Test health response has required fields"""
        response = client.get("/api/health")
        data = response.json()
        
        # Required top-level fields
        assert "status" in data
        assert "version" in data
        assert "platform" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert "services" in data
        assert "system" in data
        assert "environment" in data
    
    def test_health_status_values(self):
        """Test health status has valid values"""
        response = client.get("/api/health")
        data = response.json()
        
        assert data["status"] in ["healthy", "degraded", "limited"]
    
    def test_database_service_info(self):
        """Test database service information"""
        response = client.get("/api/health")
        data = response.json()
        
        db = data["services"]["database"]
        assert "status" in db
        assert "type" in db
        assert db["type"] == "SQLite"
    
    def test_ai_providers_info(self):
        """Test AI providers information"""
        response = client.get("/api/health")
        data = response.json()
        
        ai = data["services"]["ai_providers"]
        assert "configured" in ai
        assert "total" in ai
        assert "status" in ai
        assert ai["total"] >= 3  # At least openai, anthropic, perplexity
    
    def test_system_metrics(self):
        """Test system metrics are provided"""
        response = client.get("/api/health")
        data = response.json()
        
        system = data["system"]
        assert "memory_used_percent" in system
        assert "memory_available_mb" in system
        assert isinstance(system["memory_used_percent"], (int, float))
        assert system["memory_used_percent"] >= 0
        assert system["memory_used_percent"] <= 100
    
    def test_environment_info(self):
        """Test environment information"""
        response = client.get("/api/health")
        data = response.json()
        
        env = data["environment"]
        assert "debug" in env
        assert "log_level" in env
        assert isinstance(env["debug"], bool)
    
    def test_uptime_increases(self):
        """Test uptime increases between calls"""
        response1 = client.get("/api/health")
        import time
        time.sleep(1)
        response2 = client.get("/api/health")
        
        uptime1 = response1.json()["uptime_seconds"]
        uptime2 = response2.json()["uptime_seconds"]
        
        assert uptime2 >= uptime1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])