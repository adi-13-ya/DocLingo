"""
Uncertainty Handler - Phase 5 (Refactored)
Non-blocking: only adjusts confidence and logs warnings.
Never alters answer text.
"""

import logging
from typing import Dict, List, Optional, Any

# Setup diagnostic logging
_diagnostic_logger = logging.getLogger("doclingo.uncertainty")
_diagnostic_logger.setLevel(logging.DEBUG)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('🔍 [UNCERTAINTY] %(message)s'))
_diagnostic_logger.addHandler(_handler)


class UncertaintyHandler:
    """
    Non-blocking uncertainty handler.
    Only adjusts confidence levels and logs warnings.
    Never modifies answer text.
    """
    
    def __init__(self):
        """Initialize uncertainty handler."""
        # Confidence thresholds
        self.low_confidence_threshold = "Low"
        self.medium_confidence_threshold = "Medium"
        
        # Minimum chunks required for confident answer
        self.min_chunks_for_confidence = 2
        
        # Minimum similarity score for confident answer
        self.min_similarity_for_confidence = 0.5
        
        # Cross-lingual similarity thresholds (more lenient)
        self.min_similarity_crosslingual = 0.25  # Lower threshold for cross-lingual
        self.min_similarity_same_language = 0.5  # Standard threshold for same language
    
    def should_adjust_confidence(
        self,
        confidence: str,
        num_chunks: int,
        avg_similarity: Optional[float] = None,
        answer: Optional[str] = None,
        target_language: str = "en",
        query_intent: Optional[str] = None,
        document_language: Optional[str] = None,
        query_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determine if confidence should be adjusted (downgraded).
        Non-blocking: only adjusts confidence, never blocks answers.
        
        Args:
            confidence: Confidence level ("High", "Medium", "Low")
            num_chunks: Number of retrieved chunks
            avg_similarity: Average FAISS similarity score (0.0 to 1.0)
            answer: Generated answer (optional, for logging)
            target_language: Target language for messages
            query_intent: Intent of the query (e.g., "summarization", "comparison")
            document_language: Document language code
            query_language: Query language code
            
        Returns:
            Dictionary with:
                - adjust_confidence: Boolean (True if confidence should be downgraded)
                - reason: Explanation
                - adjusted_confidence: Suggested confidence level if adjustment needed
                - warnings: List of warning messages
        """
        _diagnostic_logger.debug(f"=== Uncertainty Handler (Non-blocking) ===")
        _diagnostic_logger.debug(f"Confidence: {confidence}, Chunks: {num_chunks}, Similarity: {avg_similarity}")
        _diagnostic_logger.debug(f"Intent: {query_intent}, Doc Lang: {document_language}, Query Lang: {query_language}")
        
        warnings = []
        downgrade_reasons = []
        
        # Detect cross-lingual scenario
        is_crosslingual = document_language and query_language and document_language != query_language
        if is_crosslingual:
            _diagnostic_logger.debug(f"🔄 Cross-lingual detected: doc={document_language}, query={query_language}")
            similarity_threshold = self.min_similarity_crosslingual
        else:
            similarity_threshold = self.min_similarity_same_language
        
        # For summarization queries, be more lenient (they work with entire document)
        is_summarization = query_intent == "summarization"
        
        # Check 1: Insufficient chunks (downgrade confidence)
        min_chunks_needed = 1 if is_summarization else self.min_chunks_for_confidence
        if num_chunks < min_chunks_needed and num_chunks > 0:
            downgrade_reasons.append(f"Insufficient chunks ({num_chunks} < {min_chunks_needed})")
            warnings.append(f"Only {num_chunks} chunk(s) retrieved")
            _diagnostic_logger.debug(f"⚠️ MODERATE: Insufficient chunks - will downgrade confidence")
        
        # Check 2: Low similarity scores (downgrade confidence)
        if avg_similarity is not None:
            _diagnostic_logger.debug(f"Similarity check: {avg_similarity:.4f} < {similarity_threshold:.4f}?")
            
            if avg_similarity < similarity_threshold and not is_summarization:
                downgrade_reasons.append(f"Moderate similarity (avg: {avg_similarity:.2%} < {similarity_threshold:.2%})")
                warnings.append(f"Low similarity score: {avg_similarity:.2%}")
                _diagnostic_logger.debug(f"⚠️ MODERATE: Low similarity - will downgrade confidence")
        
        # Check 3: Medium confidence with weak signals (downgrade to Low)
        if not is_summarization and confidence == self.medium_confidence_threshold:
            if num_chunks < 3 or (avg_similarity is not None and avg_similarity < (similarity_threshold * 1.2)):
                downgrade_reasons.append("Medium confidence with weak supporting evidence")
                warnings.append("Weak evidence for medium confidence")
                _diagnostic_logger.debug("⚠️ MODERATE: Medium confidence with weak evidence - downgrade to Low")
        
        # Determine confidence adjustment
        adjust_confidence = len(downgrade_reasons) > 0
        adjusted_confidence = None
        
        if adjust_confidence:
            # Downgrade: High -> Medium, Medium -> Low, Low stays Low
            if confidence == "High":
                adjusted_confidence = "Medium"
            elif confidence == "Medium":
                adjusted_confidence = "Low"
            else:
                adjusted_confidence = "Low"  # Keep it Low
        
        # DIAGNOSTIC LOG: Decision
        if adjust_confidence:
            _diagnostic_logger.debug(f"🟡 DECISION: ADJUST CONFIDENCE {confidence} -> {adjusted_confidence} - Reasons: {downgrade_reasons}")
        else:
            _diagnostic_logger.debug(f"🟢 DECISION: NO ADJUSTMENT - Confidence is appropriate")
        
        return {
            "adjust_confidence": adjust_confidence,
            "reason": "; ".join(downgrade_reasons) if downgrade_reasons else "Sufficient evidence for current confidence",
            "adjusted_confidence": adjusted_confidence,
            "warnings": warnings,
            "target_language": target_language,
            "is_crosslingual": is_crosslingual,
            "similarity_threshold_used": similarity_threshold
        }
