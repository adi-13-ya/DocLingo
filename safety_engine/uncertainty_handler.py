"""
Uncertainty Handler - Phase 5
Detects low-confidence cases and forces explicit uncertainty responses.
Deterministic and explainable uncertainty detection.
"""

import json
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
    Handles uncertainty by detecting weak evidence and forcing explicit responses.
    Prevents misleading answers when confidence is low.
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
    
    def should_force_uncertainty(
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
        Determine if uncertainty response should be forced.
        Refined to downgrade confidence instead of blocking answers for moderate cases.
        
        Args:
            confidence: Confidence level ("High", "Medium", "Low")
            num_chunks: Number of retrieved chunks
            avg_similarity: Average FAISS similarity score (0.0 to 1.0)
            answer: Generated answer (optional, for additional checks)
            target_language: Target language for messages
            query_intent: Intent of the query (e.g., "summarization", "comparison")
            document_language: Document language code
            query_language: Query language code
            
        Returns:
            Dictionary with:
                - force_uncertainty: Boolean (only True for severe cases)
                - downgrade_confidence: Boolean (True for moderate cases)
                - reason: Explanation
                - uncertainty_message: Message to show user (if force_uncertainty)
                - confidence_downgrade: Suggested confidence level if downgrade
        """
        # DIAGNOSTIC LOG: Input parameters
        _diagnostic_logger.debug(f"=== Uncertainty Handler Decision ===")
        _diagnostic_logger.debug(f"Confidence: {confidence}, Chunks: {num_chunks}, Similarity: {avg_similarity}")
        _diagnostic_logger.debug(f"Intent: {query_intent}, Doc Lang: {document_language}, Query Lang: {query_language}")
        if answer:
            answer_preview = answer[:200] + "..." if len(answer) > 200 else answer
            _diagnostic_logger.debug(f"Answer preview: {answer_preview}")
        
        reasons = []
        downgrade_reasons = []
        
        # Detect cross-lingual scenario
        is_crosslingual = document_language and query_language and document_language != query_language
        if is_crosslingual:
            _diagnostic_logger.debug(f"🔄 Cross-lingual detected: doc={document_language}, query={query_language}")
            # Use more lenient thresholds for cross-lingual
            similarity_threshold = self.min_similarity_crosslingual
        else:
            similarity_threshold = self.min_similarity_same_language
        
        # For summarization queries, be more lenient (they work with entire document)
        is_summarization = query_intent == "summarization"
        
        # Check 1: No chunks at all (SEVERE - force uncertainty)
        if num_chunks == 0:
            reasons.append("No relevant chunks retrieved from document")
            _diagnostic_logger.debug("❌ SEVERE: No chunks retrieved")
        
        # Check 2: Insufficient chunks (MODERATE - downgrade confidence, don't block)
        min_chunks_needed = 1 if is_summarization else self.min_chunks_for_confidence
        if num_chunks < min_chunks_needed and num_chunks > 0:
            downgrade_reasons.append(f"Insufficient chunks ({num_chunks} < {min_chunks_needed})")
            _diagnostic_logger.debug(f"⚠️ MODERATE: Insufficient chunks - will downgrade confidence")
        
        # Check 3: Very low similarity scores (SEVERE - force uncertainty)
        if avg_similarity is not None:
            _diagnostic_logger.debug(f"Similarity check: {avg_similarity:.4f} < {similarity_threshold:.4f}? (threshold adjusted for {'cross-lingual' if is_crosslingual else 'same-language'})")
            
            if avg_similarity < 0.1:  # Very low - likely no relevant content
                reasons.append(f"Very low similarity scores (avg: {avg_similarity:.2%} < 10%)")
                _diagnostic_logger.debug("❌ SEVERE: Very low similarity - force uncertainty")
            elif avg_similarity < similarity_threshold and not is_summarization:
                # Moderate similarity - downgrade confidence, don't block
                downgrade_reasons.append(f"Moderate similarity (avg: {avg_similarity:.2%} < {similarity_threshold:.2%})")
                _diagnostic_logger.debug(f"⚠️ MODERATE: Moderate similarity - will downgrade confidence")
        
        # Check 4: Low confidence (MODERATE - already low, just ensure it stays low)
        if confidence == self.low_confidence_threshold:
            if not is_summarization or num_chunks == 0:
                downgrade_reasons.append("Low confidence score")
                _diagnostic_logger.debug("⚠️ MODERATE: Low confidence - ensure it stays low")
        
        # Check 5: Medium confidence with weak signals (MODERATE - downgrade to Low)
        if not is_summarization and confidence == self.medium_confidence_threshold:
            if num_chunks < 3 or (avg_similarity is not None and avg_similarity < (similarity_threshold * 1.2)):
                downgrade_reasons.append("Medium confidence with weak supporting evidence")
                _diagnostic_logger.debug("⚠️ MODERATE: Medium confidence with weak evidence - downgrade to Low")
        
        # Decision: Only force uncertainty for severe cases (no chunks or very low similarity)
        force_uncertainty = len(reasons) > 0
        
        # Determine confidence downgrade
        downgrade_confidence = len(downgrade_reasons) > 0
        downgraded_confidence = None
        
        if downgrade_confidence:
            # Downgrade: High -> Medium, Medium -> Low, Low stays Low
            if confidence == "High":
                downgraded_confidence = "Medium"
            elif confidence == "Medium":
                downgraded_confidence = "Low"
            else:
                downgraded_confidence = "Low"  # Keep it Low
        
        # DIAGNOSTIC LOG: Decision
        if force_uncertainty:
            _diagnostic_logger.debug(f"🔴 DECISION: FORCE UNCERTAINTY - Reasons: {reasons}")
        elif downgrade_confidence:
            _diagnostic_logger.debug(f"🟡 DECISION: DOWNGRADE CONFIDENCE {confidence} -> {downgraded_confidence} - Reasons: {downgrade_reasons}")
        else:
            _diagnostic_logger.debug(f"🟢 DECISION: NO ACTION - Answer is acceptable")
        
        # Generate uncertainty message only if forcing uncertainty
        if force_uncertainty:
            uncertainty_message = self._generate_uncertainty_message(reasons, num_chunks, target_language)
        else:
            uncertainty_message = None
        
        return {
            "force_uncertainty": force_uncertainty,
            "downgrade_confidence": downgrade_confidence,
            "reason": "; ".join(reasons) if reasons else ("; ".join(downgrade_reasons) if downgrade_reasons else "Sufficient evidence for confident answer"),
            "downgrade_reasons": downgrade_reasons,
            "uncertainty_message": uncertainty_message,
            "confidence_downgrade": downgraded_confidence,
            "target_language": target_language,
            "is_crosslingual": is_crosslingual,
            "similarity_threshold_used": similarity_threshold
        }
    
    def _generate_uncertainty_message(
        self, 
        reasons: List[str], 
        num_chunks: int,
        target_language: str = "en"
    ) -> str:
        """
        Generate human-readable uncertainty message in target language.
        
        Args:
            reasons: List of reasons for uncertainty
            num_chunks: Number of chunks retrieved
            target_language: Target language code for the message
            
        Returns:
            Uncertainty message string in target language
        """
        from language_manager.multilingual_messages import get_message_generator
        msg_gen = get_message_generator()
        
        if num_chunks == 0:
            return msg_gen.get_no_answer_message(target_language)
        
        if "Low similarity" in " ".join(reasons):
            return msg_gen.get_low_similarity_message(target_language)
        
        if "Insufficient chunks" in " ".join(reasons):
            return msg_gen.get_insufficient_chunks_message(target_language)
        
        # Generic uncertainty message
        return msg_gen.get_uncertain_answer_message(target_language)
    
    def apply_uncertainty_response(
        self,
        original_answer: str,
        uncertainty_info: Dict[str, Any]
    ) -> str:
        """
        Apply uncertainty handling to answer.
        Only blocks/severe cases apply uncertainty message. Moderate cases preserve answer.
        
        Args:
            original_answer: Original generated answer
            uncertainty_info: Result from should_force_uncertainty()
            
        Returns:
            Modified answer with uncertainty handling (only for severe cases)
        """
        # DIAGNOSTIC LOG: Applying uncertainty response
        _diagnostic_logger.debug(f"Applying uncertainty response: force={uncertainty_info.get('force_uncertainty')}, downgrade={uncertainty_info.get('downgrade_confidence')}")
        
        # Only apply uncertainty message for severe cases (force_uncertainty)
        if not uncertainty_info.get("force_uncertainty"):
            # For moderate cases, just return original answer (confidence will be downgraded separately)
            _diagnostic_logger.debug("Answer preserved (moderate case - confidence downgrade only)")
            return original_answer
        
        uncertainty_message = uncertainty_info.get("uncertainty_message", "")
        
        # Change 1: Multilingual note (translate the note part)
        from language_manager.multilingual_messages import get_message_generator
        msg_gen = get_message_generator()
        # Get language from uncertainty_info if available, otherwise default to English
        target_lang = uncertainty_info.get("target_language", "en")
        note_text = msg_gen.get_message("uncertain_answer", target_lang).split(".")[0]  # Use first sentence as note
        
        # Prepend uncertainty message to answer (only for severe cases)
        result = f"{uncertainty_message}\n\n[Note: {note_text}]\n\n{original_answer}"
        _diagnostic_logger.debug("Uncertainty message applied (severe case)")
        return result
    
    def get_uncertainty_only_response(self, query: str, target_language: str = "en") -> str:
        """
        Get a response that only states uncertainty (no partial answer).
        
        Args:
            query: Original query
            target_language: Target language for the message
            
        Returns:
            Uncertainty-only response in target language
        """
        from language_manager.multilingual_messages import get_message_generator
        msg_gen = get_message_generator()
        return msg_gen.get_no_answer_message(target_language)

