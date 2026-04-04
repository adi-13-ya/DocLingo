"""
Embedding Manager for DocLingo
Handles text-to-vector conversion using LiteLLM (provider-agnostic).
"""

from typing import List, Optional
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.llm_client import create_embedding, get_embedding_dimension, get_current_embedding_model


class EmbeddingManager:
    """Manages text embedding generation using LiteLLM (supports OpenAI, Gemini, etc.)"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the embedding manager.

        Args:
            api_key: Kept for backward compatibility (unused - LiteLLM reads from env)
            model: Embedding model to use (default from env/config)
                - text-embedding-3-small (1536 dims, $0.02/1M tokens) - RECOMMENDED
                - text-embedding-3-large (3072 dims, $0.13/1M tokens)
                - text-embedding-ada-002 (1536 dims, legacy)
        """
        self.model = model or get_current_embedding_model()
        self.dimension = get_embedding_dimension(self.model)

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
            return np.zeros(self.dimension, dtype=np.float32)

        try:
            response = create_embedding(
                input_text=text.strip(),
                model=self.model,
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

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to embed per API call (max 2048)

        Returns:
            Numpy array of shape (n_texts, embedding_dim)
        """
        if not texts:
            return np.array([]).reshape(0, self.dimension)

        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch = [text.strip() if text else "" for text in batch]

            try:
                response = create_embedding(
                    input_text=batch,
                    model=self.model,
                )

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
                        all_embeddings.append(np.zeros(self.dimension).tolist())

        return np.array(all_embeddings, dtype=np.float32)

    def get_dimension(self) -> int:
        """Return the embedding dimension"""
        return self.dimension
