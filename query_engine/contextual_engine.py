"""
Contextual Engine Module
Specialized LLM engine for context and background queries.
"""

from typing import List, Optional
from utils.llm_client import chat_completion
from utils.language_utils import get_language_name


class ContextualEngine:
    """
    Handles contextual queries - background, setting, circumstances, and situational context.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize ContextualEngine. api_key kept for backward compatibility."""
        pass

    def process(self, query: str, pages: List[str], relevant_chunks: Optional[List[str]] = None,
                answer_language: Optional[str] = None) -> str:
        """
        Process contextual queries with specialized prompting.

        Args:
            query: User query
            pages: Document pages
            relevant_chunks: Pre-retrieved relevant chunks
            answer_language: Target language for the answer

        Returns:
            Contextual answer
        """
        if relevant_chunks:
            context = "\n\n".join(relevant_chunks)
        else:
            context = "\n\n".join(pages)

        output_lang = answer_language or "en"
        system_prompt = self._build_system_prompt(output_lang)
        user_prompt = self._build_user_prompt(query, context, output_lang)

        try:
            response = chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=650,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error providing context: {str(e)}"

    def _build_system_prompt(self, output_lang: str = "en") -> str:
        """Build context-specific system prompt"""
        lang_name = get_language_name(output_lang)

        return f"""You are an expert at extracting and explaining contextual information from documents. You MUST answer in {lang_name} ({output_lang}).
Your role is to provide background, setting, circumstances, and situational context that helps understand the content.

CORE RESPONSIBILITIES:
1. Extract background information provided in the document
2. Identify the historical, cultural, or situational context
3. Explain the circumstances or conditions relevant to the content
4. Note the timeframe and setting
5. Identify the intended audience or purpose
6. Provide context that aids comprehension

CRITICAL RULES:
1. Extract context information ONLY from the provided document
2. Do NOT add historical or cultural context from external knowledge
3. Distinguish between:
   - Context explicitly provided in the document
   - Context implied by the content
   - Context that would require external information (note when this is missing)
4. If context is limited in the document, state this clearly
5. Quote passages that establish context
6. Be clear about what the document assumes readers already know

TYPES OF CONTEXT TO IDENTIFY:

**Historical Context:**
- When was this written/published?
- What time period does it discuss?
- What events preceded or influenced this?

**Cultural/Social Context:**
- What cultural setting or norms?
- What social conditions?
- What audience is this for?

**Situational Context:**
- What problem or situation prompted this?
- What circumstances led to this?

**Purpose/Framework Context:**
- Why was this created?
- What perspective or framework is used?
- What assumptions underlie the content?

RESPONSE STRUCTURE:
1. **Primary Context**: The main situational or historical setting
2. **Background**: Relevant preceding information
3. **Circumstances**: Conditions or factors at play
4. **Framework**: The perspective or approach being used
5. **Intended Audience**: Who this is for (if indicated)
6. **Relevance**: Why this context matters for understanding the content"""

    def _build_user_prompt(self, query: str, context: str, output_lang: str = "en") -> str:
        """Build user prompt with context"""
        lang_name = get_language_name(output_lang)

        return f"""Document Content:
{context}

User Question: {query}

Please provide the contextual information and background in {lang_name} based on the document content. Explain the setting, circumstances, and relevant context that helps understand this document."""
