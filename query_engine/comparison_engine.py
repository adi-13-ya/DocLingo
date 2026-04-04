"""
Comparison Engine Module
Specialized LLM engine for comparison and contrast queries.
"""

from typing import List, Optional
from utils.llm_client import chat_completion
from utils.language_utils import get_language_name


class ComparisonEngine:
    """
    Handles comparison queries - analyzing similarities and differences.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize ComparisonEngine. api_key kept for backward compatibility."""
        pass

    def process(self, query: str, pages: List[str], relevant_chunks: Optional[List[str]] = None,
                answer_language: Optional[str] = None) -> str:
        """
        Process comparison queries with specialized prompting.

        Args:
            query: User query
            pages: Document pages
            relevant_chunks: Pre-retrieved relevant chunks
            answer_language: Target language for the answer

        Returns:
            Comparison answer
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
                temperature=0.3,
                max_tokens=700,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating comparison: {str(e)}"

    def _build_system_prompt(self, output_lang: str = "en") -> str:
        """Build comparison-specific system prompt"""
        lang_name = get_language_name(output_lang)

        return f"""You are an expert at comparative analysis. You MUST answer in {lang_name} ({output_lang}).
Your role is to identify, analyze, and clearly articulate similarities and differences between items, concepts, or approaches mentioned in documents.

CORE RESPONSIBILITIES:
1. Identify what is being compared
2. Find relevant information about each item
3. Systematically compare across multiple dimensions
4. Present findings in a clear, structured manner
5. Highlight both similarities AND differences
6. Provide balanced analysis

CRITICAL RULES:
1. Base ALL comparisons STRICTLY on information in the provided document
2. Do NOT add external knowledge or make unsupported comparisons
3. If information for comparison is incomplete, state what's missing
4. Be objective - don't favor one item over another unless the document does
5. Cite specific passages when making comparative claims
6. If items cannot be meaningfully compared based on the document, explain why

COMPARISON STRUCTURE:
1. Briefly identify what is being compared
2. Present similarities (if any)
3. Present differences across key dimensions:
   - Purpose/function
   - Approach/methodology
   - Results/outcomes
   - Advantages/limitations
   - Context/applicability
4. Provide a brief synthesis

FORMAT GUIDELINES:
- Use clear headers (Similarities, Differences, Key Distinctions)
- Present information in parallel structure
- Use bullet points or tables when appropriate
- Be concise but comprehensive
- Ensure fair representation of both/all items"""

    def _build_user_prompt(self, query: str, context: str, output_lang: str = "en") -> str:
        """Build user prompt with context"""
        lang_name = get_language_name(output_lang)

        return f"""Document Content:
{context}

User Question: {query}

Please provide a clear comparison in {lang_name} based on the document content. Include both similarities and differences, organized in a structured format."""
