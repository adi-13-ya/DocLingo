"""
Feedback Collection Layer - Phase 4
Collects and persists user feedback with rich metadata for system learning.
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path


class FeedbackLogger:
    """
    Enhanced feedback logger that captures rich metadata for system learning.
    All feedback is deterministic and auditable.
    """
    
    def __init__(self, feedback_file: str = "feedback_log.json"):
        """
        Initialize feedback logger.
        
        Args:
            feedback_file: Path to JSON file for storing feedback
        """
        self.feedback_file = feedback_file
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Ensure the directory for feedback file exists."""
        file_path = Path(self.feedback_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_feedback(
        self,
        rating: int,
        query: str,
        answer: str,
        metadata: Dict[str, Any],
        feedback_file: Optional[str] = None
    ) -> bool:
        """
        Log user feedback with comprehensive metadata.
        
        Args:
            rating: User rating (1-10 scale)
            query: Original user query
            answer: Generated answer
            metadata: Rich metadata including:
                - intent: Query intent classification
                - engine: Engine used
                - tier: Tier (TIER 1/2/3)
                - translation_strategy: Translation strategy used
                - num_chunks: Number of chunks retrieved
                - confidence: Confidence score
                - retrieval_method: Retrieval method
                - avg_similarity_score: Average FAISS similarity (if applicable)
                - query_language: Query language code
                - document_language: Document language code
            feedback_file: Optional override for feedback file path
            
        Returns:
            True if logging succeeded, False otherwise
        """
        # Validate rating
        if not isinstance(rating, int) or rating < 1 or rating > 10:
            print(f"⚠️ Invalid rating: {rating}. Must be integer between 1-10.")
            return False
        
        # Prepare feedback record
        feedback_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "rating": rating,
            "query": query,
            "answer": answer,
            "metadata": metadata
        }
        
        # Use provided file or default
        file_path = feedback_file or self.feedback_file
        
        try:
            # Append to JSONL file (one JSON object per line)
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(feedback_data, ensure_ascii=False) + "\n")
            
            return True
        
        except Exception as e:
            print(f"⚠️ Feedback logging failed: {e}")
            return False
    
    def log_feedback_from_result(
        self,
        rating: int,
        query: str,
        result: Dict[str, Any],
        feedback_file: Optional[str] = None
    ) -> bool:
        """
        Convenience method to log feedback from a result dictionary.
        
        Args:
            rating: User rating (1-10)
            query: Original query
            result: Result dictionary from run_doclingo()
            feedback_file: Optional override for feedback file path
            
        Returns:
            True if logging succeeded
        """
        # Extract metadata from result
        metadata = {
            "intent": result.get("query_intent"),
            "engine": result.get("routing_used"),
            "translation_strategy": result.get("decision_used", {}).get("translation_strategy") if isinstance(result.get("decision_used"), dict) else None,
            "num_chunks": result.get("num_chunks_used", 0),
            "confidence": result.get("confidence"),
            "retrieval_method": result.get("retrieval_method"),
            "avg_similarity_score": result.get("avg_similarity_score"),
            "query_language": result.get("query_language"),
            "document_language": result.get("document_language"),
        }
        
        return self.log_feedback(
            rating=rating,
            query=query,
            answer=result.get("answer", ""),
            metadata=metadata,
            feedback_file=feedback_file
        )


# Backward compatibility function
def log_feedback(feedback_data: Dict[str, Any], file_path: str = "feedback_log.json"):
    """
    Legacy function for backward compatibility.
    Logs feedback data dictionary directly.
    
    Args:
        feedback_data: Dictionary containing feedback information
        file_path: Path to feedback log file
    """
    logger = FeedbackLogger(feedback_file=file_path)
    
    # Extract rating and other data
    rating = feedback_data.get("rating", 0)
    query = feedback_data.get("query", "")
    answer = feedback_data.get("answer", "")
    metadata = {k: v for k, v in feedback_data.items() 
                if k not in ["rating", "query", "answer", "timestamp"]}
    
    logger.log_feedback(
        rating=rating,
        query=query,
        answer=answer,
        metadata=metadata,
        feedback_file=file_path
    )
