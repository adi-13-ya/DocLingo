"""
Vector Store Package for DocLingo
Provides FAISS-based vector storage and retrieval
"""

from .embedding_manager import EmbeddingManager
from .faiss_index import FAISSIndex

__all__ = ['EmbeddingManager', 'FAISSIndex']