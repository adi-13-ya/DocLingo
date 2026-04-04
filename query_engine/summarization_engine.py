"""
Summarization Engine Module
Specialized LLM engine for summarization queries with expert prompts.
FAISS-enhanced with multilingual support.
"""

from typing import List, Optional, Dict, Union
from utils.llm_client import chat_completion
from utils.language_utils import get_language_name


class SummarizationEngine:
    """
    Handles summarization queries using specialized LLM prompts.
    Optimized for creating concise, accurate summaries.
    Supports FAISS chunks and multilingual output.
    """
    
    def __init__(self, api_key: Optional[str] = None, retriever=None):
        """Initialize SummarizationEngine. api_key kept for backward compatibility."""
        self.retriever = retriever  # FAISS retriever (optional)
    
    def process(
        self, 
        query: str, 
        pages: List[str], 
        relevant_chunks: Optional[Union[List[str], List[Dict]]] = None,
        answer_language: Optional[str] = None
    ) -> str:
        """
        Process summarization queries with specialized prompting.
        
        Args:
            query: User query
            pages: Document pages
            relevant_chunks: Pre-retrieved relevant chunks (strings or FAISS dicts)
            answer_language: Target language for the answer (e.g., "te", "hi", "en")
            
        Returns:
            Summarized answer
        """
        # Normalize chunks (handle both string and FAISS dict formats)
        if relevant_chunks:
            # Extract text from chunks (handle FAISS format)
            context_chunks = []
            for chunk in relevant_chunks:
                if isinstance(chunk, dict):
                    context_chunks.append(chunk.get('chunk', str(chunk)))
                else:
                    context_chunks.append(str(chunk))
            # For summarization, use ALL retrieved chunks or full document
            context = "\n\n".join(context_chunks)
        else:
            # No chunks provided - use full document (for summarization, we want the whole doc)
            context = "\n\n".join(pages)  # Use all pages for summary
        
        # Detect summary type from query (works with multilingual queries too)
        summary_type = self._detect_summary_type(query.lower())
        
        # Build specialized prompt with multilingual support
        output_lang = answer_language or "en"
        lang_name = self._get_language_name(output_lang)
        system_prompt = self._build_system_prompt(summary_type, output_lang, lang_name)
        user_prompt = self._build_user_prompt(query, context, summary_type, output_lang, lang_name)
        
        try:
            response = chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=800,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def _get_language_name(self, lang_code: str) -> str:
        """Get human-readable language name from language code."""
        return get_language_name(lang_code)
    
    def _detect_summary_type(self, query: str) -> str:
        """Detect what kind of summary is requested (works with multilingual queries)"""
        query_lower = query.lower()
        
        # English keywords
        if any(word in query_lower for word in ["brief", "short", "quick", "concise", "150", "100"]):
            return "brief"
        elif any(word in query_lower for word in ["key points", "main points", "highlights", "takeaways"]):
            return "key_points"
        elif any(word in query_lower for word in ["abstract", "overview"]):
            return "abstract"
        elif any(word in query_lower for word in ["detailed", "comprehensive", "in-depth"]):
            return "detailed"
        # Telugu keywords
        elif "150" in query or "100" in query or any(word in query_lower for word in ["సంక్షిప్త", "క్లుప్త"]):
            return "brief"
        # Hindi keywords
        elif any(word in query_lower for word in ["संक्षिप्त", "मुख्य बिंदु"]):
            return "brief" if "संक्षिप्त" in query_lower else "key_points"
        else:
            return "standard"
    
    def _build_system_prompt(self, summary_type: str, answer_language: str = "en", lang_name: str = "English") -> str:
        """Build summary-type specific system prompt"""
        
        base_prompt = f"""You are an expert document summarizer. You MUST generate the summary in {lang_name} ({answer_language}).

CRITICAL RULES:
1. Generate the summary STRICTLY in {lang_name} ({answer_language})
2. Extract information ONLY from the provided context
3. Do NOT add external knowledge or assumptions
4. Preserve key facts, figures, and dates accurately
5. Maintain the document's tone and perspective
6. Do NOT use technical terms like 'chunks', 'embeddings', 'similarity scores', 'retrieval', or 'FAISS' in your summary
7. Use natural, user-friendly language
8. If the document doesn't contain enough information, state this clearly in {lang_name}"""
        
        type_specific = {
            "brief": "\n6. Create a CONCISE summary (2-3 sentences maximum)\n7. Focus on the absolute most important point",
            
            "key_points": "\n6. Structure the summary as bullet points\n7. Include 4-6 key takeaways\n8. Each point should be 1-2 sentences\n9. Prioritize actionable insights",
            
            "abstract": "\n6. Write in academic/formal style\n7. Include: purpose, methods, findings, conclusions\n8. Keep to 150-200 words\n9. Use third-person perspective",
            
            "detailed": "\n6. Provide a comprehensive summary\n7. Organize by main sections or themes\n8. Include important supporting details\n9. Aim for 300-400 words",
            
            "standard": "\n6. Create a balanced summary (100-150 words)\n7. Cover main ideas and key supporting points\n8. Maintain logical flow"
        }
        
        return base_prompt + type_specific.get(summary_type, type_specific["standard"])
    
    def _build_user_prompt(
        self, 
        query: str, 
        context: str, 
        summary_type: str,
        answer_language: str = "en",
        lang_name: str = "English"
    ) -> str:
        """Build user prompt with context and language instructions"""
        
        # Extract word count if specified (e.g., "150 words", "150 పదాలలో")
        word_count_match = None
        import re
        word_count_patterns = [
            r'(\d+)\s*(?:words?|పదాల?|शब्दों?|வார்த்தைகள்?|വാക്കുകൾ?)',
            r'(\d+)\s*words?',
        ]
        for pattern in word_count_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                word_count_match = int(match.group(1))
                break
        
        if summary_type == "key_points":
            instruction = f"Provide the key points from this document in bullet format in {lang_name}:"
        elif summary_type == "brief":
            if word_count_match:
                instruction = f"Provide a brief summary of this document in approximately {word_count_match} words in {lang_name}:"
            else:
                instruction = f"Provide a brief summary of this document (2-3 sentences) in {lang_name}:"
        elif summary_type == "abstract":
            instruction = f"Provide an abstract-style summary of this document in {lang_name}:"
        elif summary_type == "detailed":
            instruction = f"Provide a detailed summary of this document in {lang_name}:"
        else:
            if word_count_match:
                instruction = f"Summarize this document in approximately {word_count_match} words in {lang_name}:"
            else:
                instruction = f"Summarize this document in {lang_name}:"
        
        return f"""Document Content:
{context}

User Question: {query}

{instruction}"""