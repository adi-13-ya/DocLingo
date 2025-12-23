"""
Feedback-Aware Confidence Calibration - Phase 4
Calibrates confidence scores based on historical user feedback.
Deterministic and explainable calibration.
"""

from typing import Dict, Optional
from feedback_manager.feedback_analyzer import FeedbackAnalyzer


class ConfidenceCalibrator:
    """
    Calibrates confidence scores using historical feedback data.
    All calibration is rule-based and explainable.
    """
    
    def __init__(self, feedback_file: str = "feedback_log.json"):
        """
        Initialize confidence calibrator.
        
        Args:
            feedback_file: Path to feedback log file
        """
        self.analyzer = FeedbackAnalyzer(feedback_file)
    
    def calibrate_confidence(
        self,
        base_confidence: str,
        intent: Optional[str] = None,
        engine: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, any]:
        """
        Calibrate confidence score based on feedback history.
        
        Args:
            base_confidence: Base confidence level ("High", "Medium", "Low")
            intent: Optional intent type for intent-specific calibration
            engine: Optional engine name for engine-specific calibration
            days: Number of days of feedback to consider
            
        Returns:
            Dictionary with calibrated confidence and explanation
        """
        # Confidence level to numeric mapping
        confidence_map = {"High": 3, "Medium": 2, "Low": 1}
        base_level = confidence_map.get(base_confidence, 2)
        
        # Get feedback statistics
        stats = self.analyzer.get_statistics(days=days)
        
        # Default: return base confidence with no adjustment
        result = {
            "calibrated_confidence": base_confidence,
            "adjustment": 0,
            "explanation": f"Using base confidence: {base_confidence}",
            "feedback_based": False,
        }
        
        # Need sufficient feedback to calibrate
        if stats["total_feedback"] < 10:
            return result
        
        adjustment = 0
        explanations = []
        
        # Intent-based calibration
        if intent:
            intent_perf = self.analyzer.get_intent_performance(intent, days=days)
            if intent_perf.get("count", 0) >= 5:
                avg_rating = intent_perf.get("average_rating", 0)
                
                if avg_rating >= 8.5:
                    adjustment += 1
                    explanations.append(f"Intent '{intent}' has excellent feedback ({avg_rating:.1f}/10)")
                elif avg_rating <= 5.0:
                    adjustment -= 1
                    explanations.append(f"Intent '{intent}' has poor feedback ({avg_rating:.1f}/10)")
        
        # Engine-based calibration
        if engine:
            engine_perf = self.analyzer.get_engine_performance(engine, days=days)
            if engine_perf.get("count", 0) >= 5:
                avg_rating = engine_perf.get("average_rating", 0)
                
                if avg_rating >= 8.5:
                    adjustment += 1
                    explanations.append(f"Engine '{engine}' performs well ({avg_rating:.1f}/10)")
                elif avg_rating <= 5.0:
                    adjustment -= 1
                    explanations.append(f"Engine '{engine}' performs poorly ({avg_rating:.1f}/10)")
        
        # Confidence-level based calibration
        confidence_perf = stats.get("by_confidence", {}).get(base_confidence, {})
        if confidence_perf.get("count", 0) >= 5:
            avg_rating = confidence_perf.get("average_rating", 0)
            
            # If high confidence queries are rated low, reduce confidence
            if base_confidence == "High" and avg_rating < 6.0:
                adjustment -= 1
                explanations.append(f"'High' confidence queries underperformed ({avg_rating:.1f}/10)")
            # If low confidence queries are rated high, increase confidence
            elif base_confidence == "Low" and avg_rating > 7.5:
                adjustment += 1
                explanations.append(f"'Low' confidence queries overperformed ({avg_rating:.1f}/10)")
        
        # Apply adjustment (clamp between Low and High)
        new_level = max(1, min(3, base_level + adjustment))
        
        # Map back to confidence string
        reverse_map = {3: "High", 2: "Medium", 1: "Low"}
        calibrated = reverse_map.get(new_level, base_confidence)
        
        result["calibrated_confidence"] = calibrated
        result["adjustment"] = adjustment
        result["feedback_based"] = len(explanations) > 0
        
        if explanations:
            result["explanation"] = f"Calibrated from {base_confidence} to {calibrated}. " + " ".join(explanations)
        else:
            result["explanation"] = f"Using base confidence: {base_confidence} (insufficient feedback for calibration)"
        
        return result
    
    def get_confidence_with_feedback_info(
        self,
        base_confidence: str,
        intent: Optional[str] = None,
        engine: Optional[str] = None,
        days: int = 30
    ) -> str:
        """
        Get confidence string with optional feedback-based information.
        
        Args:
            base_confidence: Base confidence level
            intent: Optional intent type
            engine: Optional engine name
            days: Number of days of feedback to consider
            
        Returns:
            Confidence string, optionally with feedback info
        """
        calibrated = self.calibrate_confidence(base_confidence, intent, engine, days)
        
        if calibrated["feedback_based"]:
            # Include feedback info in confidence string
            return f"{calibrated['calibrated_confidence']} (calibrated based on user feedback)"
        else:
            return calibrated["calibrated_confidence"]

