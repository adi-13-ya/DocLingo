"""
Comparison Engine Module
Specialized LLM engine for comparison and contrast queries.
"""

from typing import List, Optional
import os
from openai import OpenAI


class ComparisonEngine:
    """
    Handles comparison queries - analyzing similarities and differences.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required for ComparisonEngine")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"
    
    def process(self, query: str, pages: List[str], relevant_chunks: Optional[List[str]] = None) -> str:
        """
        Process comparison queries with specialized prompting.
        
        Args:
            query: User query
            pages: Document pages
            relevant_chunks: Pre-retrieved relevant chunks
            
        Returns:
            Comparison answer
        """
        # Use chunks or full document
        if relevant_chunks:
            context = "\n\n".join(relevant_chunks)
        else:
            context = "\n\n".join(pages)
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(query, context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=700
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating comparison: {str(e)}"
    
    def _build_system_prompt(self) -> str:
        """Build comparison-specific system prompt"""
        
        return """You are an expert at comparative analysis. Your role is to identify, analyze, and clearly articulate similarities and differences between items, concepts, or approaches mentioned in documents.

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
    
    def _build_user_prompt(self, query: str, context: str) -> str:
        """Build user prompt with context"""
        
        return f"""Document Content:
{context}

User Question: {query}

Please provide a clear comparison based on the document content. Include both similarities and differences, organized in a structured format."""