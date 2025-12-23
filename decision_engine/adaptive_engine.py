"""
Adaptive Decision Engine - Phase 2 + Phase 4
Decides translation & retrieval strategy dynamically.
Now supports feedback-informed optimization.
"""

from typing import Dict, Optional, Any


class AdaptiveDecisionEngine:
    """
    Adaptive Decision Engine (Phase 2 + Phase 4)
    Decides translation & retrieval strategy dynamically.
    Can accept feedback-optimized parameters for learning.
    """

    def decide(
        self,
        doc_lang: str,
        query_lang: str,
        num_pages: int,
        optimized_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Decide translation and retrieval strategy.
        
        Args:
            doc_lang: Document language code
            query_lang: Query language code
            num_pages: Number of pages in document
            optimized_params: Optional feedback-optimized parameters (Phase 4)
                Expected keys:
                    - preferred_translation_strategy: Preferred strategy from feedback
                    - retrieval_depth: Optimal retrieval depth (top_k)
        
        Returns:
            Dictionary with decision details
        """
        decision = {}
        
        # Phase 4: Check if we have feedback-optimized strategy preference
        preferred_strategy = None
        if optimized_params and optimized_params.get("preferred_translation_strategy"):
            preferred_strategy = optimized_params["preferred_translation_strategy"]
        
        # Rule 1: Same language → no translation (highest priority)
        if doc_lang == query_lang:
            decision["translation_strategy"] = "none"
            decision["strategy_reason"] = "Document and query are in the same language"
        
        # Rule 2: Use feedback-optimized strategy if available and valid
        elif preferred_strategy and self._is_valid_strategy_for_context(
            preferred_strategy, doc_lang, query_lang, num_pages
        ):
            decision["translation_strategy"] = preferred_strategy
            decision["strategy_reason"] = f"Using feedback-optimized strategy: {preferred_strategy}"
            decision["feedback_informed"] = True
        
        # Rule 3: Large document → partial translation
        elif num_pages > 5:
            decision["translation_strategy"] = "partial"
            decision["strategy_reason"] = f"Large document ({num_pages} pages) - using partial translation"
        
        # Rule 4: Default → full translation
        else:
            decision["translation_strategy"] = "full"
            decision["strategy_reason"] = "Default strategy for medium-sized documents"
        
        decision["retrieval_strategy"] = "semantic"
        
        # Phase 4: Include optimized retrieval depth if available
        if optimized_params and optimized_params.get("retrieval_depth"):
            decision["retrieval_depth"] = optimized_params["retrieval_depth"]
            decision["retrieval_depth_reason"] = "Feedback-optimized retrieval depth"
        else:
            decision["retrieval_depth"] = 5  # Default
            decision["retrieval_depth_reason"] = "Default retrieval depth"
        
        return decision
    
    def _is_valid_strategy_for_context(
        self,
        strategy: str,
        doc_lang: str,
        query_lang: str,
        num_pages: int
    ) -> bool:
        """
        Check if a strategy is valid for the given context.
        
        Args:
            strategy: Strategy to validate
            doc_lang: Document language
            query_lang: Query language
            num_pages: Number of pages
            
        Returns:
            True if strategy is valid for context
        """
        # "none" strategy only valid if languages match
        if strategy == "none":
            return doc_lang == query_lang
        
        # "partial" and "full" are always valid if languages differ
        return doc_lang != query_lang
