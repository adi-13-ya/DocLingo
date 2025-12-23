"""
Analytical Engine Module
Handles derived and computational queries programmatically.
"""

from typing import List, Optional, Dict
import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser


class AnalyticalEngine:
    """
    Handles queries requiring computation or reasoning.
    Performs calculations programmatically, LLM only phrases results.
    """
    
    def __init__(self):
        pass
    
    def process(self, query: str, pages: List[str], document_info: Optional[Dict] = None) -> Optional[str]:
        """
        Process analytical queries requiring computation.
        
        Args:
            query: User query
            pages: Document pages
            document_info: Optional document metadata
            
        Returns:
            Answer string or None if query cannot be handled
        """
        query_lower = query.lower()
        full_text = " ".join(pages)
        
        # Document age calculation
        if any(phrase in query_lower for phrase in ["how old", "age of document", "published how long ago"]):
            result = self._calculate_document_age(document_info)
            if result:
                return result
        
        # Time span/duration analysis
        if any(phrase in query_lower for phrase in ["time span", "duration", "period covered", "time range"]):
            result = self._analyze_time_span(full_text)
            if result:
                return result
        
        # Percentage calculations
        if "percentage" in query_lower or "percent" in query_lower:
            result = self._calculate_percentages(full_text, query_lower)
            if result:
                return result
        
        # Average/mean calculations
        if any(phrase in query_lower for phrase in ["average", "mean", "typical"]):
            result = self._calculate_averages(full_text, query_lower)
            if result:
                return result
        
        # Growth/change analysis
        if any(phrase in query_lower for phrase in ["growth rate", "change over time", "increase", "decrease"]):
            result = self._analyze_growth(full_text)
            if result:
                return result
        
        # Trend analysis
        if any(phrase in query_lower for phrase in ["trend", "pattern", "trajectory"]):
            result = self._analyze_trends(full_text)
            if result:
                return result
        
        return None
    
    def _calculate_document_age(self, document_info: Optional[Dict]) -> Optional[str]:
        """Calculate how old the document is"""
        if not document_info or "date" not in document_info:
            return None
        
        try:
            doc_date = date_parser.parse(document_info["date"])
            today = datetime.now()
            age = today - doc_date
            
            years = age.days // 365
            months = (age.days % 365) // 30
            
            if years > 0:
                return f"The document is approximately {years} year(s) and {months} month(s) old."
            elif months > 0:
                return f"The document is approximately {months} month(s) old."
            else:
                return f"The document is approximately {age.days} day(s) old."
        except:
            return None
    
    def _analyze_time_span(self, text: str) -> Optional[str]:
        """Analyze time span covered in document"""
        # Find all years mentioned
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        if not years:
            return None
        
        years = [int(y) for y in years]
        min_year = min(years)
        max_year = max(years)
        span = max_year - min_year
        
        if span > 0:
            return f"The document covers a time span from {min_year} to {max_year}, approximately {span} years."
        else:
            return f"The document primarily focuses on the year {min_year}."
    
    def _calculate_percentages(self, text: str, query: str) -> Optional[str]:
        """Extract and analyze percentages"""
        # Find all percentages in text
        percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
        if not percentages:
            return None
        
        percentages = [float(p) for p in percentages]
        
        if "highest" in query or "maximum" in query:
            return f"The highest percentage mentioned in the document is {max(percentages)}%."
        elif "lowest" in query or "minimum" in query:
            return f"The lowest percentage mentioned in the document is {min(percentages)}%."
        elif "average" in query:
            avg = sum(percentages) / len(percentages)
            return f"The average percentage across all mentions is {avg:.2f}%."
        else:
            return f"The document mentions {len(percentages)} percentages ranging from {min(percentages)}% to {max(percentages)}%."
    
    def _calculate_averages(self, text: str, query: str) -> Optional[str]:
        """Calculate averages from numerical data"""
        # This is a simplified implementation
        # In production, you'd want more sophisticated extraction
        
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        if not numbers or len(numbers) < 2:
            return None
        
        numbers = [float(n) for n in numbers if float(n) < 1000000]  # Filter outliers
        
        if numbers:
            avg = sum(numbers) / len(numbers)
            return f"Based on numerical values in the document, the average is approximately {avg:.2f}."
        
        return None
    
    def _analyze_growth(self, text: str) -> Optional[str]:
        """Analyze growth patterns"""
        # Look for growth-related patterns
        growth_patterns = [
            r'increased?\s+by\s+(\d+(?:\.\d+)?)\s*%',
            r'decreased?\s+by\s+(\d+(?:\.\d+)?)\s*%',
            r'growth\s+of\s+(\d+(?:\.\d+)?)\s*%',
        ]
        
        growth_values = []
        for pattern in growth_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            growth_values.extend([float(m) for m in matches])
        
        if growth_values:
            avg_growth = sum(growth_values) / len(growth_values)
            return f"The document mentions growth/change rates averaging {avg_growth:.2f}% across {len(growth_values)} instances."
        
        return None
    
    def _analyze_trends(self, text: str) -> Optional[str]:
        """Identify trends in the document"""
        # Look for trend keywords
        positive_trends = len(re.findall(r'\b(increasing|rising|growing|upward|improvement)\b', text, re.IGNORECASE))
        negative_trends = len(re.findall(r'\b(decreasing|declining|falling|downward|deterioration)\b', text, re.IGNORECASE))
        stable_trends = len(re.findall(r'\b(stable|steady|constant|unchanged|flat)\b', text, re.IGNORECASE))
        
        total = positive_trends + negative_trends + stable_trends
        if total == 0:
            return None
        
        result = "Trend analysis: "
        if positive_trends > max(negative_trends, stable_trends):
            result += f"The document predominantly discusses positive/upward trends ({positive_trends} mentions)."
        elif negative_trends > max(positive_trends, stable_trends):
            result += f"The document predominantly discusses negative/downward trends ({negative_trends} mentions)."
        else:
            result += f"The document discusses mixed trends: {positive_trends} positive, {negative_trends} negative, {stable_trends} stable mentions."
        
        return result