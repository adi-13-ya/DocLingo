"""
Interpretation Engine Module
Specialized LLM engine for interpretation and explanation queries.
"""

from typing import List, Optional
from utils.llm_client import chat_completion
from utils.language_utils import get_language_name


class InterpretationEngine:
    """
    Handles interpretation queries - explaining meaning, significance, and implications.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize InterpretationEngine. api_key kept for backward compatibility."""
        pass

    def process(self, query: str, pages: List[str], relevant_chunks: Optional[List[str]] = None,
                answer_language: Optional[str] = None) -> str:
        """
        Process interpretation queries with specialized prompting.

        Args:
            query: User query
            pages: Document pages
            relevant_chunks: Pre-retrieved relevant chunks
            answer_language: Target language for the answer

        Returns:
            Interpretation answer
        """
        if relevant_chunks:
            context = "\n\n".join(relevant_chunks)
        else:
            context = self._find_relevant_context(query, pages)

        output_lang = answer_language or "en"
        system_prompt = self._build_system_prompt(output_lang)
        user_prompt = self._build_user_prompt(query, context, output_lang)

        try:
            response = chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=600,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating interpretation: {str(e)}"

    def _find_relevant_context(self, query: str, pages: List[str], top_k: int = 3) -> str:
        """Simple keyword-based context retrieval"""
        query_words = set(query.lower().split())
        page_scores = []

        for i, page in enumerate(pages):
            page_words = set(page.lower().split())
            overlap = len(query_words & page_words)
            if overlap > 0:
                page_scores.append((overlap, page))

        page_scores.sort(reverse=True, key=lambda x: x[0])
        return "\n\n".join([page for _, page in page_scores[:top_k]])

    def _build_system_prompt(self, output_lang: str = "en") -> str:
        """Build interpretation-specific system prompt"""
        lang_name = get_language_name(output_lang)

        return f"""You are an expert at interpreting and explaining document content. You MUST answer in {lang_name} ({output_lang}).
Your role is to clarify meaning, explain significance, and illuminate implications.

CORE RESPONSIBILITIES:
1. Explain the MEANING of terms, phrases, or concepts as used in the document
2. Clarify the SIGNIFICANCE or importance of information
3. Explore IMPLICATIONS and what information suggests
4. Provide CONTEXT that aids understanding
5. Break down complex ideas into understandable explanations

CRITICAL RULES:
1. Base all interpretations STRICTLY on the provided document content
2. Distinguish clearly between:
   - What the document explicitly states
   - What can be reasonably inferred from the content
   - What would be speculation (avoid this)
3. If something is ambiguous, acknowledge multiple possible interpretations
4. Use clear, accessible language
5. Cite specific passages when explaining meaning
6. If the document doesn't provide enough context, state this clearly

INTERPRETATION APPROACH:
- Start with the literal meaning
- Then explain deeper significance
- Connect to broader context within the document
- Highlight why this matters
- Avoid over-interpretation or reading things not present in the text"""

    def _build_user_prompt(self, query: str, context: str, output_lang: str = "en") -> str:
        """Build user prompt with context"""
        lang_name = get_language_name(output_lang)

        return f"""Document Content:
{context}

User Question: {query}

Please provide a clear interpretation in {lang_name} based on the document content. Explain the meaning, significance, and implications of the relevant information."""
