"""
Centralized LLM Client for DocLingo
Provider-agnostic interface using LiteLLM.
Supports OpenAI, Gemini, Ollama, and 100+ other providers.
"""

import os
import litellm
from typing import List, Dict, Optional, Union
from dotenv import load_dotenv

load_dotenv()

# Suppress verbose LiteLLM logging
litellm.set_verbose = False

# Runtime-configurable model settings
_current_chat_model: Optional[str] = None
_current_embedding_model: Optional[str] = None


def get_current_chat_model() -> str:
    """Get the currently active chat model."""
    return _current_chat_model or os.getenv("LLM_CHAT_MODEL", "gpt-4o-mini")


def set_current_chat_model(model: str):
    """Set the chat model at runtime (e.g., from Streamlit UI)."""
    global _current_chat_model
    _current_chat_model = model


def get_current_embedding_model() -> str:
    """Get the currently active embedding model."""
    return _current_embedding_model or os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")


def set_current_embedding_model(model: str):
    """Set the embedding model at runtime."""
    global _current_embedding_model
    _current_embedding_model = model


def chat_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: Optional[int] = None,
    stream: bool = False,
):
    """
    Provider-agnostic chat completion using LiteLLM.

    Model name conventions:
      - OpenAI:  "gpt-4o-mini", "gpt-4o"
      - Gemini:  "gemini/gemini-2.0-flash"
      - Ollama:  "ollama/llama3"

    API keys are read from environment variables automatically:
      - OpenAI:  OPENAI_API_KEY
      - Gemini:  GEMINI_API_KEY
      - Ollama:  No key needed (local)

    Returns:
        LiteLLM response (OpenAI-compatible format).
        Access: response.choices[0].message.content
    """
    model = model or get_current_chat_model()
    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": stream,
    }
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    return litellm.completion(**kwargs)


def create_embedding(
    input_text: Union[str, List[str]],
    model: Optional[str] = None,
):
    """
    Provider-agnostic embedding generation using LiteLLM.

    Args:
        input_text: Single string or list of strings to embed
        model: Embedding model name (default from env/config)

    Returns:
        LiteLLM response (OpenAI-compatible format).
        Access: response.data[0].embedding (single) or response.data[i].embedding (batch)
    """
    model = model or get_current_embedding_model()
    return litellm.embedding(model=model, input=input_text)


def get_embedding_dimension(model: Optional[str] = None) -> int:
    """Return the expected embedding dimension for the configured model."""
    model = model or get_current_embedding_model()
    dim_map = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }
    return dim_map.get(model, 1536)
