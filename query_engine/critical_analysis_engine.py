"""
Critical Analysis Engine Module
Specialized LLM engine for critical evaluation queries.
"""

from typing import List, Optional
from utils.llm_client import chat_completion
from utils.language_utils import get_language_name


class CriticalAnalysisEngine:
    """
    Handles critical analysis queries - limitations, assumptions, gaps, weaknesses.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize CriticalAnalysisEngine. api_key kept for backward compatibility."""
        pass

    def process(self, query: str, pages: List[str], relevant_chunks: Optional[List[str]] = None,
                answer_language: Optional[str] = None) -> str:
        """
        Process critical analysis queries with specialized prompting.

        Args:
            query: User query
            pages: Document pages
            relevant_chunks: Pre-retrieved relevant chunks
            answer_language: Target language for the answer

        Returns:
            Critical analysis answer
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
                max_tokens=650,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error performing critical analysis: {str(e)}"

    def _build_system_prompt(self, output_lang: str = "en") -> str:
        """Build critical-analysis specific system prompt"""
        lang_name = get_language_name(output_lang)

        return f"""You are an expert at critical document analysis. You MUST answer in {lang_name} ({output_lang}).
Your role is to identify and explain limitations, assumptions, gaps, weaknesses, and potential issues in documents - but ONLY those that are explicitly mentioned or strongly implied by the document itself.

CORE RESPONSIBILITIES:
1. Identify limitations explicitly stated by the author
2. Note assumptions the author makes or acknowledges
3. Point out gaps the author mentions or that are evident
4. Describe weaknesses or challenges the author discusses
5. Highlight methodological issues mentioned
6. Note areas where the author expresses uncertainty
7. Identify potential biases the author acknowledges

CRITICAL RULES:
1. Focus PRIMARILY on what the document itself says about its limitations
2. You may note OBVIOUS gaps evident from the content, but don't:
   - Add external critique not based on the document
   - Import standards or expectations not relevant to the document
   - Criticize the document from your own perspective
3. Distinguish clearly between:
   - Limitations the author explicitly states
   - Issues evident from reading the content
   - Potential concerns (mark these clearly as inferences)
4. If the document is thorough and acknowledges few limitations, say so
5. Be fair and balanced - don't overstate weaknesses
6. Quote specific passages when citing limitations

RESPONSE STRUCTURE:
1. Start with what limitations the author explicitly acknowledges
2. Note any assumptions clearly stated or evident
3. Mention gaps the author identifies
4. Discuss any weaknesses or challenges described
5. If inferring issues not explicitly stated, clearly mark as "potentially" or "appears to"
6. If the document is comprehensive and well-qualified, acknowledge this

BALANCED TONE:
- Be objective, not overly critical
- Recognize the document's strengths as well as limitations
- Understand context (e.g., a summary won't be as detailed as a full report)"""

    def _build_user_prompt(self, query: str, context: str, output_lang: str = "en") -> str:
        """Build user prompt with context"""
        lang_name = get_language_name(output_lang)

        return f"""Document Content:
{context}

User Question: {query}

Please provide a critical analysis in {lang_name} based on the document content. Focus on limitations, assumptions, and issues that the document itself mentions or that are clearly evident from the content."""
