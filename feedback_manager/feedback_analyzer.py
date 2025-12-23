"""
Feedback Analytics Engine - Phase 4
Analyzes feedback statistics to identify patterns and performance metrics.
Pure functional approach - no hidden state.
"""

import json
from typing import Dict, List, Optional, Any
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timedelta


class FeedbackAnalyzer:
    """
    Analyzes feedback data to extract insights for system optimization.
    All analysis is deterministic and explainable.
    """
    
    def __init__(self, feedback_file: str = "feedback_log.json"):
        """
        Initialize feedback analyzer.
        
        Args:
            feedback_file: Path to feedback log file (JSONL format)
        """
        self.feedback_file = feedback_file
    
    def load_feedback_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load feedback data from file.
        
        Args:
            limit: Optional limit on number of records to load
            
        Returns:
            List of feedback records
        """
        feedback_records = []
        
        if not Path(self.feedback_file).exists():
            return feedback_records
        
        try:
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if limit and line_num > limit:
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        record = json.loads(line)
                        feedback_records.append(record)
                    except json.JSONDecodeError:
                        print(f"⚠️ Skipping invalid JSON at line {line_num}")
                        continue
        
        except Exception as e:
            print(f"⚠️ Error loading feedback data: {e}")
        
        return feedback_records
    
    def get_statistics(self, days: Optional[int] = None) -> Dict[str, Any]:
        """
        Get aggregated feedback statistics.
        
        Args:
            days: Optional number of days to look back (None = all time)
            
        Returns:
            Dictionary with aggregated statistics
        """
        records = self.load_feedback_data()
        
        # Filter by date if specified
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            records = [
                r for r in records
                if datetime.fromisoformat(r.get("timestamp", "")).replace(tzinfo=None) >= cutoff_date
            ]
        
        if not records:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "by_intent": {},
                "by_engine": {},
                "by_translation_strategy": {},
                "by_confidence": {},
            }
        
        # Aggregate statistics
        total_rating = sum(r.get("rating", 0) for r in records)
        total_count = len(records)
        
        # Group by intent
        by_intent = defaultdict(lambda: {"total": 0, "sum_rating": 0, "ratings": []})
        by_engine = defaultdict(lambda: {"total": 0, "sum_rating": 0, "ratings": []})
        by_translation = defaultdict(lambda: {"total": 0, "sum_rating": 0, "ratings": []})
        by_confidence = defaultdict(lambda: {"total": 0, "sum_rating": 0, "ratings": []})
        
        for record in records:
            rating = record.get("rating", 0)
            metadata = record.get("metadata", {})
            
            # Intent statistics
            intent = metadata.get("intent") or "unknown"
            by_intent[intent]["total"] += 1
            by_intent[intent]["sum_rating"] += rating
            by_intent[intent]["ratings"].append(rating)
            
            # Engine statistics
            engine = metadata.get("engine") or "unknown"
            by_engine[engine]["total"] += 1
            by_engine[engine]["sum_rating"] += rating
            by_engine[engine]["ratings"].append(rating)
            
            # Translation strategy statistics
            translation = metadata.get("translation_strategy") or "unknown"
            by_translation[translation]["total"] += 1
            by_translation[translation]["sum_rating"] += rating
            by_translation[translation]["ratings"].append(rating)
            
            # Confidence statistics
            confidence = metadata.get("confidence") or "unknown"
            by_confidence[confidence]["total"] += 1
            by_confidence[confidence]["sum_rating"] += rating
            by_confidence[confidence]["ratings"].append(rating)
        
        # Compute averages and format results
        def format_stats(stats_dict):
            result = {}
            for key, data in stats_dict.items():
                avg = data["sum_rating"] / data["total"] if data["total"] > 0 else 0.0
                result[key] = {
                    "count": data["total"],
                    "average_rating": round(avg, 2),
                    "min_rating": min(data["ratings"]) if data["ratings"] else 0,
                    "max_rating": max(data["ratings"]) if data["ratings"] else 0,
                }
            return result
        
        return {
            "total_feedback": total_count,
            "average_rating": round(total_rating / total_count, 2) if total_count > 0 else 0.0,
            "by_intent": format_stats(by_intent),
            "by_engine": format_stats(by_engine),
            "by_translation_strategy": format_stats(by_translation),
            "by_confidence": format_stats(by_confidence),
            "date_range": {
                "from": records[0].get("timestamp") if records else None,
                "to": records[-1].get("timestamp") if records else None,
            }
        }
    
    def get_intent_performance(self, intent: str, days: Optional[int] = None) -> Dict[str, Any]:
        """
        Get performance statistics for a specific intent.
        
        Args:
            intent: Intent type to analyze
            days: Optional number of days to look back
            
        Returns:
            Performance statistics for the intent
        """
        stats = self.get_statistics(days=days)
        return stats.get("by_intent", {}).get(intent, {
            "count": 0,
            "average_rating": 0.0,
            "min_rating": 0,
            "max_rating": 0,
        })
    
    def get_engine_performance(self, engine: str, days: Optional[int] = None) -> Dict[str, Any]:
        """
        Get performance statistics for a specific engine.
        
        Args:
            engine: Engine name to analyze
            days: Optional number of days to look back
            
        Returns:
            Performance statistics for the engine
        """
        stats = self.get_statistics(days=days)
        return stats.get("by_engine", {}).get(engine, {
            "count": 0,
            "average_rating": 0.0,
            "min_rating": 0,
            "max_rating": 0,
        })
    
    def get_strategy_performance(
        self, 
        translation_strategy: str, 
        days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get performance statistics for a translation strategy.
        
        Args:
            translation_strategy: Strategy name ("none", "partial", "full")
            days: Optional number of days to look back
            
        Returns:
            Performance statistics for the strategy
        """
        stats = self.get_statistics(days=days)
        return stats.get("by_translation_strategy", {}).get(translation_strategy, {
            "count": 0,
            "average_rating": 0.0,
            "min_rating": 0,
            "max_rating": 0,
        })
    
    def identify_best_strategies(self, days: Optional[int] = None) -> Dict[str, str]:
        """
        Identify best-performing strategies based on feedback.
        
        Args:
            days: Optional number of days to look back
            
        Returns:
            Dictionary with best strategies by category
        """
        stats = self.get_statistics(days=days)
        
        def find_best(category_dict):
            """Find strategy with highest average rating (minimum 3 samples)."""
            best_key = None
            best_avg = 0.0
            
            for key, data in category_dict.items():
                if data["count"] >= 3 and data["average_rating"] > best_avg:
                    best_avg = data["average_rating"]
                    best_key = key
            
            return best_key
        
        return {
            "best_translation_strategy": find_best(stats.get("by_translation_strategy", {})),
            "best_engine_overall": find_best(stats.get("by_engine", {})),
        }
    
    def get_retrieval_depth_analysis(self, days: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze optimal retrieval depth based on feedback.
        
        Args:
            days: Optional number of days to look back
            
        Returns:
            Analysis of retrieval depth performance
        """
        records = self.load_feedback_data()
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            records = [
                r for r in records
                if datetime.fromisoformat(r.get("timestamp", "")).replace(tzinfo=None) >= cutoff_date
            ]
        
        # Group by number of chunks
        by_chunks = defaultdict(lambda: {"total": 0, "sum_rating": 0, "ratings": []})
        
        for record in records:
            num_chunks = record.get("metadata", {}).get("num_chunks", 0)
            rating = record.get("rating", 0)
            
            # Group into ranges
            if num_chunks == 0:
                chunk_range = "0"
            elif num_chunks <= 2:
                chunk_range = "1-2"
            elif num_chunks <= 5:
                chunk_range = "3-5"
            elif num_chunks <= 10:
                chunk_range = "6-10"
            else:
                chunk_range = "10+"
            
            by_chunks[chunk_range]["total"] += 1
            by_chunks[chunk_range]["sum_rating"] += rating
            by_chunks[chunk_range]["ratings"].append(rating)
        
        # Compute averages
        result = {}
        for chunk_range, data in by_chunks.items():
            avg = data["sum_rating"] / data["total"] if data["total"] > 0 else 0.0
            result[chunk_range] = {
                "count": data["total"],
                "average_rating": round(avg, 2),
            }
        
        # Find optimal range
        optimal_range = max(
            result.items(),
            key=lambda x: x[1]["average_rating"] if x[1]["count"] >= 3 else 0
        )[0] if result else None
        
        return {
            "by_chunk_count": result,
            "optimal_range": optimal_range,
        }

