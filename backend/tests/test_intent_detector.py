"""
Tests for Intent Detector
"""
import pytest
from app.core.intent_detector import IntentDetector


class TestIntentDetector:
    """Test intent detection for auto code review"""
    
    def setup_method(self):
        """Setup test instance"""
        self.detector = IntentDetector()
    
    # German Intent Detection Tests
    
    def test_german_review_intent(self):
        """Test detecting German review requests"""
        test_cases = [
            "Review meinen Code",
            "Überprüfe mein Backend",
            "Analysiere den Frontend Code",
            "Verbessere mein Projekt",
            "Optimiere meinen Code"
        ]
        
        for message in test_cases:
            result = self.detector.detect_code_review_intent(message)
            assert result is not None, f"Failed for: {message}"
            assert result['type'] == 'code_review'
            assert result['language'] == 'de'
    
    def test_german_bug_finding_intent(self):
        """Test detecting German bug finding requests"""
        test_cases = [
            "Finde Fehler in meinem Code",
            "Suche Bugs im Backend"
        ]
        
        for message in test_cases:
            result = self.detector.detect_code_review_intent(message)
            assert result is not None
            assert result['type'] == 'code_review'
    
    # English Intent Detection Tests
    
    def test_english_review_intent(self):
        """Test detecting English review requests"""
        test_cases = [
            "Review my code",
            "Analyze my backend",
            "Check the frontend code",
            "Improve my project",
            "Optimize my code"
        ]
        
        for message in test_cases:
            result = self.detector.detect_code_review_intent(message)
            assert result is not None, f"Failed for: {message}"
            assert result['type'] == 'code_review'
            assert result['language'] == 'en'
    
    def test_english_bug_finding_intent(self):
        """Test detecting English bug finding requests"""
        test_cases = [
            "Find bugs in my code",
            "Detect errors in the backend"
        ]
        
        for message in test_cases:
            result = self.detector.detect_code_review_intent(message)
            assert result is not None
            assert result['type'] == 'code_review'
    
    # Scope Detection Tests
    
    def test_backend_scope_detection(self):
        """Test detecting backend scope"""
        test_cases = [
            "Review my backend",
            "Analyze the backend code",
            "Check backend API"
        ]
        
        for message in test_cases:
            result = self.detector.detect_code_review_intent(message)
            assert result is not None
            assert result['scope'] == 'backend'
    
    def test_frontend_scope_detection(self):
        """Test detecting frontend scope"""
        test_cases = [
            "Review my frontend",
            "Analyze the frontend code",
            "Check React components"
        ]
        
        for message in test_cases:
            result = self.detector.detect_code_review_intent(message)
            assert result is not None
            assert result['scope'] == 'frontend'
    
    def test_full_scope_detection(self):
        """Test detecting full/complete scope"""
        test_cases = [
            "Review all my code",
            "Analyze the entire project",
            "Check the complete codebase"
        ]
        
        for message in test_cases:
            result = self.detector.detect_code_review_intent(message)
            assert result is not None
            assert result['scope'] == 'full'
    
    def test_default_full_scope(self):
        """Test default scope is full when not specified"""
        result = self.detector.detect_code_review_intent("Review my code")
        assert result is not None
        assert result['scope'] == 'full'
    
    # Negative Tests (Non-Intent Messages)
    
    def test_non_review_message(self):
        """Test that non-review messages return None"""
        test_cases = [
            "Hello, how are you?",
            "What's the weather like?",
            "Tell me a joke",
            "Explain quantum physics",
            "How to cook pasta"
        ]
        
        for message in test_cases:
            result = self.detector.detect_code_review_intent(message)
            assert result is None, f"False positive for: {message}"
    
    def test_empty_message(self):
        """Test empty message returns None"""
        result = self.detector.detect_code_review_intent("")
        assert result is None
    
    def test_whitespace_only_message(self):
        """Test whitespace-only message returns None"""
        result = self.detector.detect_code_review_intent("   ")
        assert result is None
    
    # Language Detection Tests
    
    def test_german_language_detection(self):
        """Test German language is correctly identified"""
        german_messages = [
            "Überprüfe meinen Code",
            "Analysiere das Backend",
            "Finde Fehler"
        ]
        
        for message in german_messages:
            result = self.detector.detect_code_review_intent(message)
            assert result is not None
            assert result['language'] == 'de'
    
    def test_english_language_detection(self):
        """Test English language is correctly identified"""
        english_messages = [
            "Review my code",
            "Analyze the backend",
            "Find bugs"
        ]
        
        for message in english_messages:
            result = self.detector.detect_code_review_intent(message)
            assert result is not None
            assert result['language'] == 'en'
    
    # Edge Cases
    
    def test_mixed_case_message(self):
        """Test messages with mixed case"""
        result = self.detector.detect_code_review_intent("ReViEw My CoDe")
        assert result is not None
        assert result['type'] == 'code_review'
    
    def test_message_with_special_characters(self):
        """Test messages with special characters"""
        result = self.detector.detect_code_review_intent("Review my code! @#$%")
        assert result is not None
        assert result['type'] == 'code_review'
    
    def test_long_message_with_intent(self):
        """Test long message containing review intent"""
        long_message = "Hello, I would like you to please review my backend code and find any bugs or issues. Thank you!"
        result = self.detector.detect_code_review_intent(long_message)
        assert result is not None
        assert result['type'] == 'code_review'
        assert result['scope'] == 'backend'
