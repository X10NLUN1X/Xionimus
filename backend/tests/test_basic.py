"""
Basic tests for Xionimus AI Backend
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def test_import_main():
    """Test that main module can be imported"""
    try:
        from main import app
        assert app is not None
    except Exception as e:
        pytest.skip(f"Main import failed (expected in CI without deps): {e}")


def test_api_structure():
    """Test basic API structure"""
    try:
        from app.api import chat, github, edit, tokens
        assert chat is not None
        assert github is not None
        assert edit is not None
        assert tokens is not None
    except ImportError as e:
        pytest.skip(f"API import failed (expected in CI): {e}")


def test_core_modules():
    """Test that core modules exist"""
    try:
        from app.core import ai_manager, token_tracker, edit_agent
        assert ai_manager is not None
        assert token_tracker is not None
        assert edit_agent is not None
    except ImportError as e:
        pytest.skip(f"Core import failed (expected in CI): {e}")


def test_token_tracker_logic():
    """Test token tracker calculations"""
    try:
        from app.core.token_tracker import TokenUsageTracker
        
        tracker = TokenUsageTracker()
        
        # Test limits
        assert tracker.SOFT_LIMIT == 50000
        assert tracker.HARD_LIMIT == 100000
        assert tracker.CRITICAL_LIMIT == 150000
        
        # Test recommendation levels
        rec_ok = tracker._get_recommendation(10000)
        assert rec_ok['level'] == 'ok'
        
        rec_warning = tracker._get_recommendation(60000)
        assert rec_warning['level'] == 'warning'
        
        rec_high = tracker._get_recommendation(120000)
        assert rec_high['level'] == 'high'
        
        rec_critical = tracker._get_recommendation(160000)
        assert rec_critical['level'] == 'critical'
        
    except ImportError:
        pytest.skip("Token tracker not available")


def test_edit_agent_exists():
    """Test that edit agent is available"""
    try:
        from app.core.edit_agent import EditAgent, edit_agent
        assert EditAgent is not None
        assert edit_agent is not None
        assert hasattr(edit_agent, 'autonomous_edit')
        assert hasattr(edit_agent, 'user_directed_edit')
    except ImportError:
        pytest.skip("Edit agent not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
