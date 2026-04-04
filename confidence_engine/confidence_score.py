"""
Confidence Score Computation - Enhanced with Grounding Score
Integrates grounding penalties into confidence calculation.
Uses token-level overlap with normalization for multilingual support.
"""

import re
from typing import List, Optional, Dict, Any


def normalize_text(text: str) -> List[str]:
    """
    Normalize text for token-level comparison.
    Lowercases, removes punctuation, and splits into tokens.
    
    Args:
        text: Input text
        
    Returns:
        List of normalized tokens
    """
    if not text:
        return []
    
    # Lowercase
    text = text.lower()
    
    # Remove punctuation and special characters (keep alphanumeric and spaces)
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Split into tokens (words)
    tokens = re.findall(r'\b\w+\b', text)
    
    # Filter out very short tokens (less than 2 characters)
    tokens = [t for t in tokens if len(t) >= 2]
    
    return tokens


def compute_grounding_score(
    answer: str,
    retrieved_chunks: List[str],
    document_language: Optional[str] = None,
    answer_language: Optional[str] = None
) -> float:
    """
    Compute grounding score using token-level overlap with normalization.
    Multilingual-aware: uses lenient thresholds for cross-lingual cases.
    
    Args:
        answer: Generated answer text
        retrieved_chunks: List of retrieved document chunks
        document_language: Document language code (e.g., "en", "te", "hi")
        answer_language: Answer language code (e.g., "en", "te", "hi")
        
    Returns:
        Grounding score (0.0 to 1.0)
    """
    if not answer or not retrieved_chunks:
        return 0.0
    
    # Detect cross-lingual scenario
    is_crosslingual = (
        document_language and 
        answer_language and 
        document_language != answer_language
    )
    
    # Normalize answer tokens
    answer_tokens = normalize_text(answer)
    
    if not answer_tokens:
        # If no tokens after normalization, return low score
        return 0.1 if len(answer.strip()) > 20 else 0.0
    
    # Normalize all chunk tokens
    all_chunk_tokens = set()
    for chunk in retrieved_chunks:
        chunk_tokens = normalize_text(chunk)
        all_chunk_tokens.update(chunk_tokens)
    
    if not all_chunk_tokens:
        # If chunks have no tokens (e.g., non-text content), use lenient score
        return 0.5 if len(answer.strip()) > 20 else 0.3
    
    # Calculate token overlap
    answer_token_set = set(answer_tokens)
    overlap_tokens = answer_token_set & all_chunk_tokens
    
    # Calculate overlap ratio
    total_answer_tokens = len(answer_token_set)
    if total_answer_tokens == 0:
        return 0.0
    
    overlap_ratio = len(overlap_tokens) / total_answer_tokens
    
    # For cross-lingual cases, apply lenient scoring
    # (exact token matching doesn't work across languages)
    if is_crosslingual:
        # For cross-lingual, if we have any overlap or substantial answer, give moderate score
        if overlap_ratio > 0.1 or len(answer.strip()) > 50:
            return min(0.6, overlap_ratio * 2.0)  # Boost cross-lingual scores
        else:
            return 0.3  # Minimum for cross-lingual with some content
    
    # For same-language, use direct overlap ratio
    return min(overlap_ratio, 1.0)


def apply_grounding_penalty(
    base_confidence: str,
    grounding_score: float,
    is_crosslingual: bool = False
) -> str:
    """
    Apply grounding penalty to confidence level.
    Low grounding downgrades confidence: High -> Medium -> Low
    
    Args:
        base_confidence: Base confidence level ("High", "Medium", "Low")
        grounding_score: Grounding score (0.0 to 1.0)
        is_crosslingual: Whether this is a cross-lingual scenario
        
    Returns:
        Adjusted confidence level
    """
    # Multilingual-aware thresholds (more lenient for cross-lingual)
    if is_crosslingual:
        high_threshold = 0.3  # Lower threshold for cross-lingual
        medium_threshold = 0.15
    else:
        high_threshold = 0.5  # Standard threshold for same language
        medium_threshold = 0.3
    
    # Apply penalty based on grounding score
    if grounding_score < medium_threshold:
        # Very low grounding: downgrade by 2 levels
        if base_confidence == "High":
            return "Low"
        elif base_confidence == "Medium":
            return "Low"
        else:
            return "Low"  # Already low
    elif grounding_score < high_threshold:
        # Moderate grounding: downgrade by 1 level
        if base_confidence == "High":
            return "Medium"
        elif base_confidence == "Medium":
            return "Low"
        else:
            return "Low"  # Already low
    else:
        # Good grounding: keep base confidence
        return base_confidence


def compute_confidence(
    num_chunks: int,
    translation_strategy: str,
    grounding_score: Optional[float] = None,
    document_language: Optional[str] = None,
    answer_language: Optional[str] = None
) -> Dict[str, Any]:
    """
    Compute confidence with grounding score integration.
    
    Args:
        num_chunks: Number of retrieved chunks
        translation_strategy: Translation strategy ("none", "partial", "full")
        grounding_score: Optional grounding score (0.0 to 1.0)
        document_language: Document language code
        answer_language: Answer language code
        
    Returns:
        Dictionary with:
            - confidence: Confidence level ("High", "Medium", "Low")
            - base_confidence: Base confidence before grounding penalty
            - grounding_score: Grounding score used
            - grounding_penalty_applied: Boolean
    """
    score = 0.0
    
    # Base scoring from chunks and translation
    if num_chunks >= 3:
        score += 0.5
    elif num_chunks == 2:
        score += 0.3
    elif num_chunks == 1:
        score += 0.15
    
    if translation_strategy == "none":
        score += 0.3
    elif translation_strategy == "partial":
        score += 0.2
    elif translation_strategy == "full":
        score += 0.1
    
    # Determine base confidence
    if score >= 0.7:
        base_confidence = "High"
    elif score >= 0.4:
        base_confidence = "Medium"
    else:
        base_confidence = "Low"
    
    # Apply grounding penalty if grounding score provided
    is_crosslingual = (
        document_language and 
        answer_language and 
        document_language != answer_language
    )
    
    if grounding_score is not None:
        final_confidence = apply_grounding_penalty(
            base_confidence=base_confidence,
            grounding_score=grounding_score,
            is_crosslingual=is_crosslingual
        )
        grounding_penalty_applied = (final_confidence != base_confidence)
    else:
        final_confidence = base_confidence
        grounding_penalty_applied = False
    
    return {
        "confidence": final_confidence,
        "base_confidence": base_confidence,
        "grounding_score": grounding_score,
        "grounding_penalty_applied": grounding_penalty_applied,
        "is_crosslingual": is_crosslingual
    }
