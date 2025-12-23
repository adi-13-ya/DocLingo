"""
Language Resolver - Explicit Language Selection
Resolves final document, query, and answer languages based on user selections and automatic detection.
Deterministic and explainable language resolution.
"""

from typing import Optional, Dict, Any


class LanguageResolver:
    """
    Resolves final languages for document, query, and answer.
    Respects user selections when provided, falls back to automatic detection otherwise.
    """
    
    def __init__(self):
        """Initialize language resolver."""
        pass
    
    def resolve_languages(
        self,
        user_doc_lang: Optional[str] = None,
        user_query_lang: Optional[str] = None,
        user_answer_lang: Optional[str] = None,
        detected_doc_lang: Optional[str] = None,
        detected_query_lang: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Resolve final languages based on user selections and detected languages.
        
        Rules:
        1. If user provides explicit language, use it (skip detection)
        2. If user doesn't provide, use detected language
        3. Answer language defaults to query language if not explicitly set
        4. All decisions are deterministic and explainable
        
        Args:
            user_doc_lang: User-selected document language (optional)
            user_query_lang: User-selected query language (optional)
            user_answer_lang: User-selected answer language (optional)
            detected_doc_lang: Auto-detected document language (fallback)
            detected_query_lang: Auto-detected query language (fallback)
            
        Returns:
            Dictionary with:
                - document_language: Final document language
                - query_language: Final query language
                - answer_language: Final answer language
                - resolution_explanation: Human-readable explanation
                - used_auto_detection: Boolean indicating if auto-detection was used
        """
        resolution_steps = []
        used_auto_detection = False
        
        # Resolve document language
        if user_doc_lang:
            document_language = user_doc_lang
            resolution_steps.append(f"Document language: User-selected '{user_doc_lang}'")
        elif detected_doc_lang:
            document_language = detected_doc_lang
            used_auto_detection = True
            resolution_steps.append(f"Document language: Auto-detected '{detected_doc_lang}'")
        else:
            # Fallback to 'en' if nothing available
            document_language = "en"
            resolution_steps.append("Document language: Defaulted to 'en' (no selection or detection)")
        
        # Resolve query language
        if user_query_lang:
            query_language = user_query_lang
            resolution_steps.append(f"Query language: User-selected '{user_query_lang}'")
        elif detected_query_lang:
            query_language = detected_query_lang
            used_auto_detection = True
            resolution_steps.append(f"Query language: Auto-detected '{detected_query_lang}'")
        else:
            # Fallback to document language if query not detected
            query_language = document_language
            resolution_steps.append(f"Query language: Defaulted to document language '{document_language}'")
        
        # Resolve answer language (CRITICAL: defaults to query language)
        if user_answer_lang:
            answer_language = user_answer_lang
            resolution_steps.append(f"Answer language: User-selected '{user_answer_lang}'")
        else:
            # DEFAULT RULE: answer_language = query_language
            answer_language = query_language
            resolution_steps.append(f"Answer language: Defaulted to query language '{query_language}'")
        
        # Build explanation
        resolution_explanation = " | ".join(resolution_steps)
        
        return {
            "document_language": document_language,
            "query_language": query_language,
            "answer_language": answer_language,
            "resolution_explanation": resolution_explanation,
            "used_auto_detection": used_auto_detection,
            "user_selections": {
                "document": user_doc_lang is not None,
                "query": user_query_lang is not None,
                "answer": user_answer_lang is not None
            }
        }
    
    def should_detect_document_language(self, user_doc_lang: Optional[str]) -> bool:
        """
        Determine if document language should be auto-detected.
        
        Args:
            user_doc_lang: User-selected document language (optional)
            
        Returns:
            True if detection should be performed, False otherwise
        """
        return user_doc_lang is None
    
    def should_detect_query_language(self, user_query_lang: Optional[str]) -> bool:
        """
        Determine if query language should be auto-detected.
        
        Args:
            user_query_lang: User-selected query language (optional)
            
        Returns:
            True if detection should be performed, False otherwise
        """
        return user_query_lang is None
    
    def should_translate_document(
        self,
        document_language: str,
        query_language: str,
        user_doc_lang: Optional[str] = None
    ) -> bool:
        """
        Determine if document should be translated.
        
        Args:
            document_language: Resolved document language
            query_language: Resolved query language
            user_doc_lang: User-selected document language (for context)
            
        Returns:
            True if translation is needed, False otherwise
        """
        # Translation needed if languages differ
        return document_language != query_language
    
    def should_translate_answer(
        self,
        answer_language: str,
        query_language: str
    ) -> bool:
        """
        Determine if answer should be translated.
        
        Args:
            answer_language: Resolved answer language
            query_language: Resolved query language
            
        Returns:
            True if translation is needed, False otherwise
        """
        # Translation needed if answer language differs from query language
        return answer_language != query_language

