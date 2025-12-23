"""
FAISS Index Manager for DocLingo
Handles vector storage, indexing, and similarity search
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path


class FAISSIndex:
    """Manages FAISS vector index for efficient similarity search"""
    
    def __init__(self, dimension: int = 1536, index_type: str = "flat"):
        """
        Initialize FAISS index.
        
        Args:
            dimension: Embedding vector dimension (1536 for text-embedding-3-small)
            index_type: Type of FAISS index
                - "flat": Exact search (best quality, slower for large datasets)
                - "ivf": Inverted file index (faster, slight quality tradeoff)
                - "hnsw": Hierarchical Navigable Small World (best balance)
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.chunks = []  # Store actual text chunks
        self.metadata = []  # Store metadata (page numbers, doc IDs, etc.)
        
        self._initialize_index()
    
    def _initialize_index(self):
        """Create appropriate FAISS index based on type"""
        if self.index_type == "flat":
            # L2 distance (Euclidean)
            self.index = faiss.IndexFlatL2(self.dimension)
            
        elif self.index_type == "ivf":
            # Inverted file with 100 clusters (adjust based on dataset size)
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
            
        elif self.index_type == "hnsw":
            # HNSW for fast approximate search
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)  # 32 = M parameter
            
        else:
            raise ValueError(f"Unknown index type: {self.index_type}")
    
    def add_documents(self, 
                     chunks: List[str], 
                     embeddings: np.ndarray,
                     metadata: Optional[List[Dict]] = None):
        """
        Add documents to the index.
        
        Args:
            chunks: List of text chunks
            embeddings: Numpy array of embeddings (n_chunks, dimension)
            metadata: Optional metadata for each chunk (page numbers, etc.)
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        # Normalize embeddings for cosine similarity (optional but recommended)
        embeddings_normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Train index if needed (for IVF)
        if self.index_type == "ivf" and not self.index.is_trained:
            print(f"Training IVF index with {len(embeddings)} vectors...")
            self.index.train(embeddings_normalized)
        
        # Add vectors to index
        self.index.add(embeddings_normalized)
        
        # Store chunks and metadata
        self.chunks.extend(chunks)
        if metadata:
            self.metadata.extend(metadata)
        else:
            # Create default metadata
            self.metadata.extend([{"chunk_id": i + len(self.chunks) - len(chunks)} 
                                 for i in range(len(chunks))])
        
        print(f"Added {len(chunks)} chunks to index. Total: {len(self.chunks)}")
    
    def search(self, 
              query_embedding: np.ndarray, 
              k: int = 5,
              score_threshold: Optional[float] = None) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector (1D array of dimension)
            k: Number of results to return
            score_threshold: Optional minimum similarity score (lower L2 = more similar)
            
        Returns:
            List of dictionaries containing matched chunks, scores, and metadata
        """
        if self.index.ntotal == 0:
            print("Warning: Index is empty")
            return []
        
        # Normalize query
        query_normalized = query_embedding.reshape(1, -1)
        query_normalized = query_normalized / np.linalg.norm(query_normalized)
        
        # Search
        distances, indices = self.index.search(query_normalized, k)
        
        # Prepare results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            
            # Apply threshold if specified
            if score_threshold and dist > score_threshold:
                continue
            
            results.append({
                "chunk": self.chunks[idx],
                "score": float(dist),  # L2 distance (lower = more similar)
                "metadata": self.metadata[idx],
                "index": int(idx)
            })
        
        return results
    
    def delete_all(self):
        """Clear the entire index"""
        self._initialize_index()
        self.chunks = []
        self.metadata = []
        print("Index cleared")
    
    def save(self, filepath: str):
        """
        Save index and associated data to disk.
        
        Args:
            filepath: Path to save (without extension)
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(filepath.with_suffix('.faiss')))
        
        # Save chunks and metadata
        with open(filepath.with_suffix('.pkl'), 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'metadata': self.metadata,
                'dimension': self.dimension,
                'index_type': self.index_type
            }, f)
        
        print(f"Index saved to {filepath}")
    
    def load(self, filepath: str):
        """
        Load index and associated data from disk.
        
        Args:
            filepath: Path to load (without extension)
        """
        filepath = Path(filepath)
        
        # Load FAISS index
        self.index = faiss.read_index(str(filepath.with_suffix('.faiss')))
        
        # Load chunks and metadata
        with open(filepath.with_suffix('.pkl'), 'rb') as f:
            data = pickle.load(f)
            self.chunks = data['chunks']
            self.metadata = data['metadata']
            self.dimension = data['dimension']
            self.index_type = data['index_type']
        
        print(f"Index loaded: {len(self.chunks)} chunks")
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        return {
            "total_chunks": len(self.chunks),
            "dimension": self.dimension,
            "index_type": self.index_type,
            "is_trained": self.index.is_trained if hasattr(self.index, 'is_trained') else True,
            "ntotal": self.index.ntotal
        }


# Quick test
if __name__ == "__main__":
    # Create dummy embeddings
    dimension = 1536
    n_docs = 100
    
    dummy_embeddings = np.random.randn(n_docs, dimension).astype('float32')
    dummy_chunks = [f"This is document chunk {i}" for i in range(n_docs)]
    dummy_metadata = [{"page": i // 10, "chunk_id": i} for i in range(n_docs)]
    
    # Test index
    index = FAISSIndex(dimension=dimension, index_type="flat")
    index.add_documents(dummy_chunks, dummy_embeddings, dummy_metadata)
    
    # Search
    query_vector = np.random.randn(dimension).astype('float32')
    results = index.search(query_vector, k=5)
    
    print("\nSearch results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.4f}")
        print(f"   Chunk: {result['chunk']}")
        print(f"   Metadata: {result['metadata']}")
    
    # Test save/load
    index.save("test_index/my_index")
    
    new_index = FAISSIndex(dimension=dimension)
    new_index.load("test_index/my_index")
    print(f"\nLoaded index stats: {new_index.get_stats()}")