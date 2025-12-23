"""
Adaptive Strategy Optimizer - Phase 4
Optimizes system parameters based on feedback history.
Pure functional, deterministic, and explainable.
"""

from typing import Dict, Optional, Any
from feedback_manager.feedback_analyzer import FeedbackAnalyzer


class StrategyOptimizer:
    """
    Optimizes system strategies based on feedback analysis.
    All optimizations are rule-based and explainable.
    """
    
    def __init__(self, feedback_file: str = "feedback_log.json"):
        """
        Initialize strategy optimizer.
        
        Args:
            feedback_file: Path to feedback log file
        """
        self.analyzer = FeedbackAnalyzer(feedback_file)
    
    def get_optimized_parameters(
        self,
        intent: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get optimized parameters based on feedback history.
        
        Args:
            intent: Optional intent type for intent-specific optimization
            days: Number of days of feedback to consider
            
        Returns:
            Dictionary with optimized parameters and explanations
        """
        stats = self.analyzer.get_statistics(days=days)
        best_strategies = self.analyzer.identify_best_strategies(days=days)
        retrieval_analysis = self.analyzer.get_retrieval_depth_analysis(days=days)
        
        # Default parameters
        optimized = {
            "retrieval_depth": 5,  # Default top_k
            "preferred_translation_strategy": None,
            "confidence_adjustment": 0.0,
            "explanation": "Using default parameters (insufficient feedback data)",
            "feedback_samples": stats.get("total_feedback", 0),
        }
        
        # Only optimize if we have sufficient feedback
        if stats["total_feedback"] < 5:
            return optimized
        
        # Optimize retrieval depth
        optimal_range = retrieval_analysis.get("optimal_range")
        if optimal_range:
            range_map = {
                "1-2": 2,
                "3-5": 5,
                "6-10": 7,
                "10+": 10,
            }
            optimized["retrieval_depth"] = range_map.get(optimal_range, 5)
            optimized["explanation"] = f"Optimized based on {stats['total_feedback']} feedback samples. Optimal retrieval depth: {optimal_range} chunks."
        
        # Optimize translation strategy preference
        best_translation = best_strategies.get("best_translation_strategy")
        if best_translation and stats.get("by_translation_strategy", {}).get(best_translation, {}).get("count", 0) >= 3:
            optimized["preferred_translation_strategy"] = best_translation
            avg_rating = stats["by_translation_strategy"][best_translation]["average_rating"]
            optimized["explanation"] += f" Preferred translation strategy: {best_translation} (avg rating: {avg_rating:.1f})"
        
        # Intent-specific optimization
        if intent:
            intent_perf = self.analyzer.get_intent_performance(intent, days=days)
            if intent_perf.get("count", 0) >= 3:
                avg_rating = intent_perf.get("average_rating", 0)
                
                # Adjust confidence based on intent performance
                if avg_rating >= 8.0:
                    optimized["confidence_adjustment"] = 0.1  # Boost confidence
                elif avg_rating <= 5.0:
                    optimized["confidence_adjustment"] = -0.1  # Reduce confidence
                
                optimized["explanation"] += f" Intent '{intent}' performance: {avg_rating:.1f}/10 (n={intent_perf['count']})"
        
        return optimized
    
    def get_optimal_retrieval_depth(
        self,
        intent: Optional[str] = None,
        days: int = 30
    ) -> int:
        """
        Get optimal retrieval depth (top_k) based on feedback.
        
        Args:
            intent: Optional intent for intent-specific optimization
            days: Number of days of feedback to consider
            
        Returns:
            Optimal number of chunks to retrieve (default: 5)
        """
        params = self.get_optimized_parameters(intent=intent, days=days)
        return params.get("retrieval_depth", 5)
    
    def should_prefer_translation_strategy(
        self,
        strategy: str,
        days: int = 30
    ) -> bool:
        """
        Check if a translation strategy should be preferred based on feedback.
        
        Args:
            strategy: Translation strategy to check
            days: Number of days of feedback to consider
            
        Returns:
            True if strategy should be preferred
        """
        best_strategies = self.analyzer.identify_best_strategies(days=days)
        preferred = best_strategies.get("best_translation_strategy")
        
        if not preferred:
            return False
        
        # Check if this strategy is significantly better than others
        stats = self.analyzer.get_statistics(days=days)
        this_perf = self.analyzer.get_strategy_performance(strategy, days=days)
        preferred_perf = self.analyzer.get_strategy_performance(preferred, days=days)
        
        if this_perf["count"] < 3:
            return False
        
        # Prefer if average rating is within 0.5 of the best, or if it's the best
        return (strategy == preferred or 
                abs(this_perf["average_rating"] - preferred_perf["average_rating"]) <= 0.5)
    
    def get_parameter_explanation(
        self,
        intent: Optional[str] = None,
        days: int = 30
    ) -> str:
        """
        Get human-readable explanation of why parameters were chosen.
        
        Args:
            intent: Optional intent type
            days: Number of days of feedback to consider
            
        Returns:
            Explanation string
        """
        params = self.get_optimized_parameters(intent=intent, days=days)
        return params.get("explanation", "Using default parameters")

