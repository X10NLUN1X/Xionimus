"""
Tests for Token Usage Tracker
"""
import pytest
import tempfile
import os
import asyncio
from pathlib import Path
from app.core.token_tracker import TokenUsageTracker


@pytest.fixture
def tracker():
    """Create tracker with temp storage"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w')
    temp_file.close()
    
    tracker = TokenUsageTracker()
    tracker.storage_file = Path(temp_file.name)
    tracker.reset_session()
    tracker.save_usage()
    
    yield tracker
    
    # Cleanup
    try:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    except Exception:
        pass


def test_session_reset_on_new_session_id(tracker):
    """
    Test that session resets correctly when session_id changes
    
    Expected: New session starts with 0 tokens
    """
    # Session 1
    tracker.track_usage("session-1", prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
    assert tracker.current_session['total_tokens'] == 1500, "Session 1 should have 1500 tokens"
    assert tracker.current_session['session_id'] == "session-1"
    
    # Session 2 - SHOULD RESET
    tracker.track_usage("session-2", prompt_tokens=2000, completion_tokens=1000, total_tokens=3000)
    
    # Verify reset worked
    assert tracker.current_session['total_tokens'] == 3000, \
        f"Session 2 should have 3000 tokens (fresh start), but has {tracker.current_session['total_tokens']}"
    assert tracker.current_session['session_id'] == "session-2", \
        "Session ID should be updated"
    
    # Old session should be in total_usage
    assert tracker.total_usage['sessions_count'] >= 1, \
        "Previous session should be counted in total"
    assert tracker.total_usage['all_time_tokens'] >= 1500, \
        "Previous session tokens should be in all_time total"


def test_token_stats_return_type(tracker):
    """
    Test that get_usage_stats always returns valid dict structure
    """
    # Test with empty session
    stats = tracker.get_usage_stats()
    
    assert stats is not None, "Stats should never be None"
    assert isinstance(stats, dict), "Stats should be a dict"
    assert 'current_session' in stats, "Missing current_session key"
    assert 'recommendation' in stats, "Missing recommendation key"
    assert 'limits' in stats, "Missing limits key"
    assert 'percentages' in stats, "Missing percentages key"
    
    # Check nested structure
    assert 'total_tokens' in stats['current_session'], "Missing total_tokens in current_session"
    assert 'level' in stats['recommendation'], "Missing level in recommendation"
    assert 'soft_limit' in stats['limits'], "Missing soft_limit"


def test_multiple_sessions_sequential(tracker):
    """
    Test multiple session switches in sequence
    """
    # Create 5 sessions
    for i in range(5):
        tracker.track_usage(f"session-{i}", prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
    
    # Current session should be session-4 with 1500 tokens
    assert tracker.current_session['session_id'] == "session-4"
    assert tracker.current_session['total_tokens'] == 1500
    
    # Should have 4 completed sessions (0-3)
    assert tracker.total_usage['sessions_count'] == 4
    # Total should be 1500 * 4 = 6000
    assert tracker.total_usage['all_time_tokens'] == 6000


def test_negative_tokens_prevented(tracker):
    """
    Ensure negative tokens don't corrupt state
    """
    # Try to track negative tokens (malformed input)
    tracker.track_usage("test", prompt_tokens=-500, completion_tokens=0, total_tokens=-500)
    
    # Should be 0, not negative
    assert tracker.current_session['total_tokens'] >= 0, "Tokens should never be negative"
    assert tracker.current_session['prompt_tokens'] >= 0, "Prompt tokens should never be negative"


def test_recommendation_levels(tracker):
    """
    Test recommendation levels at different token counts
    """
    # OK level (< 50k)
    rec_ok = tracker._get_recommendation(10000)
    assert rec_ok['level'] == 'ok'
    assert rec_ok['color'] == 'green'
    
    # Warning level (50k-100k)
    rec_warning = tracker._get_recommendation(60000)
    assert rec_warning['level'] == 'warning'
    assert rec_warning['color'] == 'yellow'
    assert 'fork' in rec_warning['action'].lower()
    
    # High level (100k-150k)
    rec_high = tracker._get_recommendation(120000)
    assert rec_high['level'] == 'high'
    assert rec_high['color'] == 'orange'
    assert 'fork' in rec_high['action'].lower()
    
    # Critical level (> 150k)
    rec_critical = tracker._get_recommendation(160000)
    assert rec_critical['level'] == 'critical'
    assert rec_critical['color'] == 'red'
    assert 'critical' in rec_critical['action'].lower()


def test_accumulation_within_session(tracker):
    """
    Test that tokens accumulate correctly within same session
    """
    tracker.track_usage("same-session", 100, 50, 150)
    assert tracker.current_session['total_tokens'] == 150
    
    tracker.track_usage("same-session", 200, 100, 300)
    assert tracker.current_session['total_tokens'] == 450, "Tokens should accumulate within session"
    
    tracker.track_usage("same-session", 300, 150, 450)
    assert tracker.current_session['total_tokens'] == 900, "Tokens should continue accumulating"


def test_should_recommend_fork(tracker):
    """
    Test fork recommendation logic
    """
    # Below hard limit
    tracker.track_usage("test", 50000, 30000, 80000)
    assert not tracker.should_recommend_fork(), "Should not recommend fork below 100k"
    
    # At hard limit
    tracker.reset_session()
    tracker.track_usage("test", 70000, 30000, 100000)
    assert tracker.should_recommend_fork(), "Should recommend fork at 100k"
    
    # Above hard limit
    tracker.reset_session()
    tracker.track_usage("test", 80000, 50000, 130000)
    assert tracker.should_recommend_fork(), "Should recommend fork above 100k"


def test_persistence(tracker):
    """
    Test that data persists to file and can be loaded
    """
    # Track some usage
    tracker.track_usage("persist-test", 1000, 500, 1500)
    
    # Create new tracker with same file
    tracker2 = TokenUsageTracker()
    tracker2.storage_file = tracker.storage_file
    tracker2.load_usage()
    
    # Should have loaded the data
    assert tracker2.current_session['session_id'] == "persist-test"
    assert tracker2.current_session['total_tokens'] == 1500


def test_edge_case_very_large_tokens(tracker):
    """
    Test with tokens far exceeding critical limit
    """
    tracker.track_usage("huge", 1000000, 500000, 1500000)
    
    rec = tracker._get_recommendation(1500000)
    assert rec['level'] == 'critical'
    assert 'fork' in rec['action'].lower()
    
    stats = tracker.get_usage_stats()
    assert stats['current_session']['total_tokens'] == 1500000
    assert stats['recommendation']['level'] == 'critical'


def test_estimate_tokens(tracker):
    """
    Test token estimation from text
    """
    short_text = "Hello world"
    estimate_short = tracker.estimate_tokens(short_text)
    assert estimate_short > 0
    assert estimate_short < 10  # Should be ~3 tokens
    
    long_text = "A" * 1000
    estimate_long = tracker.estimate_tokens(long_text)
    assert estimate_long > estimate_short
    assert estimate_long == 250  # 1000 chars / 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
