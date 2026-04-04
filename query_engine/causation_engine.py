"""
Causation Engine Module
Specialized LLM engine for cause-effect and reasoning queries.
"""

from typing import List, Optional
from utils.llm_client import chat_completion
from utils.language_utils import get_language_name


class CausationEngine:
    """
    Handles causation queries - explaining why things happened and cause-effect relationships.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize CausationEngine. api_key kept for backward compatibility."""
        pass

    def process(self, query: str, pages: List[str], relevant_chunks: Optional[List[str]] = None,
                answer_language: Optional[str] = None) -> str:
        """
        Process causation queries with specialized prompting.

        Args:
            query: User query
            pages: Document pages
            relevant_chunks: Pre-retrieved relevant chunks
            answer_language: Target language for the answer

        Returns:
            Causation answer
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
            return f"Error analyzing causation: {str(e)}"

    def _find_relevant_context(self, query: str, pages: List[str], top_k: int = 3) -> str:
        """Find context related to the question"""
        query_words = set(query.lower().split())
        page_scores = []

        for page in pages:
            page_words = set(page.lower().split())
            overlap = len(query_words & page_words)
            if overlap > 0:
                page_scores.append((overlap, page))

        page_scores.sort(reverse=True, key=lambda x: x[0])
        return "\n\n".join([page for _, page in page_scores[:top_k]])

    def _build_system_prompt(self, output_lang: str = "en") -> str:
        """Build causation-specific system prompt"""
        lang_name = get_language_name(output_lang)

        return f"""You are an expert at causal analysis. You MUST answer in {lang_name} ({output_lang}).
Your role is to identify, explain, and trace cause-effect relationships and reasoning chains in documents.

CORE RESPONSIBILITIES:
1. Identify explicit cause-effect relationships stated in the document
2. Trace chains of causation (A -> B -> C)
3. Explain the reasoning and rationale provided
4. Distinguish between:
   - Direct causes (immediate triggers)
   - Root causes (underlying factors)
   - Contributing factors (supporting conditions)
   - Consequences (effects and outcomes)
5. Present causal relationships clearly and logically

CRITICAL RULES:
1. Base ALL causal claims STRICTLY on what the document states or clearly implies
2. Do NOT invent causal relationships not supported by the text
3. Distinguish between:
   - Explicitly stated causation ("X caused Y")
   - Implied causation ("X led to Y", "due to X")
   - Correlation without stated causation ("X and Y occurred")
4. If causation is unclear or multiple explanations exist, acknowledge this
5. Quote or cite specific passages that establish causation
6. If the document doesn't explain "why," clearly state this

EXPLANATION STRUCTURE:
1. Identify what needs explanation (the effect or outcome)
2. State the primary cause(s) from the document
3. Explain the causal mechanism (how/why the cause led to effect)
4. Note any contributing factors
5. Mention any consequences or further effects
6. Acknowledge limitations or alternative explanations if mentioned

LANGUAGE CLARITY:
- Use clear causal language: "because," "led to," "resulted in," "caused by"
- Avoid ambiguous phrasing
- Be explicit about strength of causal claims (definite vs. possible)
- Chain causes logically when multiple factors are involved"""

    def _build_user_prompt(self, query: str, context: str, output_lang: str = "en") -> str:
        """Build user prompt with context"""
        lang_name = get_language_name(output_lang)

        return f"""Document Content:
{context}

User Question: {query}

Please explain the cause-effect relationships in {lang_name} based on the document content. Identify the causes, explain the reasoning, and trace any causal chains mentioned."""
