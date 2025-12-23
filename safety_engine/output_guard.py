"""
Output Guard - Phase 5
Validates LLM-generated answers for grounding and safety.
Ensures answers are based on retrieved document chunks.
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
    Validates generated answers to ensure they are:
    - Grounded in retrieved document chunks
    - Not hallucinated or speculative
    - Safe and appropriate
    """
    
    def __init__(self):
        """Initialize output guard."""
        # Phrases that indicate uncertainty or lack of grounding
        self.uncertainty_phrases = [
            r'i\s+(don\'?t|do\s+not)\s+know',
            r'i\s+(can\'?t|cannot)\s+(find|locate|determine)',
            r'not\s+(mentioned|stated|found|available)\s+in',
            r'no\s+information\s+(available|provided|found)',
            r'unable\s+to\s+(find|locate|determine)',
        ]
        
        # Phrases that indicate speculation (red flags)
        self.speculation_phrases = [
            r'probably',
            r'likely',
            r'possibly',
            r'might\s+be',
            r'could\s+be',
            r'perhaps',
            r'may\s+be',
            r'seems\s+to\s+be',
            r'appears\s+to\s+be',
            r'i\s+believe',
            r'i\s+think',
            r'in\s+my\s+opinion',
        ]
        
        # Compile patterns
        self.uncertainty_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.uncertainty_phrases]
        self.speculation_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.speculation_phrases]
        
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
        Validate generated answer for grounding and safety.
        
        Args:
            answer: Generated answer text
            retrieved_chunks: List of retrieved document chunks
            query: Original user query
            confidence: Confidence level ("High", "Medium", "Low")
            
        Returns:
            Dictionary with:
                - is_valid: Boolean
                - reason: Explanation
                - fallback_answer: Safe fallback if invalid
                - warnings: List of warnings
        """
        # DIAGNOSTIC LOG: Input parameters
        _diagnostic_logger.debug(f"=== Output Guard Validation ===")
        _diagnostic_logger.debug(f"Answer length: {len(answer) if answer else 0}, Confidence: {confidence}, Target Lang: {target_language}")
        _diagnostic_logger.debug(f"Retrieved chunks: {len(retrieved_chunks)} chunks")
        answer_preview = answer[:200] + "..." if answer and len(answer) > 200 else (answer or "")
        _diagnostic_logger.debug(f"Answer preview: {answer_preview}")
        
        warnings = []
        
        # Import multilingual messages
        from language_manager.multilingual_messages import get_message_generator
        msg_gen = get_message_generator()
        
        # Check 1: Answer exists and is valid type
        if not answer or not isinstance(answer, str):
            return {
                "is_valid": False,
                "reason": "Answer is empty or invalid type",
                "fallback_answer": msg_gen.get_processing_error_message(target_language),
                "warnings": []
            }
        
        answer = answer.strip()
        
        # Check 2: Answer length
        if len(answer) < self.min_answer_length:
            return {
                "is_valid": False,
                "reason": f"Answer too short (minimum {self.min_answer_length} characters)",
                "fallback_answer": msg_gen.get_no_answer_message(target_language),
                "warnings": []
            }
        
        if len(answer) > self.max_answer_length:
            warnings.append(f"Answer very long ({len(answer)} characters)")
        
        # Check 3: Grounding validation (if chunks available)
        if retrieved_chunks:
            grounding_score = self._check_grounding(answer, retrieved_chunks, target_language)
            _diagnostic_logger.debug(f"Grounding score: {grounding_score:.4f}")
            
            # Use language-aware threshold
            # For non-English: more lenient (grounding check returns 0.5 minimum)
            # For English: stricter validation
            is_english = target_language == "en"
            min_grounding_threshold = 0.1 if is_english else 0.3  # Lower bar for non-English
            _diagnostic_logger.debug(f"Min grounding threshold: {min_grounding_threshold} (English: {is_english})")
            
            if grounding_score < min_grounding_threshold:
                # Only reject if very low score (likely hallucination)
                if grounding_score < 0.1:
                    _diagnostic_logger.debug(f"❌ REJECTED: Very low grounding score ({grounding_score:.4f} < 0.1)")
                    return {
                        "is_valid": False,
                        "reason": "Answer appears to be hallucinated (low overlap with retrieved chunks)",
                        "fallback_answer": msg_gen.get_no_answer_message(target_language),
                        "warnings": warnings,
                        "grounding_score": grounding_score
                    }
                else:
                    # For moderate scores in non-English, add warning but allow
                    warnings.append("Answer has moderate grounding score")
                    _diagnostic_logger.debug(f"⚠️ WARNING: Moderate grounding score ({grounding_score:.4f}) - allowing with warning")
            
            if grounding_score < 0.3 and is_english:  # Low overlap (English only)
                warnings.append("Answer has low grounding score - may contain speculation")
                _diagnostic_logger.debug(f"⚠️ WARNING: Low grounding score for English ({grounding_score:.4f} < 0.3)")
        
        # Check 4: Excessive speculation detection
        speculation_count = sum(1 for pattern in self.speculation_patterns if pattern.search(answer))
        
        if speculation_count > 3:  # Too many speculative phrases
            warnings.append("Answer contains multiple speculative phrases")
        
        # Check 5: Confidence mismatch
        if confidence == "High" and speculation_count > 2:
            warnings.append("High confidence but answer contains speculation")
        
        # Check 6: Explicit uncertainty (this is OK, but should be handled by uncertainty_handler)
        uncertainty_detected = any(pattern.search(answer) for pattern in self.uncertainty_patterns)
        
        if uncertainty_detected:
            # This is acceptable - uncertainty_handler will handle it
            pass
        
        # Final decision
        is_valid = len(warnings) < 3  # Allow if warnings are manageable
        
        if not is_valid:
            fallback = msg_gen.get_no_answer_message(target_language)
            _diagnostic_logger.debug(f"❌ FINAL DECISION: REJECTED - Too many warnings ({len(warnings)})")
        else:
            fallback = None
            if warnings:
                _diagnostic_logger.debug(f"✅ FINAL DECISION: ACCEPTED with {len(warnings)} warning(s)")
            else:
                _diagnostic_logger.debug(f"✅ FINAL DECISION: ACCEPTED - No warnings")
        
        return {
            "is_valid": is_valid,
            "reason": "Answer passed validation" if is_valid else "Answer failed validation due to multiple warnings",
            "fallback_answer": fallback,
            "warnings": warnings,
            "grounding_score": grounding_score if retrieved_chunks else None
        }
    
    def _check_grounding(self, answer: str, chunks: List[str], target_language: str = "en") -> float:
        """
        Check how well the answer is grounded in retrieved chunks.
        Language-aware: uses lenient validation for non-English answers.
        
        Args:
            answer: Generated answer
            chunks: Retrieved document chunks
            target_language: Target language code (e.g., "en", "te", "hi")
            
        Returns:
            Grounding score (0.0 to 1.0)
        """
        if not chunks:
            return 0.0
        
        # Check if answer contains significant non-ASCII content (non-English)
        non_ascii_ratio = sum(1 for c in answer if ord(c) > 127) / len(answer) if answer else 0
        is_english = target_language == "en" and non_ascii_ratio < 0.3
        
        # For non-English answers, use lenient validation
        # (word overlap won't work well across languages)
        if not is_english:
            # For multilingual answers, check if answer has meaningful content
            # rather than strict word overlap
            if len(answer.strip()) < 10:
                return 0.0
            
            # If answer is long enough and chunks exist, assume reasonable grounding
            # This is lenient because exact word matching doesn't work across languages
            return 0.5  # Return moderate score for non-English to avoid false rejections
        
        # English-specific word overlap check
        # Extract significant words from answer (exclude common words)
        answer_words = set(re.findall(r'\b[a-z]{4,}\b', answer.lower()))
        
        # Remove common stop words
        stop_words = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 'what', 'when', 'where', 'which', 'would', 'could', 'should', 'will', 'shall', 'may', 'might', 'must', 'can', 'could'}
        answer_words = answer_words - stop_words
        
        if not answer_words:
            # If no significant words found, check if answer is at least substantial
            if len(answer.strip()) > 50:
                return 0.3  # Moderate score for substantial but word-poor answers
            return 0.0
        
        # Check overlap with chunks
        chunk_text = ' '.join(chunks).lower()
        chunk_words = set(re.findall(r'\b[a-z]{4,}\b', chunk_text))
        chunk_words = chunk_words - stop_words
        
        # Calculate overlap
        if not chunk_words:
            # If chunks have no words (e.g., non-English), use lenient score
            return 0.5 if len(answer.strip()) > 20 else 0.3
        
        overlap = len(answer_words & chunk_words)
        total_answer_words = len(answer_words)
        
        if total_answer_words == 0:
            return 0.0
        
        # Score: percentage of answer words found in chunks
        score = overlap / total_answer_words
        
        return min(score, 1.0)
    
    def get_safe_fallback(self, query: str, reason: str = "Unable to generate answer", target_language: str = "en") -> str:
        """
        Get a safe fallback answer when validation fails.
        
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

