"""
Audit Logger - Phase 5
Comprehensive logging of all query executions for auditability and traceability.
"""

import json
from datetime import datetime
from typing import Dict, Optional, Any, List
from pathlib import Path


class AuditLogger:
    """
    Logs all query executions with comprehensive metadata.
    All logs are deterministic, human-readable, and machine-parseable.
    """
    
    def __init__(self, audit_file: str = "audit_log.jsonl"):
        """
        Initialize audit logger.
        
        Args:
            audit_file: Path to audit log file (JSONL format)
        """
        self.audit_file = audit_file
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Ensure the directory for audit file exists."""
        file_path = Path(self.audit_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_query_execution(
        self,
        query: str,
        result: Dict[str, Any],
        safety_decisions: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None
    ) -> bool:
        """
        Log a complete query execution.
        
        Args:
            query: User query
            result: Result dictionary from run_doclingo()
            safety_decisions: Optional safety decision metadata
            execution_time_ms: Optional execution time in milliseconds
            
        Returns:
            True if logging succeeded
        """
        # Extract metadata from result
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "query_intent": result.get("query_intent"),
            "document_language": result.get("document_language"),
            "query_language": result.get("query_language"),
            "engine_used": result.get("routing_used"),
            "retrieval_method": result.get("retrieval_method"),
            "num_chunks_retrieved": result.get("num_chunks_used", 0),
            "translation_strategy": result.get("decision_used", {}).get("translation_strategy") if isinstance(result.get("decision_used"), dict) else None,
            "confidence_score": result.get("confidence"),
            "base_confidence": result.get("base_confidence"),
            "answer_length": len(result.get("answer", "")),
            "avg_similarity_score": result.get("avg_similarity_score"),
            "execution_time_ms": execution_time_ms,
            "safety_decisions": safety_decisions or {},
            "optimization_applied": result.get("optimization_applied", False),
        }
        
        try:
            # Append to JSONL file
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
            
            return True
        
        except Exception as e:
            print(f"⚠️ Audit logging failed: {e}")
            return False
    
    def log_safety_decision(
        self,
        query: str,
        decision_type: str,
        decision: Dict[str, Any],
        outcome: str
    ) -> bool:
        """
        Log a safety decision (query guard, output guard, etc.).
        Ensures all objects are JSON serializable.
        
        Args:
            query: User query
            decision_type: Type of decision ("query_guard", "output_guard", "uncertainty_handler")
            decision: Decision dictionary (will be converted to JSON-serializable format)
            outcome: Outcome ("allowed", "denied", "modified")
            
        Returns:
            True if logging succeeded
        """
        # Convert decision to JSON-serializable format
        serializable_decision = self._make_serializable(decision)
        
        safety_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "decision_type": decision_type,
            "decision": serializable_decision,
            "outcome": outcome
        }
        
        try:
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(safety_entry, ensure_ascii=False, default=str) + "\n")
            
            return True
        
        except Exception as e:
            print(f"⚠️ Safety decision logging failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _make_serializable(self, obj: Any) -> Any:
        """
        Convert an object to JSON-serializable format.
        Handles enums, custom objects, and nested structures.
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON-serializable representation
        """
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._make_serializable(item) for item in obj)
        elif hasattr(obj, '__dict__'):
            # Custom object - convert to dict
            return self._make_serializable(obj.__dict__)
        elif hasattr(obj, 'value'):
            # Enum object
            return obj.value
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # Fallback: convert to string
            return str(obj)
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent audit logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of audit log entries
        """
        logs = []
        
        if not Path(self.audit_file).exists():
            return logs
        
        try:
            with open(self.audit_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
                # Get last N lines
                for line in lines[-limit:]:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        log_entry = json.loads(line)
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            print(f"⚠️ Error reading audit logs: {e}")
        
        return logs
    
    def search_logs(
        self,
        query_text: Optional[str] = None,
        intent: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search audit logs by criteria.
        
        Args:
            query_text: Search for queries containing this text
            intent: Filter by intent type
            date_from: Filter from date (ISO format)
            date_to: Filter to date (ISO format)
            
        Returns:
            List of matching audit log entries
        """
        all_logs = self.get_recent_logs(limit=10000)  # Get large sample
        filtered = []
        
        for log in all_logs:
            # Query text filter
            if query_text and query_text.lower() not in log.get("query", "").lower():
                continue
            
            # Intent filter
            if intent and log.get("query_intent") != intent:
                continue
            
            # Date filters
            timestamp = log.get("timestamp", "")
            if date_from and timestamp < date_from:
                continue
            if date_to and timestamp > date_to:
                continue
            
            filtered.append(log)
        
        return filtered

