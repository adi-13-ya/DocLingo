"""
Opinion & Stance Engine Module
Specialized LLM engine for identifying author's viewpoint, arguments, and positions.
"""

from typing import List, Optional
from utils.llm_client import chat_completion
from utils.language_utils import get_language_name


class OpinionStanceEngine:
    """
    Handles queries about author's opinions, positions, arguments, and stances.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpinionStanceEngine. api_key kept for backward compatibility."""
        pass

    def process(self, query: str, pages: List[str], relevant_chunks: Optional[List[str]] = None,
                answer_language: Optional[str] = None) -> str:
        """
        Process opinion/stance queries with specialized prompting.

        Args:
            query: User query
            pages: Document pages
            relevant_chunks: Pre-retrieved relevant chunks
            answer_language: Target language for the answer

        Returns:
            Opinion/stance analysis
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
                max_tokens=600,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error analyzing opinion/stance: {str(e)}"

    def _build_system_prompt(self, output_lang: str = "en") -> str:
        """Build opinion-stance specific system prompt"""
        lang_name = get_language_name(output_lang)

        return f"""You are an expert at analyzing author viewpoints, arguments, and positions in documents. You MUST answer in {lang_name} ({output_lang}).
Your role is to identify and explain what the author believes, argues, advocates, or opposes.

CORE RESPONSIBILITIES:
1. Identify the author's position or stance on key issues
2. Extract and present the author's main arguments
3. Note what the author supports, opposes, or recommends
4. Identify the evidence and reasoning the author provides
5. Recognize the author's perspective and framing
6. Distinguish between different types of statements:
   - Factual claims
   - Value judgments
   - Recommendations
   - Predictions

CRITICAL RULES:
1. Base ALL analysis STRICTLY on what the document explicitly states
2. Do NOT attribute opinions to the author that aren't in the text
3. Distinguish between:
   - The author's own opinion
   - Opinions the author is reporting or quoting
   - Neutral presentation of multiple viewpoints
4. Quote directly when presenting the author's views
5. If the author is neutral or presents multiple sides, state this clearly
6. Acknowledge when the document doesn't reveal the author's position

ANALYSIS STRUCTURE:
1. Main Position: What is the author's overall stance?
2. Key Arguments: What arguments does the author make?
3. Supporting Evidence: What evidence or reasoning is provided?
4. What They Support: What does the author advocate for or endorse?
5. What They Oppose: What does the author critique or reject?
6. Recommendations: What actions or changes does the author suggest?
7. Underlying Values/Assumptions: What beliefs or principles underpin the position?

NEUTRAL ANALYSIS:
- Describe the position objectively
- Don't add your own judgment about whether the position is correct
- Present the strongest version of the author's argument
- Note any qualifications or limitations the author acknowledges"""

    def _build_user_prompt(self, query: str, context: str, output_lang: str = "en") -> str:
        """Build user prompt with context"""
        lang_name = get_language_name(output_lang)

        return f"""Document Content:
{context}

User Question: {query}

Please analyze the author's position, arguments, and stance in {lang_name} based on the document content. Include what they support, oppose, and recommend, with supporting quotes."""
