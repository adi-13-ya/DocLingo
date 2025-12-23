"""
Content Engine Module
Handles semantic queries using OpenAI LLM with RAG (Retrieval Augmented Generation).
"""

from typing import List, Optional, Dict
import os
from openai import OpenAI


class ContentEngine:
    """
    Handles content-based queries using semantic search + LLM.
    Strictly document-grounded to avoid hallucination.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (will use OPENAI_API_KEY env var if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # or "gpt-4" for better quality
    
    def process(self, query: str, pages: List[str], relevant_chunks: Optional[List[str]] = None,
                query_intent: Optional[str] = None, answer_language: Optional[str] = None) -> str:
        """
        Process content-based queries using LLM with document context.
        
        Args:
            query: User query
            pages: Full document pages
            relevant_chunks: Pre-retrieved relevant text chunks (from FAISS or similar)
            query_intent: The classified intent for better prompting
            
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
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            return answer
        
        except Exception as e:
            return f"Error processing query with LLM: {str(e)}"
    
    def _simple_retrieval(self, query: str, pages: List[str], top_k: int = 3) -> List[str]:
        """
        Simple keyword-based retrieval when no vector search is available.
        In production, replace this with FAISS or similar vector search.
        
        Args:
            query: User query
            pages: Document pages
            top_k: Number of top chunks to return
            
        Returns:
            List of relevant text chunks
        """
        query_words = set(query.lower().split())
        
        # Score each page by keyword overlap
        page_scores = []
        for i, page in enumerate(pages):
            page_words = set(page.lower().split())
            overlap = len(query_words & page_words)
            if overlap > 0:
                page_scores.append((overlap, i, page))
        
        # Sort by score and return top pages
        page_scores.sort(reverse=True, key=lambda x: x[0])
        return [page for _, _, page in page_scores[:top_k]]
    
    def _build_system_prompt(self, query_intent: Optional[str]) -> str:
        """Build intent-specific system prompt"""
        base_prompt = """You are a helpful AI assistant that answers questions based strictly on the provided document context.

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
        lang_name = self._get_language_name(answer_language)
        return f"""Document Context:
{context}

Question: {query}

Please answer the question in {lang_name} ({answer_language}) using only the information from the document context above."""
    
    def _get_language_name(self, lang_code: str) -> str:
        """Get human-readable language name from language code"""
        lang_names = {
            "en": "English", "es": "Spanish", "fr": "French", "de": "German",
            "it": "Italian", "pt": "Portuguese", "ru": "Russian", "zh": "Chinese",
            "ja": "Japanese", "ko": "Korean", "ar": "Arabic", "hi": "Hindi",
            "ml": "Malayalam", "ta": "Tamil", "te": "Telugu", "kn": "Kannada",
            "mr": "Marathi", "ur": "Urdu", "bn": "Bengali", "gu": "Gujarati",
            "pa": "Punjabi", "or": "Odia", "as": "Assamese",
        }
        return lang_names.get(lang_code, lang_code.upper())
    
    def process_with_translation(self, query: str, query_language: str, 
                                 pages: List[str], document_language: str,
                                 relevant_chunks: Optional[List[str]] = None) -> str:
        """
        Process query with automatic translation support.
        
        Args:
            query: User query in any language
            query_language: Language code of the query (e.g., 'es', 'fr', 'hi')
            pages: Document pages in original language
            document_language: Language code of document
            relevant_chunks: Pre-retrieved relevant chunks
            
        Returns:
            Answer in the query language
        """
        # Translate query to document language if needed
        if query_language != document_language:
            translated_query = self._translate_text(query, query_language, document_language)
        else:
            translated_query = query
        
        # Process with translated query
        answer = self.process(translated_query, pages, relevant_chunks)
        
        # Translate answer back to query language if needed
        if query_language != document_language:
            answer = self._translate_text(answer, document_language, query_language)
        
        return answer
    
    def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using OpenAI.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
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
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return text  # Return original text if translation fails