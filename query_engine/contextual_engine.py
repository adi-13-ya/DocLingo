"""
Contextual Engine Module
Specialized LLM engine for context and background queries.
"""

from typing import List, Optional
import os
from openai import OpenAI


class ContextualEngine:
    """
    Handles contextual queries - background, setting, circumstances, and situational context.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required for ContextualEngine")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"
    
    def process(self, query: str, pages: List[str], relevant_chunks: Optional[List[str]] = None) -> str:
        """
        Process contextual queries with specialized prompting.
        
        Args:
            query: User query
            pages: Document pages
            relevant_chunks: Pre-retrieved relevant chunks
            
        Returns:
            Contextual answer
        """
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
                temperature=0.4,
                max_tokens=650
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error providing context: {str(e)}"
    
    def _build_system_prompt(self) -> str:
        """Build context-specific system prompt"""
        
        return """You are an expert at extracting and explaining contextual information from documents. Your role is to provide background, setting, circumstances, and situational context that helps understand the content.

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
- What was happening at the time?

**Cultural/Social Context:**
- What cultural setting or norms?
- What social conditions?
- What audience is this for?

**Situational Context:**
- What problem or situation prompted this?
- What circumstances led to this?
- What was the state of affairs?

**Purpose/Framework Context:**
- Why was this created?
- What perspective or framework is used?
- What assumptions underlie the content?

**Institutional/Organizational Context:**
- What organization or entity is involved?
- What role or authority do they have?
- What are their goals or mandate?

RESPONSE STRUCTURE:
1. **Primary Context**: The main situational or historical setting
2. **Background**: Relevant preceding information
3. **Circumstances**: Conditions or factors at play
4. **Framework**: The perspective or approach being used
5. **Intended Audience**: Who this is for (if indicated)
6. **Relevance**: Why this context matters for understanding the content

CLARITY GUIDELINES:
- Start with the most important context
- Connect context to the main content
- Explain why the context matters
- Note any context the document assumes but doesn't explain
- If the document provides minimal context, acknowledge this"""
    
    def _build_user_prompt(self, query: str, context: str) -> str:
        """Build user prompt with context"""
        
        return f"""Document Content:
{context}

User Question: {query}

Please provide the contextual information and background based on the document content. Explain the setting, circumstances, and relevant context that helps understand this document."""