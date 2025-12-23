# def handle_metadata_query(pages, query):
#     full_text = " ".join(pages)

#     if "how many pages" in query.lower():
#         return f"The document contains {len(pages)} pages."

#     if "how many words" in query.lower():
#         words = len(full_text.split())
#         return f"The document contains approximately {words} words."

#     return "Metadata information could not be determined."


'''CLAUDE'''

"""
Metadata Engine Module
Handles queries about document properties programmatically without LLM.
"""

from typing import List, Optional, Dict
import re
from datetime import datetime


class MetadataEngine:
    """
    Answers document property questions using precomputed statistics.
    No vector search or LLM usage - purely programmatic.
    """
    
    def __init__(self):
        self.metadata_cache = {}
    
    def compute_metadata(self, pages: List[str], document_info: Optional[Dict] = None) -> Dict:
        """
        Precompute all document metadata.
        
        Args:
            pages: List of page texts
            document_info: Optional additional document information
            
        Returns:
            Dict containing all metadata
        """
        full_text = " ".join(pages)
        
        metadata = {
            "page_count": len(pages),
            "word_count": len(full_text.split()),
            "character_count": len(full_text),
            "paragraph_count": sum(text.count('\n\n') + 1 for text in pages),
            "line_count": sum(text.count('\n') + 1 for text in pages),
        }
        
        # Add document info if provided
        if document_info:
            metadata.update(document_info)
        
        return metadata
    
    def process(self, query: str, pages: List[str], document_info: Optional[Dict] = None) -> Optional[str]:
        """
        Process metadata queries and return answers.
        
        Args:
            query: User query
            pages: Document pages
            document_info: Optional document information (title, author, date, etc.)
            
        Returns:
            Answer string or None if query cannot be handled
        """
        query_lower = query.lower()
        metadata = self.compute_metadata(pages, document_info)
        
        # Page count queries
        if any(phrase in query_lower for phrase in ["how many pages", "page count", "number of pages", "total pages"]):
            return f"The document has {metadata['page_count']} pages."
        
        # Word count queries
        if any(phrase in query_lower for phrase in ["word count", "how many words", "number of words"]):
            return f"The document contains approximately {metadata['word_count']:,} words."
        
        # Character count queries
        if any(phrase in query_lower for phrase in ["character count", "how many characters", "length in characters"]):
            return f"The document contains {metadata['character_count']:,} characters."
        
        # Document length queries (general)
        if any(phrase in query_lower for phrase in ["how long", "length of document", "document length"]):
            return (f"The document is {metadata['page_count']} pages long "
                   f"with approximately {metadata['word_count']:,} words.")
        
        # Title queries
        if "title" in query_lower and document_info and "title" in document_info:
            return f"The document title is: {document_info['title']}"
        
        # Author queries (only for document file metadata)
        # Require explicit "this document" context to avoid matching content queries
        if any(phrase in query_lower for phrase in ["author of this document", "who wrote this document", 
                                                   "author of the document", "who created this document"]):
            if document_info and "author" in document_info:
                authors = document_info['author']
                if isinstance(authors, list):
                    return f"The document author(s): {', '.join(authors)}"
                return f"The document author is: {authors}"
            return "The author information is not available in the document metadata."
        
        # Publication/creation date queries (only for document file metadata)
        # Require explicit "this document" context to avoid matching content queries
        if any(phrase in query_lower for phrase in ["when was this document", "publication date of this document", 
                                                   "created date of this document", "date this document was published",
                                                   "date this document was created"]):
            if document_info and "date" in document_info:
                return f"The document was published/created on: {document_info['date']}"
            return "The publication date is not available in the document metadata."
        
        # Generic "publication date" without context might be asking about content
        # Return None to allow fallthrough to content-based answering
        
        # Document type queries
        if any(phrase in query_lower for phrase in ["type of document", "document type", "what kind of document"]):
            if document_info and "type" in document_info:
                return f"This is a {document_info['type']}."
            return "The document type is not specified."
        
        # Language queries
        if "language" in query_lower:
            if document_info and "language" in document_info:
                return f"The document is written in {document_info['language']}."
            return "The document language information is not available."
        
        return None