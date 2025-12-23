"""
Multilingual Message Generator - Change 1
Generates fallback, error, and uncertainty messages in the query language.
Centralized message generation to avoid hardcoded English strings.
"""

from typing import Optional
from deep_translator import GoogleTranslator


class MultilingualMessageGenerator:
    """
    Generates system messages in the target language.
    All fallback, error, and uncertainty messages are translated to match query language.
    """
    
    def __init__(self):
        """Initialize multilingual message generator."""
        # Base English messages (will be translated)
        self.base_messages = {
            "no_content": "No readable content found in the document.",
            "no_answer": "I couldn't find enough information in the document to answer this question. The document may not contain the information you're looking for, or the information may be insufficient to provide a confident answer.",
            "low_similarity": "The document contains some related information, but it may not directly answer your question. The retrieved content has low similarity to your query.",
            "insufficient_chunks": "I found limited information in the document related to your question. The answer may be incomplete or uncertain.",
            "uncertain_answer": "The document does not provide enough information to answer this question confidently. The available evidence is insufficient or uncertain.",
            "translation_failed": "Translation failed. Please try again.",
            "query_rejected": "Your query was blocked by safety checks. Please rephrase your question without attempting to override system instructions.",
            "processing_error": "An error occurred while processing your request. Please try again.",
        }
    
    def get_message(
        self,
        message_key: str,
        target_language: str = "en",
        fallback_to_english: bool = True
    ) -> str:
        """
        Get a message in the target language.
        
        Args:
            message_key: Key for the message (e.g., "no_answer", "low_similarity")
            target_language: Target language code (default: "en")
            fallback_to_english: If True, return English if translation fails
            
        Returns:
            Message in target language
        """
        if message_key not in self.base_messages:
            return self.base_messages.get("processing_error", "An error occurred.")
        
        base_message = self.base_messages[message_key]
        
        # If target is English, return base message
        if target_language == "en" or target_language is None:
            return base_message
        
        # Translate to target language
        try:
            translated = GoogleTranslator(
                source="en",
                target=target_language
            ).translate(base_message)
            return translated
        except Exception as e:
            print(f"⚠️ Message translation failed for '{message_key}' to {target_language}: {e}")
            if fallback_to_english:
                return base_message
            return f"[Translation unavailable] {base_message}"
    
    def get_no_content_message(self, target_language: str = "en") -> str:
        """Get 'no content' message in target language."""
        return self.get_message("no_content", target_language)
    
    def get_no_answer_message(self, target_language: str = "en") -> str:
        """Get 'no answer' message in target language."""
        return self.get_message("no_answer", target_language)
    
    def get_low_similarity_message(self, target_language: str = "en") -> str:
        """Get 'low similarity' message in target language."""
        return self.get_message("low_similarity", target_language)
    
    def get_insufficient_chunks_message(self, target_language: str = "en") -> str:
        """Get 'insufficient chunks' message in target language."""
        return self.get_message("insufficient_chunks", target_language)
    
    def get_uncertain_answer_message(self, target_language: str = "en") -> str:
        """Get 'uncertain answer' message in target language."""
        return self.get_message("uncertain_answer", target_language)
    
    def get_query_rejected_message(self, target_language: str = "en") -> str:
        """Get 'query rejected' message in target language."""
        return self.get_message("query_rejected", target_language)
    
    def get_processing_error_message(self, target_language: str = "en") -> str:
        """Get 'processing error' message in target language."""
        return self.get_message("processing_error", target_language)


# Global instance for easy access
_message_generator = None

def get_message_generator() -> MultilingualMessageGenerator:
    """Get global message generator instance."""
    global _message_generator
    if _message_generator is None:
        _message_generator = MultilingualMessageGenerator()
    return _message_generator

