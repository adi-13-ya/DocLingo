"""
Output Guard - Phase 5 (Refactored)
Non-blocking, user-experience focused validation.
Only rejects answers when zero chunks retrieved.
All other checks are soft (warnings only).
"""

import re
import logging
from typing import Dict, List, Optional, Any

# Setup diagnostic logging
_diagnostic_logger = logging.getLogger("doclingo.output_guard")
_diagnostic_logger.setLevel(logging.DEBUG)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('🔍 [OUTPUT_GUARD] %(message)s'))
_diagnostic_logger.addHandler(_handler)


class OutputGuard:
    """
    Non-blocking output validation.
    Only rejects answers when zero chunks retrieved.
    All other issues result in warnings only.
    """
    
    def __init__(self):
        """Initialize output guard."""
        # Minimum answer length (too short might be incomplete)
        self.min_answer_length = 10
        
        # Maximum answer length (prevent excessive output)
        self.max_answer_length = 5000
    
    def validate_answer(
        self,
        answer: str,
        retrieved_chunks: List[str],
        query: str,
        confidence: str,
        target_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Non-blocking validation: only rejects if zero chunks.
        All other checks produce warnings only.
        
        Args:
            answer: Generated answer text
            retrieved_chunks: List of retrieved document chunks
            query: Original user query
            confidence: Confidence level ("High", "Medium", "Low")
            target_language: Target language for messages
            
        Returns:
            Dictionary with:
                - is_valid: Boolean (False only if zero chunks)
                - reason: Explanation
                - warnings: List of warnings (soft checks)
                - grounding_score: None (moved to confidence engine)
        """
        _diagnostic_logger.debug(f"=== Output Guard Validation (Non-blocking) ===")
        _diagnostic_logger.debug(f"Answer length: {len(answer) if answer else 0}, Confidence: {confidence}")
        _diagnostic_logger.debug(f"Retrieved chunks: {len(retrieved_chunks)} chunks")
        
        warnings = []
        
        # Import multilingual messages
        from language_manager.multilingual_messages import get_message_generator
        msg_gen = get_message_generator()
        
        # Check 1: Answer exists and is valid type
        if not answer or not isinstance(answer, str):
            warnings.append("Answer is empty or invalid type")
            _diagnostic_logger.debug("⚠️ WARNING: Answer is empty or invalid type")
        
        if answer:
            answer = answer.strip()
            
            # Check 2: Answer length (warning only, never reject)
            if len(answer) < self.min_answer_length:
                warnings.append(f"Answer is very short ({len(answer)} characters)")
                _diagnostic_logger.debug(f"⚠️ WARNING: Answer too short ({len(answer)} characters)")
            
            if len(answer) > self.max_answer_length:
                warnings.append(f"Answer is very long ({len(answer)} characters)")
                _diagnostic_logger.debug(f"⚠️ WARNING: Answer very long ({len(answer)} characters)")
        
        # Check 3: Zero chunks retrieved (ONLY HARD REJECTION)
        if len(retrieved_chunks) == 0:
            _diagnostic_logger.debug("❌ REJECTED: Zero chunks retrieved")
            return {
                "is_valid": False,
                "reason": "No relevant chunks retrieved from document",
                "fallback_answer": msg_gen.get_no_answer_message(target_language),
                "warnings": warnings,
                "grounding_score": None  # Moved to confidence engine
            }
        
        # All other cases: answer is valid (non-blocking)
        _diagnostic_logger.debug(f"✅ ACCEPTED: Answer validated (with {len(warnings)} warning(s))")
        
        return {
            "is_valid": True,
            "reason": "Answer passed validation",
            "warnings": warnings,
            "grounding_score": None  # Grounding score computation moved to confidence engine
        }
    
    def get_safe_fallback(self, query: str, reason: str = "Unable to generate answer", target_language: str = "en") -> str:
        """
        Get a safe fallback answer when validation fails (zero chunks only).
        
        Args:
            query: Original query
            reason: Reason for fallback
            target_language: Target language for the message
            
        Returns:
            Safe fallback answer text in target language
        """
        from language_manager.multilingual_messages import get_message_generator
        msg_gen = get_message_generator()
        return msg_gen.get_no_answer_message(target_language)
