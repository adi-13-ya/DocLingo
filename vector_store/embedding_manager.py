"""
Embedding Manager for DocLingo
Handles text-to-vector conversion using OpenAI embeddings
"""

from typing import List, Optional
import openai
import os
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential


class EmbeddingManager:
    """Manages text embedding generation using OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        """
        Initialize the embedding manager.
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            model: Embedding model to use
                - text-embedding-3-small (1536 dims, $0.02/1M tokens) - RECOMMENDED
                - text-embedding-3-large (3072 dims, $0.13/1M tokens)
                - text-embedding-ada-002 (1536 dims, legacy)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        self.model = model
        self.dimension = 1536 if "small" in model or "ada" in model else 3072
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Numpy array of embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.dimension, dtype=np.float32)
        
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=text.strip()
            )
            embedding = response.data[0].embedding
            return np.array(embedding, dtype=np.float32)
        
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def embed_batch(self, texts: List[str], batch_size: int = 100) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batches.
        More efficient than calling embed_text repeatedly.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to embed per API call (max 2048)
            
        Returns:
            Numpy array of shape (n_texts, embedding_dim)
        """
        if not texts:
            return np.array([]).reshape(0, self.dimension)
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            # Filter out empty strings
            batch = [text.strip() if text else "" for text in batch]
            
            try:
                response = openai.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                # Extract embeddings in order
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
            except Exception as e:
                print(f"Error in batch {i//batch_size}: {e}")
                # Fallback: embed individually
                for text in batch:
                    try:
                        emb = self.embed_text(text)
                        all_embeddings.append(emb.tolist())
                    except:
                        # Use zero vector as fallback
                        all_embeddings.append(np.zeros(self.dimension).tolist())
        
        return np.array(all_embeddings, dtype=np.float32)
    
    def get_dimension(self) -> int:
        """Return the embedding dimension"""
        return self.dimension


# Quick test
if __name__ == "__main__":
    manager = EmbeddingManager()
    
    # Test single embedding
    text = "This is a test document about machine learning."
    embedding = manager.embed_text(text)
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    
    # Test batch embedding
    texts = [
        "First document about AI",
        "Second document about machine learning",
        "Third document about neural networks"
    ]
    embeddings = manager.embed_batch(texts)
    print(f"\nBatch embeddings shape: {embeddings.shape}")