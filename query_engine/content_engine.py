"""
Content Engine Module
Handles semantic queries using LLM with RAG (Retrieval Augmented Generation).
"""

from typing import List, Optional, Dict
from utils.llm_client import chat_completion
from utils.language_utils import get_language_name


class ContentEngine:
    """
    Handles content-based queries using semantic search + LLM.
    Strictly document-grounded to avoid hallucination.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ContentEngine.

        Args:
            api_key: Kept for backward compatibility (unused - LiteLLM reads from env)
        """
        pass

    def process(self, query: str, pages: List[str], relevant_chunks: Optional[List[str]] = None,
                query_intent: Optional[str] = None, answer_language: Optional[str] = None) -> str:
        """
        Process content-based queries using LLM with document context.

        Args:
            query: User query
            pages: Full document pages
            relevant_chunks: Pre-retrieved relevant text chunks (from FAISS or similar)
            query_intent: The classified intent for better prompting
            answer_language: Target language for the answer

        Returns:
            str: LLM-generated answer grounded in document
        """
        # If no relevant chunks provided, use a simple retrieval
        if relevant_chunks is None:
            relevant_chunks = self._simple_retrieval(query, pages)

        # Build context from relevant chunks
        context = "\n\n".join(relevant_chunks)

        # Determine answer language (default to query language)
        output_lang = answer_language or "en"

        # Create intent-specific system prompt
        system_prompt = self._build_system_prompt(query_intent, output_lang)

        # Build user prompt
        user_prompt = self._build_user_prompt(query, context, output_lang)

        # Call LLM API
        try:
            response = chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            answer = response.choices[0].message.content
            return answer

        except Exception as e:
            return f"Error processing query with LLM: {str(e)}"

    def _simple_retrieval(self, query: str, pages: List[str], top_k: int = 3) -> List[str]:
        """
        Simple keyword-based retrieval when no vector search is available.
        """
        query_words = set(query.lower().split())

        page_scores = []
        for i, page in enumerate(pages):
            page_words = set(page.lower().split())
            overlap = len(query_words & page_words)
            if overlap > 0:
                page_scores.append((overlap, i, page))

        page_scores.sort(reverse=True, key=lambda x: x[0])
        return [page for _, _, page in page_scores[:top_k]]

    def _build_system_prompt(self, query_intent: Optional[str] = None, output_lang: str = "en") -> str:
        """Build intent-specific system prompt with language instruction."""
        lang_name = get_language_name(output_lang)

        base_prompt = f"""You are a helpful AI assistant that answers questions based strictly on the provided document context.
You MUST answer in {lang_name} ({output_lang}).

CRITICAL RULES:
1. Only use information from the provided context
2. If the answer is not in the context, say "I cannot find this information in the document"
3. Do not make up or infer information not explicitly stated
4. Cite specific parts of the document when possible
5. Be concise and direct in your answers"""

        # Add intent-specific instructions
        intent_instructions = {
            "summarization": "\n6. Focus on providing a clear, structured summary of the key points",
            "comparison": "\n6. Clearly highlight similarities and differences between the items being compared",
            "interpretation": "\n6. Explain the meaning or significance while staying grounded in the document text",
            "causation": "\n6. Identify and explain cause-effect relationships mentioned in the document",
            "predictive": "\n6. Focus on forward-looking statements and predictions in the document",
            "opinion_stance": "\n6. Identify the author's position, arguments, and supporting evidence",
            "procedural": "\n6. List steps or procedures in a clear, sequential manner",
            "definitional": "\n6. Provide clear definitions based on how terms are used in the document",
        }

        if query_intent and query_intent in intent_instructions:
            base_prompt += intent_instructions[query_intent]

        return base_prompt

    def _build_user_prompt(self, query: str, context: str, answer_language: str = "en") -> str:
        """Build user prompt with context"""
        lang_name = get_language_name(answer_language)
        return f"""Document Context:
{context}

Question: {query}

Please answer the question in {lang_name} ({answer_language}) using only the information from the document context above."""

    def process_with_translation(self, query: str, query_language: str,
                                 pages: List[str], document_language: str,
                                 relevant_chunks: Optional[List[str]] = None) -> str:
        """
        Process query with automatic translation support.
        """
        if query_language != document_language:
            translated_query = self._translate_text(query, query_language, document_language)
        else:
            translated_query = query

        answer = self.process(translated_query, pages, relevant_chunks)

        if query_language != document_language:
            answer = self._translate_text(answer, document_language, query_language)

        return answer

    def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using LLM."""
        try:
            response = chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the following text from {source_lang} to {target_lang}. Preserve the meaning and tone."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            return response.choices[0].message.content

        except Exception as e:
            return text
