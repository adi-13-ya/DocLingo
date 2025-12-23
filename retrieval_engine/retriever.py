"""
Enhanced Retriever with FAISS Integration
Handles semantic search and document retrieval for DocLingo
"""

from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from vector_store import EmbeddingManager, FAISSIndex


class FAISSRetriever:
    """
    Semantic document retriever using FAISS vector search.
    Replaces simple keyword-based retrieval with AI-powered semantic search.
    """
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 embedding_model: str = "text-embedding-3-small",
                 index_type: str = "flat"):
        """
        Initialize the retriever with FAISS and OpenAI embeddings.
        
        Args:
            openai_api_key: OpenAI API key
            embedding_model: OpenAI embedding model to use
            index_type: FAISS index type ("flat", "ivf", "hnsw")
        """
        self.embedding_manager = EmbeddingManager(
            api_key=openai_api_key,
            model=embedding_model
        )
        
        self.faiss_index = FAISSIndex(
            dimension=self.embedding_manager.get_dimension(),
            index_type=index_type
        )
        
        self.is_indexed = False
    
    def index_document(self, chunks: List[str], metadata: Optional[List[Dict]] = None):
        """
        Index a document's chunks for semantic search.
        
        Args:
            chunks: List of text chunks from the document
            metadata: Optional metadata for each chunk (page numbers, positions, etc.)
        
        Example metadata:
            [
                {"page": 1, "position": "top", "doc_id": "doc123"},
                {"page": 1, "position": "middle", "doc_id": "doc123"},
                ...
            ]
        """
        if not chunks:
            print("No chunks to index")
            return
        
        print(f"Indexing {len(chunks)} chunks...")
        
        # Generate embeddings for all chunks
        embeddings = self.embedding_manager.embed_batch(chunks)
        
        # Add to FAISS index
        self.faiss_index.add_documents(chunks, embeddings, metadata)
        
        self.is_indexed = True
        print(f"✓ Document indexed successfully")
    
    def retrieve(self, 
                query: str, 
                k: int = 5,
                score_threshold: Optional[float] = None,
                filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Retrieve most relevant chunks for a query.
        
        Args:
            query: User's question
            k: Number of chunks to retrieve
            score_threshold: Minimum similarity score (lower L2 = more similar)
            filter_metadata: Optional filters (e.g., {"page": 3} to search only page 3)
        
        Returns:
            List of relevant chunks with scores and metadata
        """
        if not self.is_indexed:
            print("Warning: No documents indexed yet")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_manager.embed_text(query)
        
        # Search in FAISS
        results = self.faiss_index.search(
            query_embedding, 
            k=k * 2 if filter_metadata else k,  # Get more if filtering
            score_threshold=score_threshold
        )
        
        # Apply metadata filters if specified
        if filter_metadata:
            results = [
                r for r in results 
                if all(r['metadata'].get(k) == v for k, v in filter_metadata.items())
            ][:k]
        
        return results
    
    def retrieve_with_context(self,
                             query: str,
                             k: int = 3,
                             context_window: int = 1) -> str:
        """
        Retrieve chunks and format them with context for LLM.
        
        Args:
            query: User's question
            k: Number of chunks to retrieve
            context_window: Number of surrounding chunks to include
        
        Returns:
            Formatted context string ready for LLM
        """
        results = self.retrieve(query, k=k)
        
        if not results:
            return "No relevant information found in the document."
        
        # Format results for LLM
        context_parts = []
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            chunk_text = result['chunk']
            
            # Add metadata info
            meta_str = f"[Page {metadata.get('page', 'N/A')}]"
            
            context_parts.append(
                f"--- Relevant Section {i} {meta_str} ---\n{chunk_text}\n"
            )
        
        return "\n".join(context_parts)
    
    def clear_index(self):
        """Clear the current index"""
        self.faiss_index.delete_all()
        self.is_indexed = False
        print("Index cleared")
    
    def save_index(self, filepath: str):
        """Save index to disk for later use"""
        self.faiss_index.save(filepath)
    
    def load_index(self, filepath: str):
        """Load previously saved index"""
        self.faiss_index.load(filepath)
        self.is_indexed = True
    
    def get_stats(self) -> Dict:
        """Get retriever statistics"""
        return {
            "indexed": self.is_indexed,
            "embedding_model": self.embedding_manager.model,
            "embedding_dimension": self.embedding_manager.dimension,
            **self.faiss_index.get_stats()
        }


# Example usage and testing
if __name__ == "__main__":
    import os
    
    # Initialize retriever
    retriever = FAISSRetriever(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        embedding_model="text-embedding-3-small",
        index_type="flat"
    )
    
    # Sample document chunks
    sample_chunks = [
        "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
        "Deep learning uses neural networks with multiple layers to process data.",
        "Natural language processing enables computers to understand human language.",
        "Computer vision allows machines to interpret and understand visual information.",
        "Reinforcement learning involves agents learning through trial and error."
    ]
    
    sample_metadata = [
        {"page": 1, "section": "Introduction"},
        {"page": 2, "section": "Deep Learning"},
        {"page": 3, "section": "NLP"},
        {"page": 4, "section": "Computer Vision"},
        {"page": 5, "section": "Reinforcement Learning"}
    ]
    
    # Index the document
    retriever.index_document(sample_chunks, sample_metadata)
    
    # Test retrieval
    query = "How do neural networks work?"
    print(f"\nQuery: {query}")
    print("-" * 60)
    
    results = retriever.retrieve(query, k=3)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.4f} (lower = more similar)")
        print(f"   Page: {result['metadata']['page']}")
        print(f"   Content: {result['chunk']}")
    
    # Test formatted context
    print("\n" + "="*60)
    print("FORMATTED CONTEXT FOR LLM:")
    print("="*60)
    context = retriever.retrieve_with_context(query, k=2)
    print(context)
    
    # Print stats
    print("\n" + "="*60)
    print("RETRIEVER STATS:")
    print("="*60)
    print(retriever.get_stats())