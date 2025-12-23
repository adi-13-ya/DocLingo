"""
Aggregate Engine Module
Handles counting and frequency queries using pattern matching.
"""

from typing import List, Optional
import re


class AggregateEngine:
    """
    Handles counting, enumeration, and frequency queries.
    Uses regex and structural analysis without hallucination.
    """
    
    def __init__(self):
        self.section_patterns = [
            r'(?:^|\n)(?:chapter|section|part)\s+\d+',
            r'(?:^|\n)\d+\.\s+[A-Z]',
            r'(?:^|\n)#{1,3}\s+',
        ]
    
    def process(self, query: str, pages: List[str]) -> Optional[str]:
        """
        Process aggregate queries and return counts.
        
        Args:
            query: User query
            pages: Document pages
            
        Returns:
            Answer string or None if query cannot be handled
        """
        query_lower = query.lower()
        full_text = " ".join(pages)
        
        # Section/Chapter counting
        if self._is_section_count_query(query_lower):
            count = self._count_sections(full_text)
            return f"The document contains approximately {count} sections/chapters."
        
        # Table counting
        if any(phrase in query_lower for phrase in ["how many tables", "count tables", "number of tables"]):
            count = self._count_tables(full_text)
            return f"The document contains approximately {count} tables."
        
        # Figure/Image counting
        if any(phrase in query_lower for phrase in ["how many figures", "how many images", 
                                                     "count figures", "number of figures"]):
            count = self._count_figures(full_text)
            return f"The document contains approximately {count} figures/images."
        
        # Reference/Citation counting
        if any(phrase in query_lower for phrase in ["how many references", "how many citations",
                                                     "number of references", "count citations"]):
            count = self._count_references(full_text)
            return f"The document contains approximately {count} references/citations."
        
        # Mention counting (specific term)
        mention_match = re.search(r'how many times.*"([^"]+)"', query_lower)
        if not mention_match:
            mention_match = re.search(r'count.*"([^"]+)"', query_lower)
        if not mention_match:
            mention_match = re.search(r'occurrences? of.*"([^"]+)"', query_lower)
        
        if mention_match:
            term = mention_match.group(1)
            count = self._count_mentions(full_text, term)
            return f'The term "{term}" appears {count} times in the document.'
        
        # List all occurrences
        if "list all" in query_lower:
            # Extract what to list
            list_match = re.search(r'list all\s+(.+?)(?:\s+in|\s+from|$)', query_lower)
            if list_match:
                item_type = list_match.group(1).strip()
                items = self._list_items(full_text, item_type)
                if items:
                    return f"Found {len(items)} {item_type}:\n" + "\n".join(f"- {item}" for item in items[:20])
                return f"No {item_type} found in the document."
        
        return None
    
    def _is_section_count_query(self, query: str) -> bool:
        """Check if query asks for section/chapter count"""
        keywords = ["how many sections", "how many chapters", "count sections",
                   "count chapters", "number of sections", "number of chapters"]
        return any(kw in query for kw in keywords)
    
    def _count_sections(self, text: str) -> int:
        """Count sections using multiple heuristics"""
        counts = []
        for pattern in self.section_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            counts.append(len(matches))
        
        # Return the maximum count found
        return max(counts) if counts else 0
    
    def _count_tables(self, text: str) -> int:
        """Count table references"""
        patterns = [
            r'\btable\s+\d+',
            r'\btab\.\s+\d+',
        ]
        
        matches = set()
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches.update(found)
        
        return len(matches)
    
    def _count_figures(self, text: str) -> int:
        """Count figure/image references"""
        patterns = [
            r'\bfigure\s+\d+',
            r'\bfig\.\s+\d+',
            r'\bimage\s+\d+',
        ]
        
        matches = set()
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches.update(found)
        
        return len(matches)
    
    def _count_references(self, text: str) -> int:
        """Count references/citations"""
        patterns = [
            r'\[\d+\]',  # [1], [2], etc.
            r'\(\d{4}\)',  # (2023), (2024), etc.
            r'\b[A-Z][a-z]+\s+et\s+al\.',  # Author et al.
        ]
        
        matches = set()
        for pattern in patterns:
            found = re.findall(pattern, text)
            matches.update(found)
        
        return len(matches)
    
    def _count_mentions(self, text: str, term: str) -> int:
        """Count mentions of a specific term (case-insensitive)"""
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        return len(pattern.findall(text))
    
    def _list_items(self, text: str, item_type: str) -> List[str]:
        """List all items of a specific type"""
        items = []
        
        if "date" in item_type:
            # Find date patterns
            date_patterns = [
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            ]
            for pattern in date_patterns:
                items.extend(re.findall(pattern, text, re.IGNORECASE))
        
        elif "email" in item_type:
            # Find email addresses
            pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            items = re.findall(pattern, text)
        
        elif "url" in item_type or "link" in item_type:
            # Find URLs
            pattern = r'https?://[^\s<>"]+'
            items = re.findall(pattern, text)
        
        elif "phone" in item_type or "number" in item_type:
            # Find phone numbers
            pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            items = re.findall(pattern, text)
        
        return list(set(items))