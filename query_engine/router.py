"""
Router Module - FINAL FIXED VERSION
All import and explanation issues resolved
"""

from typing import List, Optional, Dict
import os

# Relative imports
from .intent_classifier import IntentClassifier, QueryIntent

# TIER 1: Programmatic Engines (Fast, Free, Accurate)
from .metadata_engine import MetadataEngine
from .aggregate_engine import AggregateEngine
from .analytical_engine import AnalyticalEngine

# TIER 2: Specialized LLM Engines (High Quality, Category-Specific)
from .summarization_engine import SummarizationEngine
from .interpretation_engine import InterpretationEngine
from .comparison_engine import ComparisonEngine
from .causation_engine import CausationEngine
from .opinion_stance_engine import OpinionStanceEngine
from .critical_analysis_engine import CriticalAnalysisEngine
from .procedural_engine import ProceduralEngine
from .contextual_engine import ContextualEngine

# TIER 3: General LLM Engine (Fallback)
from .content_engine import ContentEngine


class QueryRouter:
    """
    Enhanced query routing system with 3-tier architecture:
    - TIER 1: Programmatic (metadata, counting, calculations)
    - TIER 2: Specialized LLM (summarization, interpretation, etc.)
    - TIER 3: General LLM (fallback for everything else)
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, retriever=None):
        """
        Initialize router with all engines.
        
        Args:
            openai_api_key: OpenAI API key for LLM engines
            retriever: Optional FAISS retriever (only used by SummarizationEngine)
        """
        # Intent classifier
        self.intent_classifier = IntentClassifier()
        
        # TIER 1: Programmatic Engines (always initialize)
        self.metadata_engine = MetadataEngine()
        self.aggregate_engine = AggregateEngine()
        self.analytical_engine = AnalyticalEngine()
        
        # TIER 2 & 3: LLM Engines (require API key)
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if api_key:
            try:
                # TIER 2: Specialized LLM Engines
                self.summarization_engine = SummarizationEngine(api_key=api_key, retriever=retriever)
                self.interpretation_engine = InterpretationEngine(api_key=api_key)
                self.comparison_engine = ComparisonEngine(api_key=api_key)
                self.causation_engine = CausationEngine(api_key=api_key)
                self.opinion_stance_engine = OpinionStanceEngine(api_key=api_key)
                self.critical_analysis_engine = CriticalAnalysisEngine(api_key=api_key)
                self.procedural_engine = ProceduralEngine(api_key=api_key)
                self.contextual_engine = ContextualEngine(api_key=api_key)
                
                # TIER 3: General Content Engine
                self.content_engine = ContentEngine(api_key=api_key)
                
                self.llm_available = True
            except Exception as e:
                print(f"⚠️  Warning: LLM engines initialization failed: {e}")
                self.llm_available = False
        else:
            print("⚠️  Warning: No OpenAI API key provided. Only programmatic engines available.")
            self.llm_available = False
        
        # Intent to engine mapping
        self._setup_engine_mapping()
    
    def _setup_engine_mapping(self):
        """Setup mapping from intents to engines"""
        
        # TIER 1: Programmatic (always available)
        self.tier1_mapping = {
            QueryIntent.METADATA: self.metadata_engine,
            QueryIntent.AGGREGATE: self.aggregate_engine,
            QueryIntent.ANALYTICAL: self.analytical_engine,
            QueryIntent.STRUCTURAL: self.aggregate_engine,
            QueryIntent.QUANTITATIVE: self.analytical_engine,
        }
        
        # TIER 2: Specialized LLM (requires API key)
        if self.llm_available:
            self.tier2_mapping = {
                QueryIntent.SUMMARIZATION: self.summarization_engine,
                QueryIntent.INTERPRETATION: self.interpretation_engine,
                QueryIntent.COMPARISON: self.comparison_engine,
                QueryIntent.CAUSATION: self.causation_engine,
                QueryIntent.OPINION_STANCE: self.opinion_stance_engine,
                QueryIntent.CRITICAL_ANALYSIS: self.critical_analysis_engine,
                QueryIntent.PROCEDURAL: self.procedural_engine,
                QueryIntent.CONTEXTUAL: self.contextual_engine,
                QueryIntent.PREDICTIVE: self.interpretation_engine,  # Use interpretation
                QueryIntent.DEFINITIONAL: self.interpretation_engine,  # Use interpretation
                QueryIntent.SENTIMENT: self.interpretation_engine,  # Use interpretation
                QueryIntent.CROSS_REFERENCE: self.content_engine,  # Use general content
                QueryIntent.VISUAL_ELEMENTS: self.content_engine,  # Use general content
                QueryIntent.COMPLIANCE: self.content_engine,  # Use general content
                QueryIntent.FORMAT_PRESENTATION: self.content_engine,  # Use general content
                QueryIntent.SEARCH_LOOKUP: self.content_engine,  # Use general content
                QueryIntent.CONTENT_EXTRACTION: self.content_engine,  # Use general content
            }
        else:
            self.tier2_mapping = {}
    
    def route(self, query: str, pages: List[str], 
              document_info: Optional[Dict] = None,
              relevant_chunks: Optional[List[str]] = None,
              return_metadata: bool = False,
              answer_language: Optional[str] = None) -> Dict:
        """
        Route query to appropriate engine and return answer.
        
        Args:
            query: User query string
            pages: List of document pages
            document_info: Optional document metadata
            relevant_chunks: Pre-retrieved relevant chunks for content queries
            return_metadata: If True, return routing metadata along with answer
            
        Returns:
            Dict with 'answer' and optionally 'metadata' about routing decision
        """
        # Classify intent
        intent = self.intent_classifier.classify(query)
        print(f"Intent: {intent}")
        answer = None
        engine_used = None
        tier_used = None
        engine_object = None  # Store engine object for TIER 2
        
        # TRY TIER 1: Programmatic Engines
        # Note: If TIER 1 engine returns None, fall through to content-based answering
        if intent in self.tier1_mapping:
            print(f"TIER 1: {intent}")
            engine = self.tier1_mapping[intent]
            engine_used = engine.__class__.__name__
            tier_used = "TIER 1 (Programmatic)"
            
            try:
                if isinstance(engine, MetadataEngine):
                    answer = engine.process(query, pages, document_info)
                    # If MetadataEngine returns None, it means the query requires content search
                    # Fall through to content-based answering instead of early return
                elif isinstance(engine, AggregateEngine):
                    answer = engine.process(query, pages)
                elif isinstance(engine, AnalyticalEngine):
                    answer = engine.process(query, pages, document_info)
            except Exception as e:
                print(f"⚠️  {engine_used} failed: {e}")
                answer = None
            
            # Only use TIER 1 answer if it's not None (i.e., engine successfully handled it)
            # If None, fall through to TIER 2/3 for content-based answering
            if answer is not None:
                # TIER 1 successfully handled the query - return early
                if return_metadata:
                    return {
                        "answer": answer,
                        "metadata": {
                            "intent": intent.value,
                            "engine": engine_used,
                            "tier": tier_used,
                            "used_faiss": False,
                            "explanation": f"Query classified as '{intent.value}' and routed to {engine_used}"
                        }
                    }
                else:
                    return {"answer": answer}
        
        # TRY TIER 2: Specialized LLM Engines
        if answer is None and self.llm_available and intent in self.tier2_mapping:
            print(f"TIER 2: {intent}")
            engine_object = self.tier2_mapping[intent]  # Get engine instance
            engine_used = engine_object.__class__.__name__  # Get engine name
            tier_used = "TIER 2 (Specialized LLM)"
            
            # For TIER 2, we don't generate answer here (needs FAISS retrieval first)
            # Just mark that this is a TIER 2 query and return None answer
            # The engine object will be stored in metadata for later use
            answer = None
        
        # FALLBACK TO TIER 3: General Content Engine
        if answer is None and self.llm_available:
            print(f"TIER 3: {intent}")
            engine_used = "ContentEngine"
            tier_used = "TIER 3 (General LLM)"
            engine_object = None  # No engine object for TIER 3
            
            try:
                answer = self.content_engine.process(
                    query=query,
                    pages=pages,
                    relevant_chunks=relevant_chunks,
                    query_intent=intent.value,
                    answer_language=answer_language
                )
            except Exception as e:
                print(f"⚠️  ContentEngine failed: {e}")
                answer = "Unable to process query. Please try again."
        
        # If no LLM available and programmatic engines couldn't handle it
        if answer is None and not self.llm_available:
            answer = "This query requires LLM processing. Please configure OpenAI API key."
            engine_used = "None"
            tier_used = "N/A"
            engine_object = None
        
        # Prepare response
        response = {"answer": answer}
        
        if return_metadata:
            # Build metadata with engine name
            metadata = {
                "intent": intent.value,
                "engine": engine_used,
                "tier": tier_used,
                "explanation": f"Query classified as '{intent.value}' and routed to {engine_used}"
            }
            
            # For TIER 2, include the engine object for later use
            if tier_used == "TIER 2 (Specialized LLM)" and engine_object is not None:
                metadata["engine_object"] = engine_object
                print(f"✅ Router: Included engine object ({engine_used}) in metadata for TIER 2")
            
            response["metadata"] = metadata
        
        return response
    
    def batch_route(self, queries: List[str], pages: List[str],
                   document_info: Optional[Dict] = None) -> List[Dict]:
        """
        Route multiple queries efficiently.
        
        Args:
            queries: List of user queries
            pages: Document pages
            document_info: Optional document metadata
            
        Returns:
            List of response dicts
        """
        responses = []
        for query in queries:
            response = self.route(
                query=query,
                pages=pages,
                document_info=document_info,
                return_metadata=True
            )
            response["query"] = query
            responses.append(response)
        
        return responses


# Standalone function for backward compatibility
def route_query(query: str, pages: List[str], 
                document_info: Optional[Dict] = None,
                openai_api_key: Optional[str] = None) -> Optional[str]:
    """
    Simple function to route a query - for easy integration.
    Returns answer if handled by TIER 1 engine, None otherwise.
    
    Args:
        query: User query
        pages: Document pages
        document_info: Optional metadata
        openai_api_key: Optional OpenAI API key
        
    Returns:
        Answer string if TIER 1 engine handled it, None otherwise
    """
    try:
        router = QueryRouter(openai_api_key=openai_api_key)
        result = router.route(
            query=query,
            pages=pages,
            document_info=document_info,
            return_metadata=True
        )
        
        # Only return answer if handled by TIER 1 (programmatic) engine
        if result['metadata']['tier'] == "TIER 1 (Programmatic)":
            return result["answer"]
        
        return None  # Signal to use full pipeline for TIER 2/3
    
    except Exception as e:
        print(f"⚠️  route_query error: {e}")
        return None