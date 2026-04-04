"""
Enhanced Answer Generator with FAISS Integration
Generates grounded answers using LLM with semantic search context
"""

from typing import List, Dict, Union, Optional
from utils.llm_client import chat_completion
from utils.language_utils import get_language_name


def generate_answer(
    context_chunks: Union[List[str], List[Dict]], 
    query: str,
    include_citations: bool = True,
    temperature: float = 0.0,
    answer_language: Optional[str] = None
) -> str:
    """
    Uses LLM to generate an answer STRICTLY from provided context.
    Now supports both simple chunks and FAISS results with metadata.
    
    Args:
        context_chunks: Either:
            - List of strings (backward compatible)
            - List of dicts with {'chunk': str, 'metadata': dict, 'score': float}
        query: User's question
        include_citations: Whether to include page references in answer
        temperature: LLM temperature (0.0 for deterministic)
    
    Returns:
        Generated answer string
    """

    if not context_chunks:
        # Use multilingual message generator
        from language_manager.multilingual_messages import get_message_generator
        msg_gen = get_message_generator()
        output_lang = answer_language or "en"
        return msg_gen.get_no_answer_message(output_lang)

    # Detect format and normalize
    chunks_with_metadata = _normalize_chunks(context_chunks)
    
    # Format context with metadata for better grounding
    # Change 2: Remove technical terms from context formatting
    context_text = _format_context_with_metadata(chunks_with_metadata, include_citations, remove_technical=True)

    # Change 2: Explicit language instruction and remove technical terms
    print(f"Answer language: {answer_language}")
    output_lang = answer_language or "en"
    print(f"Output language: {output_lang}")
    lang_name = get_language_name(output_lang)
    
    system_prompt = (
        f"You are a document-based assistant. You MUST answer the question in {lang_name} ({output_lang}).\n"
        "Answer the question ONLY using the provided document sections.\n"
        "If the answer is not explicitly present in the document, say that the information is not available.\n"
        "Do NOT use outside knowledge.\n"
        "IMPORTANT: Do NOT use technical terms like 'chunks', 'embeddings', 'similarity scores', 'retrieval', or 'FAISS' in your answer.\n"
        "Use natural, user-friendly language that a non-technical person would understand.\n"
    )
    
    if include_citations:
        system_prompt += (
            f"\nWhen referencing information, mention which page it comes from "
            f"(e.g., 'According to page 3, ...' in {lang_name})."
        )

    user_prompt = f"""
Document Sections:
{context_text}

Question:
{query}

Please answer the question in {lang_name} ({output_lang}) using only the information from the document sections above.
"""

    try:
        response = chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating answer: {e}")
        return f"Error generating answer: {str(e)}"


def _normalize_chunks(chunks: Union[List[str], List[Dict]]) -> List[Dict]:
    """
    Normalize chunks to standard format with metadata.
    
    Args:
        chunks: Either list of strings or list of dicts
        
    Returns:
        List of dicts with 'chunk', 'metadata', and 'score'
    """
    normalized = []
    
    for i, item in enumerate(chunks):
        if isinstance(item, str):
            # Old format: just strings
            normalized.append({
                'chunk': item,
                'metadata': {'chunk_id': i},
                'score': None
            })
        elif isinstance(item, dict):
            # New format: FAISS results
            normalized.append({
                'chunk': item.get('chunk', item.get('text', str(item))),
                'metadata': item.get('metadata', {'chunk_id': i}),
                'score': item.get('score')
            })
        else:
            # Fallback
            normalized.append({
                'chunk': str(item),
                'metadata': {'chunk_id': i},
                'score': None
            })
    
    return normalized


def _format_context_with_metadata(
    chunks_with_metadata: List[Dict], 
    include_citations: bool,
    remove_technical: bool = True
) -> str:
    """
    Format chunks with metadata for LLM context.
    
    Args:
        chunks_with_metadata: Normalized chunks with metadata
        include_citations: Whether to include page info
        remove_technical: If True, use user-friendly terms instead of technical ones
        
    Returns:
        Formatted context string
    """
    context_parts = []
    
    for i, item in enumerate(chunks_with_metadata, 1):
        chunk_text = item['chunk']
        metadata = item['metadata']
        score = item['score']
        
        # Build header with metadata
        # Change 2: Use user-friendly terms instead of technical ones
        if remove_technical:
            header = f"--- Section {i}"
            if include_citations and 'page' in metadata:
                header += f" [Page {metadata['page']}]"
            header += " ---"
        else:
            header = f"--- Chunk {i}"
            if include_citations and 'page' in metadata:
                header += f" [Page {metadata['page']}]"
            if score is not None:
                # Convert L2 distance to similarity percentage
                similarity = 1 / (1 + score)
                header += f" (Relevance: {similarity:.1%})"
            header += " ---"
        
        context_parts.append(f"{header}\n{chunk_text}\n")
    
    return "\n".join(context_parts)


