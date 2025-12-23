"""
Policy Enforcer - Phase 5
Central entry point for safety and governance enforcement.
Ensures correct order of checks and prevents bypassing.
"""

from typing import Dict, Optional, Any, List
from .query_guard import QueryGuard, QuerySafetyDecision
from .output_guard import OutputGuard
from .uncertainty_handler import UncertaintyHandler
from .audit_logger import AuditLogger


class PolicyEnforcer:
    """
    Central policy enforcement for all safety checks.
    Ensures queries pass through all required safety layers.
    """
    
    def __init__(self, audit_file: str = "audit_log.jsonl"):
        """
        Initialize policy enforcer with all safety components.
        
        Args:
            audit_file: Path to audit log file
        """
        self.query_guard = QueryGuard()
        self.output_guard = OutputGuard()
        self.uncertainty_handler = UncertaintyHandler()
        self.audit_logger = AuditLogger(audit_file)
    
    def enforce_query_safety(self, query: str) -> Dict[str, Any]:
        """
        Enforce query safety checks (must be called before routing).
        
        Args:
            query: User query
            
        Returns:
            Dictionary with:
                - allowed: Boolean
                - sanitized_query: Cleaned query (if allowed)
                - reason: Explanation
                - warnings: List of warnings
        """
        # Validate query
        validation_result = self.query_guard.validate_query(query)
        
        # Convert QuerySafetyDecision enum to string for JSON serialization
        decision_value = validation_result["decision"].value if isinstance(validation_result["decision"], QuerySafetyDecision) else str(validation_result["decision"])
        
        # Create serializable validation result
        serializable_result = {
            "decision": decision_value,
            "allowed": validation_result.get("allowed", False),
            "sanitized_query": validation_result.get("sanitized_query"),
            "reason": validation_result.get("reason", ""),
            "warnings": validation_result.get("warnings", [])
        }
        
        # Log safety decision
        self.audit_logger.log_safety_decision(
            query=query,
            decision_type="query_guard",
            decision=serializable_result,
            outcome=decision_value
        )
        
        # Check if allowed
        allowed = validation_result["decision"] in [QuerySafetyDecision.ALLOW, QuerySafetyDecision.WARN]
        
        return {
            "allowed": allowed,
            "sanitized_query": validation_result.get("sanitized_query") if allowed else None,
            "reason": validation_result.get("reason", ""),
            "warnings": validation_result.get("warnings", []),
            "validation_result": validation_result
        }
    
    def enforce_output_safety(
        self,
        answer: str,
        retrieved_chunks: List[str],
        query: str,
        confidence: str,
        target_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Enforce output safety checks (must be called after answer generation).
        
        Args:
            answer: Generated answer
            retrieved_chunks: Retrieved document chunks
            query: Original query
            confidence: Confidence level
            
        Returns:
            Dictionary with:
                - is_valid: Boolean
                - validated_answer: Validated/cleaned answer
                - reason: Explanation
                - warnings: List of warnings
        """
        # Validate answer
        validation_result = self.output_guard.validate_answer(
            answer=answer,
            retrieved_chunks=retrieved_chunks,
            query=query,
            confidence=confidence,
            target_language=target_language  # Change 1: Pass language
        )
        
        # Log safety decision
        self.audit_logger.log_safety_decision(
            query=query,
            decision_type="output_guard",
            decision=validation_result,
            outcome="validated" if validation_result["is_valid"] else "rejected"
        )
        
        # Use fallback if invalid
        if not validation_result["is_valid"]:
            validated_answer = validation_result.get("fallback_answer") or self.output_guard.get_safe_fallback(query, target_language=target_language)
        else:
            validated_answer = answer
        
        return {
            "is_valid": validation_result["is_valid"],
            "validated_answer": validated_answer,
            "reason": validation_result.get("reason", ""),
            "warnings": validation_result.get("warnings", []),
            "validation_result": validation_result
        }
    
    def enforce_uncertainty_handling(
        self,
        answer: str,
        confidence: str,
        num_chunks: int,
        avg_similarity: Optional[float] = None,
        target_language: str = "en",
        query_intent: Optional[str] = None,
        document_language: Optional[str] = None,
        query_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enforce uncertainty handling (must be called before final response).
        Refined to downgrade confidence instead of blocking for moderate cases.
        
        Args:
            answer: Generated answer
            confidence: Confidence level
            num_chunks: Number of retrieved chunks
            avg_similarity: Average similarity score
            target_language: Target language for messages
            query_intent: Intent of the query (e.g., "summarization")
            document_language: Document language code
            query_language: Query language code
            
        Returns:
            Dictionary with:
                - final_answer: Answer with uncertainty handling applied (only for severe cases)
                - uncertainty_applied: Boolean (True only for severe cases)
                - confidence_downgraded: Boolean (True for moderate cases)
                - final_confidence: Confidence level after downgrade (if applicable)
                - uncertainty_message: Uncertainty message (if applied)
        """
        # Check if uncertainty should be forced or confidence downgraded
        uncertainty_result = self.uncertainty_handler.should_force_uncertainty(
            confidence=confidence,
            num_chunks=num_chunks,
            avg_similarity=avg_similarity,
            answer=answer,
            target_language=target_language,
            query_intent=query_intent,
            document_language=document_language,
            query_language=query_language
        )
        
        # Apply uncertainty handling (only for severe cases)
        if uncertainty_result.get("force_uncertainty"):
            final_answer = self.uncertainty_handler.apply_uncertainty_response(
                original_answer=answer,
                uncertainty_info=uncertainty_result
            )
        else:
            # Moderate cases: preserve answer, confidence will be downgraded
            final_answer = answer
        
        # Apply confidence downgrade if needed
        final_confidence = confidence
        if uncertainty_result.get("downgrade_confidence") and uncertainty_result.get("confidence_downgrade"):
            final_confidence = uncertainty_result["confidence_downgrade"]
        
        # Convert uncertainty_result to JSON-serializable format for logging
        serializable_result = {
            "force_uncertainty": uncertainty_result.get("force_uncertainty", False),
            "downgrade_confidence": uncertainty_result.get("downgrade_confidence", False),
            "reason": uncertainty_result.get("reason", ""),
            "downgrade_reasons": uncertainty_result.get("downgrade_reasons", []),
            "confidence_downgrade": uncertainty_result.get("confidence_downgrade"),
            "is_crosslingual": uncertainty_result.get("is_crosslingual", False),
            "similarity_threshold_used": uncertainty_result.get("similarity_threshold_used")
        }
        
        return {
            "final_answer": final_answer,
            "uncertainty_applied": uncertainty_result.get("force_uncertainty", False),
            "confidence_downgraded": uncertainty_result.get("downgrade_confidence", False),
            "final_confidence": final_confidence,
            "uncertainty_message": uncertainty_result.get("uncertainty_message"),
            "uncertainty_result": serializable_result
        }
    
    def audit_query_execution(
        self,
        query: str,
        result: Dict[str, Any],
        safety_decisions: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None
    ) -> bool:
        """
        Audit log a complete query execution.
        
        Args:
            query: User query
            result: Result dictionary
            safety_decisions: Safety decision metadata
            execution_time_ms: Execution time
            
        Returns:
            True if logging succeeded
        """
        return self.audit_logger.log_query_execution(
            query=query,
            result=result,
            safety_decisions=safety_decisions,
            execution_time_ms=execution_time_ms
        )
    
    def enforce_full_pipeline(
        self,
        query: str,
        answer: str,
        retrieved_chunks: List[str],
        confidence: str,
        num_chunks: int,
        avg_similarity: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Enforce all safety checks in correct order (convenience method).
        
        Args:
            query: User query
            answer: Generated answer
            retrieved_chunks: Retrieved chunks
            confidence: Confidence level
            num_chunks: Number of chunks
            avg_similarity: Average similarity
            
        Returns:
            Dictionary with final validated answer and safety metadata
        """
        # Step 1: Query safety (should already be done, but double-check)
        query_safety = self.enforce_query_safety(query)
        if not query_safety["allowed"]:
            return {
                "final_answer": f"Query rejected: {query_safety['reason']}",
                "query_rejected": True,
                "safety_metadata": {"query_safety": query_safety}
            }
        
        # Step 2: Output safety
        output_safety = self.enforce_output_safety(
            answer=answer,
            retrieved_chunks=retrieved_chunks,
            query=query,
            confidence=confidence
        )
        
        # Step 3: Uncertainty handling
        uncertainty_result = self.enforce_uncertainty_handling(
            answer=output_safety["validated_answer"],
            confidence=confidence,
            num_chunks=num_chunks,
            avg_similarity=avg_similarity
        )
        
        return {
            "final_answer": uncertainty_result["final_answer"],
            "query_rejected": False,
            "safety_metadata": {
                "query_safety": query_safety,
                "output_safety": output_safety,
                "uncertainty_handling": uncertainty_result
            }
        }

