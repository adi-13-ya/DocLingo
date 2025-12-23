"""
Document Chunker Module
Handles intelligent text chunking for document processing.
"""

from typing import List
import re


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Split text into chunks with overlap, trying to break at sentence boundaries.
    
    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk (in characters)
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # Validate parameters
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    
    if chunk_overlap < 0:
        chunk_overlap = 0
    
    if chunk_overlap >= chunk_size:
        # Overlap can't be larger than chunk size
        chunk_overlap = chunk_size // 2
    
    chunks = []
    text_length = len(text)
    start = 0
    
    while start < text_length:
        # Calculate end position
        end = start + chunk_size
        
        # If this is not the last chunk, try to break at a sentence boundary
        if end < text_length:
            # Look for sentence endings within the last 20% of the chunk
            search_start = max(start, end - (chunk_size // 5))
            chunk_text_segment = text[search_start:end]
            
            # Find sentence boundaries (., !, ? followed by space or newline)
            sentence_endings = list(re.finditer(r'[.!?]\s+', chunk_text_segment))
            
            if sentence_endings:
                # Use the last sentence ending found
                last_match = sentence_endings[-1]
                # Adjust end to the actual sentence boundary
                end = search_start + last_match.end()
        
        # Extract chunk
        chunk = text[start:end].strip()
        
        # Only add non-empty chunks
        if chunk:
            chunks.append(chunk)
        
        # Move start position forward (accounting for overlap)
        start = end - chunk_overlap
        
        # Prevent infinite loop
        if start <= 0:
            start = end
    
    return chunks


def chunk_text_simple(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Simple character-based chunking without sentence boundary detection.
    Faster but less intelligent than chunk_text.
    
    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk (in characters)
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # Validate parameters
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    
    if chunk_overlap < 0:
        chunk_overlap = 0
    
    if chunk_overlap >= chunk_size:
        chunk_overlap = chunk_size // 2
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        
        if chunk:
            chunks.append(chunk)
        
        # Move start position forward (accounting for overlap)
        start += chunk_size - chunk_overlap
        
        # Prevent infinite loop
        if start >= text_length:
            break
    
    return chunks


def chunk_by_paragraphs(text: str, max_chunk_size: int = 500) -> List[str]:
    """
    Chunk text by paragraphs, combining small paragraphs and splitting large ones.
    
    Args:
        text: The text to chunk
        max_chunk_size: Maximum size of each chunk (in characters)
        
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # Split by paragraph boundaries (double newlines)
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        para_size = len(para)
        
        # If paragraph fits, add it to current chunk
        if current_size + para_size <= max_chunk_size:
            current_chunk.append(para)
            current_size += para_size
        else:
            # Save current chunk if it has content
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            
            # If paragraph is too large, split it
            if para_size > max_chunk_size:
                # Split large paragraph using chunk_text
                sub_chunks = chunk_text(para, max_chunk_size, 0)
                chunks.extend(sub_chunks)
                current_chunk = []
                current_size = 0
            else:
                # Start new chunk with this paragraph
                current_chunk = [para]
                current_size = para_size
    
    # Add remaining chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

