"""
Query Guard - Phase 5
Validates and sanitizes user queries, detects prompt injection attempts.
All checks are deterministic and explainable.
"""

import re
from typing import Dict, Optional, Tuple
from enum import Enum


class QuerySafetyDecision(Enum):
    """Safety decision types"""
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"  # Allow but flag for review


class QueryGuard:
    """
    Validates user queries for safety and security.
    Detects prompt injection, manipulation attempts, and malformed queries.
    All detection is rule-based and deterministic.
    """
    
    def __init__(self):
        """Initialize query guard with detection patterns."""
        # Prompt injection patterns (common attack vectors)
        self.injection_patterns = [
            r'ignore\s+(previous|above|all)\s+(instructions|rules|prompts?)',
            r'forget\s+(previous|above|all)\s+(instructions|rules|prompts?)',
            r'disregard\s+(previous|above|all)\s+(instructions|rules|prompts?)',
            r'you\s+are\s+(now|a)\s+[^.]*',
            r'act\s+as\s+[^.]*',
            r'pretend\s+to\s+be\s+[^.]*',
            r'system\s*:\s*[^.]*',
            r'###\s*(instruction|system|prompt)\s*:',
            r'<\|(system|prompt|instruction)\|>',
            r'\[INST\]',
            r'\[SYSTEM\]',
            r'override\s+(safety|security|rules)',
            r'bypass\s+(safety|security|rules)',
            r'ignore\s+safety',
            r'you\s+must\s+(always|never|only)',
            r'your\s+(goal|objective|purpose)\s+is',
            r'new\s+(instructions|rules|prompt)',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.injection_patterns]
        
        # Maximum query length (prevent DoS)
        self.max_query_length = 5000
        
        # Minimum query length (prevent empty/malformed)
        self.min_query_length = 3
    
    def validate_query(self, query: str) -> Dict[str, any]:
        """
        Validate a user query for safety and security.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with:
                - decision: QuerySafetyDecision enum
                - reason: Explanation string
                - sanitized_query: Cleaned query (if allowed)
                - warnings: List of warning messages
        """
        warnings = []
        
        # Check 1: Empty or too short
        if not query or not isinstance(query, str):
            return {
                "decision": QuerySafetyDecision.DENY,
                "reason": "Query is empty or invalid type",
                "sanitized_query": None,
                "warnings": []
            }
        
        query = query.strip()
        
        if len(query) < self.min_query_length:
            return {
                "decision": QuerySafetyDecision.DENY,
                "reason": f"Query too short (minimum {self.min_query_length} characters)",
                "sanitized_query": None,
                "warnings": []
            }
        
        # Check 2: Too long (potential DoS)
        if len(query) > self.max_query_length:
            return {
                "decision": QuerySafetyDecision.DENY,
                "reason": f"Query too long (maximum {self.max_query_length} characters)",
                "sanitized_query": None,
                "warnings": []
            }
        
        # Check 3: Prompt injection detection
        injection_detected = False
        matched_patterns = []
        
        for pattern in self.compiled_patterns:
            if pattern.search(query):
                injection_detected = True
                matched_patterns.append(pattern.pattern)
        
        if injection_detected:
            return {
                "decision": QuerySafetyDecision.DENY,
                "reason": f"Potential prompt injection detected. Matched patterns: {', '.join(matched_patterns[:3])}",
                "sanitized_query": None,
                "warnings": []
            }
        
        # Check 4: Suspicious patterns (warn but allow)
        suspicious_patterns = [
            r'[<>\[\]{}]{3,}',  # Multiple brackets (potential encoding)
            r'%[0-9a-fA-F]{2}',  # URL encoding
            r'\\x[0-9a-fA-F]{2}',  # Hex encoding
            r'javascript:',  # Script injection
            r'<script',  # HTML script tags
        ]
        
        for pattern_str in suspicious_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            if pattern.search(query):
                warnings.append(f"Suspicious pattern detected: {pattern_str}")
        
        # Sanitize query (remove control characters, normalize whitespace)
        sanitized = self._sanitize_query(query)
        
        # Final decision
        if warnings:
            decision = QuerySafetyDecision.WARN
            reason = "Query allowed but contains suspicious patterns"
        else:
            decision = QuerySafetyDecision.ALLOW
            reason = "Query passed all safety checks"
        
        return {
            "decision": decision,
            "reason": reason,
            "sanitized_query": sanitized,
            "warnings": warnings
        }
    
    def _sanitize_query(self, query: str) -> str:
        """
        Sanitize query by removing control characters and normalizing whitespace.
        
        Args:
            query: Original query
            
        Returns:
            Sanitized query
        """
        # Remove control characters (except newline, tab, carriage return)
        sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', query)
        
        # Normalize whitespace (multiple spaces to single space)
        sanitized = re.sub(r' +', ' ', sanitized)
        
        # Remove leading/trailing whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    def is_safe(self, query: str) -> bool:
        """
        Quick check if query is safe (returns boolean).
        
        Args:
            query: User query
            
        Returns:
            True if query is safe, False otherwise
        """
        result = self.validate_query(query)
        return result["decision"] in [QuerySafetyDecision.ALLOW, QuerySafetyDecision.WARN]


class QueryValidator:
    """
    Simple validator interface for backward compatibility.
    """
    
    @staticmethod
    def validate(query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate query and return (is_valid, error_message).
        
        Args:
            query: User query
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        guard = QueryGuard()
        result = guard.validate_query(query)
        
        if result["decision"] == QuerySafetyDecision.DENY:
            return False, result["reason"]
        
        return True, None