def generate_answer_with_confidence(
    context_chunks: Union[List[str], List[Dict]], 
    query: str,
    include_citations: bool = True
) -> Dict[str, any]:
    """
    Generate answer and compute confidence based on FAISS scores.
    
    Args:
        context_chunks: Chunks with or without metadata
        query: User question
        include_citations: Include page references
        
    Returns:
        Dict with 'answer', 'confidence', and 'metrics'
    """
    if not context_chunks:
        return {
            "answer": "Answer not found in the document.",
            "confidence": "Low",
            "metrics": {
                "num_chunks": 0,
                "avg_similarity": 0.0
            }
        }
    
    # Normalize chunks
    chunks_with_metadata = _normalize_chunks(context_chunks)
    
    # Generate answer
    answer = generate_answer(context_chunks, query, include_citations)
    
    # Compute confidence from FAISS scores
    scores = [c['score'] for c in chunks_with_metadata if c['score'] is not None]
    
    if scores:
        # Convert L2 distances to similarities
        similarities = [1 / (1 + s) for s in scores]
        avg_similarity = sum(similarities) / len(similarities)
        
        # Determine confidence level
        if avg_similarity > 0.85:
            confidence = "High"
        elif avg_similarity > 0.70:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        metrics = {
            "num_chunks": len(chunks_with_metadata),
            "avg_similarity": avg_similarity,
            "min_similarity": min(similarities),
            "max_similarity": max(similarities)
        }
    else:
        # Fallback if no scores available
        confidence = "Medium" if len(chunks_with_metadata) >= 3 else "Low"
        metrics = {
            "num_chunks": len(chunks_with_metadata),
            "avg_similarity": None
        }
    
    return {
        "answer": answer,
        "confidence": confidence,
        "metrics": metrics
    }


def generate_answer_streaming(
    context_chunks: Union[List[str], List[Dict]], 
    query: str,
    include_citations: bool = True
):
    """
    Stream the answer generation for better UX.
    
    Args:
        context_chunks: Chunks with or without metadata
        query: User question
        include_citations: Include page references
        
    Yields:
        Chunks of the generated answer
    """
    if not context_chunks:
        yield "Answer not found in the document."
        return

    chunks_with_metadata = _normalize_chunks(context_chunks)
    context_text = _format_context_with_metadata(chunks_with_metadata, include_citations)

    system_prompt = (
        "You are a document-based assistant.\n"
        "Answer the question ONLY using the provided document chunks.\n"
        "If the answer is not explicitly present, say:\n"
        "'Answer not found in the document.'\n"
        "Do NOT use outside knowledge.\n"
    )
    
    if include_citations:
        system_prompt += (
            "\nWhen referencing information, mention which page it comes from "
            "(e.g., 'According to page 3, ...')."
        )

    user_prompt = f"""
Document Chunks:
{context_text}

Question:
{query}
"""

    try:
        stream = chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        yield f"Error generating answer: {str(e)}"


# Backward compatibility: Keep old function signature working
def generate_simple_answer(context_chunks: List[str], query: str) -> str:
    """
    Simplified version for backward compatibility.
    Just takes list of strings.
    """
    return generate_answer(context_chunks, query, include_citations=False)


# Example usage and testing
if __name__ == "__main__":
    # Test with simple chunks (old format)
    simple_chunks = [
        "Machine learning is a subset of AI.",
        "Deep learning uses neural networks.",
        "Python is popular for ML."
    ]
    
    print("="*60)
    print("Test 1: Simple chunks (backward compatible)")
    print("="*60)
    answer1 = generate_answer(simple_chunks, "What is machine learning?")
    print(f"Answer: {answer1}\n")
    
    # Test with FAISS results (new format)
    faiss_chunks = [
        {
            'chunk': "Machine learning is a subset of AI that enables systems to learn.",
            'metadata': {'page': 1, 'chunk_index': 0},
            'score': 0.15  # Low L2 distance = high similarity
        },
        {
            'chunk': "Deep learning uses neural networks with multiple layers.",
            'metadata': {'page': 2, 'chunk_index': 1},
            'score': 0.45  # Higher distance = lower similarity
        },
        {
            'chunk': "Python is the most popular language for ML development.",
            'metadata': {'page': 3, 'chunk_index': 2},
            'score': 0.80
        }
    ]
    
    print("="*60)
    print("Test 2: FAISS chunks with metadata")
    print("="*60)
    result = generate_answer_with_confidence(
        faiss_chunks, 
        "What is machine learning?",
        include_citations=True
    )
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Metrics: {result['metrics']}\n")
    
    print("="*60)
    print("Test 3: Streaming answer")
    print("="*60)
    print("Streaming: ", end="", flush=True)
    for chunk in generate_answer_streaming(faiss_chunks, "Explain deep learning"):
        print(chunk, end="", flush=True)
    print("\n")