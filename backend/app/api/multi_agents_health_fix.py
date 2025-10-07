"""
Quick Health Check Fix for Multi-Agent System
Add fast health check without API calls
"""

# This patch adds a fast_health_check method that doesn't make external API calls

FAST_HEALTH_CHECK_CODE = '''
async def fast_health_check(self) -> Dict[str, Any]:
    """
    Fast health check without external API calls
    Checks only internal configuration
    """
    try:
        # Check basic configuration
        is_healthy = True
        errors = []
        
        # Verify API key exists
        if not self.api_key or self.api_key == "":
            is_healthy = False
            errors.append("API key not configured")
        
        # Verify provider and model set
        if not self.provider or not self.model:
            is_healthy = False
            errors.append("Provider or model not configured")
        
        return {
            "agent_type": self.agent_type.value,
            "provider": self.provider.value if self.provider else None,
            "model": self.model,
            "status": "healthy" if is_healthy else "degraded",
            "api_key_configured": bool(self.api_key and self.api_key != ""),
            "errors": errors,
            "response_time_ms": 0  # Instant check
        }
        
    except Exception as e:
        return {
            "agent_type": self.agent_type.value,
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": 0
        }
'''

print("Add this method to BaseAgent class in /app/backend/app/core/base_agent.py")
print(FAST_HEALTH_CHECK_CODE)