import re
from typing import Dict, Optional
from collections import Counter

class LanguageDetector:
    """Simple language detection based on common words and patterns"""
    
    def __init__(self):
        # Common words for language detection
        self.language_patterns = {
            'english': {
                'common_words': ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with', 'for', 'as', 'was', 'on', 'are', 'you', 'this', 'be', 'at', 'have'],
                'question_words': ['what', 'how', 'why', 'when', 'where', 'who', 'which'],
                'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
            },
            'german': {
                'common_words': ['der', 'die', 'das', 'und', 'ist', 'in', 'zu', 'den', 'von', 'mit', 'sich', 'auf', 'für', 'als', 'war', 'an', 'sind', 'du', 'dieser', 'haben'],
                'question_words': ['was', 'wie', 'warum', 'wann', 'wo', 'wer', 'welche', 'welcher'],
                'greeting': ['hallo', 'guten morgen', 'guten tag', 'guten abend', 'hi']
            },
            'spanish': {
                'common_words': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al'],
                'question_words': ['qué', 'cómo', 'por qué', 'cuándo', 'dónde', 'quién', 'cuál'],
                'greeting': ['hola', 'buenos días', 'buenas tardes', 'buenas noches']
            },
            'french': {
                'common_words': ['le', 'de', 'et', 'être', 'un', 'à', 'avoir', 'ne', 'je', 'son', 'que', 'se', 'qui', 'ce', 'dans', 'en', 'du', 'elle', 'au', 'de'],
                'question_words': ['quoi', 'comment', 'pourquoi', 'quand', 'où', 'qui', 'quel'],
                'greeting': ['bonjour', 'bonsoir', 'salut']
            },
            'italian': {
                'common_words': ['il', 'di', 'che', 'e', 'la', 'per', 'un', 'in', 'con', 'non', 'da', 'su', 'del', 'le', 'al', 'si', 'dei', 'nel', 'ad', 'gli'],
                'question_words': ['cosa', 'come', 'perché', 'quando', 'dove', 'chi', 'quale'],
                'greeting': ['ciao', 'buongiorno', 'buonasera']
            }
        }
    
    def detect_language(self, text: str) -> Dict[str, any]:
        """
        Detect the language of the given text
        Returns: Dict with 'language', 'confidence', and 'scores'
        """
        if not text or len(text.strip()) < 3:
            return {'language': 'english', 'confidence': 0.5, 'scores': {}}
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return {'language': 'english', 'confidence': 0.5, 'scores': {}}
        
        scores = {}
        
        for lang, patterns in self.language_patterns.items():
            score = 0
            total_possible = 0
            
            # Check common words
            common_words_found = sum(1 for word in words if word in patterns['common_words'])
            score += common_words_found * 2
            total_possible += len(words) * 2
            
            # Check question words (higher weight)
            question_words_found = sum(1 for word in words if word in patterns['question_words'])
            score += question_words_found * 5
            total_possible += len([w for w in words if w in patterns['question_words']]) * 5
            
            # Check greetings (higher weight)
            for greeting in patterns['greeting']:
                if greeting in text_lower:
                    score += 10
                    total_possible += 10
            
            # Check language-specific patterns
            if lang == 'german':
                # German-specific patterns
                if re.search(r'\b(ich|mich|mir|mein|haben|werden|können|sollen|müssen)\b', text_lower):
                    score += 5
                if re.search(r'(ß|ä|ö|ü)', text_lower):
                    score += 3
            elif lang == 'spanish':
                # Spanish-specific patterns
                if re.search(r'\b(yo|me|mi|tener|ser|estar|poder|deber)\b', text_lower):
                    score += 5
                if re.search(r'(ñ|á|é|í|ó|ú)', text_lower):
                    score += 3
            elif lang == 'french':
                # French-specific patterns
                if re.search(r'\b(je|me|mon|avoir|être|pouvoir|devoir|aller)\b', text_lower):
                    score += 5
                if re.search(r'(à|è|é|ç|ù)', text_lower):
                    score += 3
            elif lang == 'italian':
                # Italian-specific patterns
                if re.search(r'\b(io|me|mio|avere|essere|potere|dovere|andare)\b', text_lower):
                    score += 5
                if re.search(r'(à|è|é|ì|ò|ù)', text_lower):
                    score += 3
            
            scores[lang] = score / max(total_possible, 1) if total_possible > 0 else 0
        
        # Find the language with the highest score
        if not scores or all(score == 0 for score in scores.values()):
            # Default to English if no clear match
            detected_language = 'english'
            confidence = 0.5
        else:
            detected_language = max(scores, key=scores.get)
            confidence = scores[detected_language]
            
            # Normalize confidence to 0-1 range
            if confidence > 1:
                confidence = min(confidence, 1.0)
            
            # Minimum confidence threshold
            if confidence < 0.3:
                detected_language = 'english'
                confidence = 0.5
        
        return {
            'language': detected_language,
            'confidence': confidence,
            'scores': scores
        }
    
    def get_system_message_for_language(self, language: str) -> str:
        """Get appropriate system message for detected language"""
        system_messages = {
            'english': "You are a helpful AI assistant. Respond in English.",
            'german': "Du bist ein hilfsreicher KI-Assistent. Antworte auf Deutsch.",
            'spanish': "Eres un asistente de IA útil. Responde en español.",
            'french': "Vous êtes un assistant IA utile. Répondez en français.",
            'italian': "Sei un assistente IA utile. Rispondi in italiano."
        }
        return system_messages.get(language, system_messages['english'])
    
    def get_language_code(self, language: str) -> str:
        """Get language code for the detected language"""
        codes = {
            'english': 'en',
            'german': 'de',
            'spanish': 'es',
            'french': 'fr',
            'italian': 'it'
        }
        return codes.get(language, 'en')