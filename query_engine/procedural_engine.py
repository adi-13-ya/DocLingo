"""
Procedural Engine Module
Specialized LLM engine for how-to and process extraction queries.
"""

from typing import List, Optional
from utils.llm_client import chat_completion
from utils.language_utils import get_language_name


class ProceduralEngine:
    """
    Handles procedural queries - extracting and explaining processes, steps, and methods.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize ProceduralEngine. api_key kept for backward compatibility."""
        pass

    def process(self, query: str, pages: List[str], relevant_chunks: Optional[List[str]] = None,
                answer_language: Optional[str] = None) -> str:
        """
        Process procedural queries with specialized prompting.

        Args:
            query: User query
            pages: Document pages
            relevant_chunks: Pre-retrieved relevant chunks
            answer_language: Target language for the answer

        Returns:
            Procedural answer
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
                temperature=0.2,
                max_tokens=700,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error extracting procedure: {str(e)}"

    def _find_relevant_context(self, query: str, pages: List[str], top_k: int = 4) -> str:
        """Find context with procedural information"""
        query_words = set(query.lower().split())
        page_scores = []

        for page in pages:
            page_words = set(page.lower().split())
            overlap = len(query_words & page_words)

            if any(word in page.lower() for word in ["step", "process", "procedure", "method", "how to"]):
                overlap += 5

            if overlap > 0:
                page_scores.append((overlap, page))

        page_scores.sort(reverse=True, key=lambda x: x[0])
        return "\n\n".join([page for _, page in page_scores[:top_k]])

    def _build_system_prompt(self, output_lang: str = "en") -> str:
        """Build procedural-specific system prompt"""
        lang_name = get_language_name(output_lang)

        return f"""You are an expert at extracting and presenting procedures, processes, and step-by-step instructions from documents. You MUST answer in {lang_name} ({output_lang}).

CORE RESPONSIBILITIES:
1. Extract step-by-step procedures from documents
2. Organize steps in logical, sequential order
3. Identify prerequisites or requirements
4. Note any warnings, cautions, or important notes
5. Clarify the purpose and expected outcome
6. Present complex processes in an understandable way

CRITICAL RULES:
1. Extract procedures EXACTLY as described in the document
2. Do NOT add steps not mentioned in the document
3. Preserve the original sequence and ordering
4. Include all important details (timing, quantities, conditions)
5. If steps are unclear or incomplete in the document, note this
6. Quote exact instructions for critical steps
7. If no clear procedure exists in the document, state this clearly

PROCESS EXTRACTION GUIDELINES:

**When Clear Steps Exist:**
- Number each step sequentially (1, 2, 3...)
- Use imperative language ("Do X", "Complete Y")
- Include sub-steps where mentioned (1a, 1b or nested bullets)
- Preserve conditional logic ("If X, then Y")
- Note parallel vs. sequential steps

**When Process is Narrative:**
- Extract the sequence from descriptive text
- Convert to step format while staying faithful to content
- Maintain causality and dependencies

**Information to Include:**
- **Purpose**: What is the goal of this process?
- **Prerequisites**: What's needed before starting?
- **Steps**: The actual procedure
- **Notes/Warnings**: Important caveats mentioned
- **Expected Outcome**: What should result from following these steps?

**Formatting:**
- Use numbered lists for sequential steps
- Use bullet points for items within steps
- Use bold for warnings or critical information
- Keep each step concise but complete
- Group related steps when appropriate"""

    def _build_user_prompt(self, query: str, context: str, output_lang: str = "en") -> str:
        """Build user prompt with context"""
        lang_name = get_language_name(output_lang)

        return f"""Document Content:
{context}

User Question: {query}

Please extract and present the procedure, process, or steps in {lang_name} as described in the document. Format as a clear, sequential guide with numbered steps."""
