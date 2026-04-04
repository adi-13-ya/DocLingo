'''
from document_processor.pdf_loader import load_pdf
from document_processor.text_extractor import extract_text_from_reader
from language_manager.translation_manager import translate_text
from retrieval_engine.retriever import retrieve_relevant_chunks
from answer_engine.generator import generate_answer
from answer_engine.explainer import generate_explanation
from confidence_engine.confidence_score import compute_confidence
from decision_engine.adaptive_engine import AdaptiveDecisionEngine
from language_manager.language_detector import detect_language
from query_engine.router import route_query

def run_doclingo(pdf_file, query, target_lang="en"):
    """
    Phase 3 pipeline with:
    - Adaptive Decision Engine
    - Grounded LLM answering
    - Human-readable explainability
    - Console-level structured metadata
    """

    # -----------------------------
    # 1. Load & extract document
    # -----------------------------
    reader = load_pdf(pdf_file)
    pages = extract_text_from_reader(reader)

    if not pages:
        return {
            "answer": "No readable content found in the document.",
            "confidence": "Low",
            "explanation_text": "The document does not contain readable content.",
        }

    # -----------------------------
    # 2. Language detection
    # -----------------------------
    document_language = detect_language(pages[0])
    query_language = detect_language(query)
    num_pages = len(pages)

    # -----------------------------
    # 3. Adaptive decision
    # -----------------------------
    decision_engine = AdaptiveDecisionEngine()
    decision = decision_engine.decide(
        doc_lang=document_language,
        query_lang=query_language,
        num_pages=num_pages
    )

    translation_strategy = decision.get("translation_strategy", "full")

    # -----------------------------
    # 4. Apply translation strategy
    # -----------------------------
    if translation_strategy == "none":
        processed_pages = pages

    elif translation_strategy == "full":
        processed_pages = [
            translate_text(page, target_lang)[0]
            for page in pages
        ]

    elif translation_strategy == "partial":
        processed_pages = pages

    else:
        processed_pages = pages

    direct_answer = route_query(query, pages)
    if direct_answer:
        return {
            "answer": direct_answer,
            "confidence": "High",
            "explanation_text": "This answer was computed directly from the document structure.",
        }
    
    # -----------------------------
    # 5. Retrieval
    # -----------------------------
    retrieved_chunks = retrieve_relevant_chunks(
        processed_pages,
        query
    )

    # -----------------------------
    # 6. Partial translation (after retrieval)
    # -----------------------------
    if translation_strategy == "partial":
        retrieved_chunks = [
            translate_text(chunk, target_lang)[0]
            for chunk in retrieved_chunks
        ]

    # -----------------------------
    # 7. LLM-based grounded answer
    # -----------------------------
    answer = generate_answer(retrieved_chunks, query)

    # -----------------------------
    # 8. Explainability (TEXT + META)
    # -----------------------------
    explanation_text, explanation_meta = generate_explanation(
    chunks=retrieved_chunks,
    translation_path=translation_strategy,
    query=query,
    query_language=query_language
    )   


    # Print structured explanation ONLY to console
    print("🔍 Explanation metadata:", explanation_meta)

    # -----------------------------
    # 9. Confidence scoring
    # -----------------------------
    confidence = compute_confidence(
        num_chunks=len(retrieved_chunks),
        translation_strategy=translation_strategy
    )

    # -----------------------------
    # 10. Final output (UI-safe)
    # -----------------------------
    return {
        "answer": answer,
        "confidence": confidence,
        "explanation_text": explanation_text,
        "decision_used": decision,
        "document_language": document_language,
        "query_language": query_language,
        "num_chunks_used": len(retrieved_chunks),
    }
'''


'''CLAUDE'''

"""
DocLingo Main Pipeline with FAISS Integration
Phase 3: Intelligent routing + Semantic search
"""

from document_processor.pdf_loader import load_pdf
from document_processor.text_extractor import extract_text_from_reader
from language_manager.translation_manager import translate_text
from language_manager.language_detector import detect_language
from language_manager.language_resolver import LanguageResolver
from retrieval_engine.retriever import FAISSRetriever
from answer_engine.generator import generate_answer
from answer_engine.explainer import generate_explanation
from confidence_engine.confidence_score import compute_confidence, compute_grounding_score
from decision_engine.adaptive_engine import AdaptiveDecisionEngine
from decision_engine.strategy_optimizer import StrategyOptimizer
from query_engine.router import QueryRouter
from query_engine.intent_classifier import IntentClassifier, QueryIntent
from confidence_engine.confidence_calibrator import ConfidenceCalibrator
from feedback_manager.feedback_logger import FeedbackLogger
from safety_engine.policy_enforcer import PolicyEnforcer

import os
import time
from typing import Dict, List, Optional


class DocLingoSystem:
    """
    Complete DocLingo system with FAISS-powered semantic search.
    Manages document indexing and query processing.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the system"""
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize components
        self.router = QueryRouter(openai_api_key=self.openai_api_key)
        self.retriever = FAISSRetriever(
            openai_api_key=self.openai_api_key,
            embedding_model="text-embedding-3-small",
            index_type="flat"
        )
        self.decision_engine = AdaptiveDecisionEngine()
        
        # Phase 4: Feedback-driven learning components
        self.strategy_optimizer = StrategyOptimizer()
        self.confidence_calibrator = ConfidenceCalibrator()
        self.feedback_logger = FeedbackLogger()
        
        # Phase 5: Safety, governance, and robustness
        self.policy_enforcer = PolicyEnforcer()
        
        # Document state
        self.current_document_indexed = False
        self.current_pages = None
        
        # Specialized engine state (set during routing for TIER 2 queries)
        self.specialized_engine = None
        self.specialized_intent = None
        self.current_chunks = None
        self.document_metadata = {}
    
    def index_document(self, pages: List[str], chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Index document pages into FAISS for semantic search.
        
        Args:
            pages: List of page texts
            chunk_size: Characters per chunk
            chunk_overlap: Overlap between chunks
        """
        print("📄 Processing and indexing document with FAISS...")
        
        # Store pages
        self.current_pages = pages
        
        # Create chunks with metadata
        all_chunks = []
        all_metadata = []
        
        for page_num, page_text in enumerate(pages, 1):
            # Use your chunker if available, otherwise simple chunking
            try:
                from document_processor.chunker import chunk_text
                page_chunks = chunk_text(page_text, chunk_size, chunk_overlap)
            except ImportError:
                page_chunks = self._simple_chunk(page_text, chunk_size, chunk_overlap)
            
            for chunk_idx, chunk in enumerate(page_chunks):
                if chunk.strip():  # Only add non-empty chunks
                    all_chunks.append(chunk)
                    all_metadata.append({
                        "page": page_num,
                        "chunk_index": chunk_idx,
                        "total_pages": len(pages)
                    })
        
        # Store chunks
        self.current_chunks = all_chunks
        
        # Index in FAISS
        self.retriever.index_document(all_chunks, all_metadata)
        self.current_document_indexed = True
        
        print(f"✓ Indexed {len(all_chunks)} chunks from {len(pages)} pages")
        
        return {
            "total_chunks": len(all_chunks),
            "total_pages": len(pages),
            "indexed": True
        }
    
    def _simple_chunk(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Simple text chunking with overlap"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk)
            
            start += chunk_size - overlap
        
        return chunks
    
    def retrieve_relevant_chunks(self, query: str, k: int = 5) -> List[str]:
        """
        Retrieve relevant chunks using FAISS semantic search.
        
        Args:
            query: User question
            k: Number of chunks to retrieve
            
        Returns:
            List of relevant chunk texts
        """
        if not self.current_document_indexed:
            print("⚠️  Document not indexed, returning empty chunks")
            return []
        
        results = self.retriever.retrieve(query, k=k)
        
        # Extract just the text chunks for backward compatibility
        return [r['chunk'] for r in results]
    
    def clear_document(self):
        """Clear current document and index"""
        self.retriever.clear_index()
        self.current_document_indexed = False
        self.current_pages = None
        self.current_chunks = None
        self.document_metadata = {}
        print("Document cleared from system")


# Global system instance (singleton pattern)
_doclingo_system = None


def get_doclingo_system() -> DocLingoSystem:
    """Get or create the global DocLingo system instance"""
    global _doclingo_system
    if _doclingo_system is None:
        _doclingo_system = DocLingoSystem()
    return _doclingo_system


def retrieve_relevant_chunks(pages: List[str], query: str, k: int = 5) -> List[str]:
    """
    BACKWARD COMPATIBILITY WRAPPER
    This function maintains the old API while using FAISS internally.
    
    Args:
        pages: Document pages (will be indexed if not already)
        query: User query
        k: Number of chunks to retrieve
        
    Returns:
        List of relevant chunk texts
    """
    system = get_doclingo_system()
    
    # Index document if not already indexed
    if not system.current_document_indexed or system.current_pages != pages:
        system.index_document(pages)
    
    return system.retrieve_relevant_chunks(query, k=k)


def run_doclingo(
    pdf_file, 
    query, 
    target_lang="en",
    user_doc_lang: Optional[str] = None,
    user_query_lang: Optional[str] = None,
    user_answer_lang: Optional[str] = None
):
    """
    Phase 3 + Phase 4 + Phase 5 pipeline with:
    - FAISS-powered semantic search
    - Intelligent Query Routing
    - Adaptive Decision Engine
    - Feedback-driven learning (Phase 4)
    - Safety, governance, and robustness (Phase 5)
    - Explicit language selection support
    - Grounded LLM answering
    - Human-readable explainability
    
    Args:
        pdf_file: PDF file to process
        query: User query
        target_lang: Target language (legacy parameter, kept for backward compatibility)
        user_doc_lang: Optional user-selected document language
        user_query_lang: Optional user-selected query language
        user_answer_lang: Optional user-selected answer language
    """
    start_time = time.time()

    # Initialize system
    system = get_doclingo_system()

    # -----------------------------
    # PHASE 5: Query Safety Check (MUST BE FIRST)
    # -----------------------------
    query_safety = system.policy_enforcer.enforce_query_safety(query)
    
    if not query_safety["allowed"]:
        # Query rejected - return safe response
        execution_time = (time.time() - start_time) * 1000
        
        result = {
            "answer": f"Query rejected for safety reasons: {query_safety['reason']}",
            "confidence": "Low",
            "explanation_text": "Your query was blocked by safety checks. Please rephrase your question without attempting to override system instructions.",
            "query_rejected": True,
            "safety_reason": query_safety["reason"],
        }
        
        # Audit log the rejection
        system.policy_enforcer.audit_query_execution(
            query=query,
            result=result,
            safety_decisions={"query_safety": query_safety},
            execution_time_ms=execution_time
        )
        
        return result
    
    # Use sanitized query if warnings were present
    if query_safety.get("warnings"):
        print(f"⚠️  Phase 5: Query safety warnings: {', '.join(query_safety['warnings'])}")
    
    sanitized_query = query_safety.get("sanitized_query") or query

    # Reset specialized engine state for this query
    system.specialized_engine = None
    system.specialized_intent = None

    # -----------------------------
    # 1. Load & extract document
    # -----------------------------
    reader = load_pdf(pdf_file)
    pages = extract_text_from_reader(reader)

    if not pages:
        return {
            "answer": "No readable content found in the document.",
            "confidence": "Low",
            "explanation_text": "The document does not contain readable content.",
        }

    # -----------------------------
    # 2. Language Resolution (with explicit user selection support)
    # -----------------------------
    language_resolver = LanguageResolver()
    
    # Auto-detect languages only if user didn't provide explicit selections
    detected_doc_lang = None
    detected_query_lang = None
    
    if language_resolver.should_detect_document_language(user_doc_lang):
        detected_doc_lang = detect_language(pages[0])
        print(f"🌐 Auto-detected document language: {detected_doc_lang}")
    else:
        print(f"🌐 Using user-selected document language: {user_doc_lang}")
    
    if language_resolver.should_detect_query_language(user_query_lang):
        detected_query_lang = detect_language(sanitized_query)
        print(f"🌐 Auto-detected query language: {detected_query_lang}")
    else:
        print(f"🌐 Using user-selected query language: {user_query_lang}")
    
    # Resolve final languages
    language_result = language_resolver.resolve_languages(
        user_doc_lang=user_doc_lang,
        user_query_lang=user_query_lang,
        user_answer_lang=user_answer_lang,
        detected_doc_lang=detected_doc_lang,
        detected_query_lang=detected_query_lang
    )
    
    document_language = language_result["document_language"]
    query_language = language_result["query_language"]
    answer_language = language_result["answer_language"]
    print(f"📋 Language resolution: {language_result['resolution_explanation']}")
    
    num_pages = len(pages)

    # -----------------------------
    # 3. Extract document metadata (for routing)
    # -----------------------------
    document_info = {
        "page_count": num_pages,
        "language": document_language,
    }
    
    # Try to extract PDF metadata
    try:
        if hasattr(reader, 'metadata') and reader.metadata:
            if reader.metadata.get('/Title'):
                document_info['title'] = reader.metadata.get('/Title')
            if reader.metadata.get('/Author'):
                document_info['author'] = reader.metadata.get('/Author')
            if reader.metadata.get('/CreationDate'):
                document_info['date'] = reader.metadata.get('/CreationDate')
    except:
        pass

    # Store metadata in system
    system.document_metadata = document_info

    # -----------------------------
    # 4. INTELLIGENT QUERY ROUTING
    # -----------------------------
    # Try to route the query first - this handles metadata/aggregate queries
    # without expensive translation or retrieval
    
    # Initialize routing_intent to None - will be set from routing result
    routing_intent = None
    
    try:
        routing_result = system.router.route(
            query=sanitized_query,  # Phase 5: Use sanitized query
            pages=pages,
            document_info=document_info,
            return_metadata=True,
            answer_language=answer_language  # Change 2: Pass answer language for multilingual output
        )
        
        # Extract intent from routing result to avoid re-classifying later
        routing_intent = routing_result.get('metadata', {}).get('intent')
        
        # Decouple tier detection from answer presence
        # Always read tier from metadata first
        tier = routing_result['metadata'].get('tier', '')
        engine_name = routing_result['metadata'].get('engine', 'ContentEngine')
        print(f"Tier is ADITYA: {tier}")
        # TIER 1 (Programmatic): Early return if answer is available
        if tier == 'TIER 1 (Programmatic)' and routing_result.get('answer') is not None:
            # Query was handled by programmatic engine (MetadataEngine, AggregateEngine, etc.)
            print(f"🎯 Query routed to: {engine_name}")
            print(f"📊 Intent detected: {routing_result['metadata']['intent']}")
            
            # Answer language defaults to query language (rule)
            answer_lang = query_language
            
            return {
                "answer": routing_result['answer'],
                "confidence": "High",
                "explanation_text": f"This answer was computed directly using {engine_name}. "
                                   f"No translation or complex retrieval was needed.",
                "decision_used": {"routing_engine": engine_name},
                "document_language": document_language,
                "query_language": query_language,
                "answer_language": answer_lang,  # Explicit language selection
                "query_intent": routing_result['metadata']['intent'],
                "language_resolution": language_result,  # Full language resolution info
                "num_chunks_used": 0,
                "retrieval_method": "None (Direct computation)",
            }
        
        # TIER 2 (Specialized LLM): Always set up specialized engine and continue to RAG pipeline
        # Note: Tier-2 queries intentionally return answer=None (they need FAISS retrieval first)
        elif tier == 'TIER 2 (Specialized LLM)':
            print(f"🎯 Tier-2 detected ({engine_name}), continuing full pipeline with specialized prompting")
            
            # Extract engine object from router metadata
            # Router always includes engine_object for TIER 2 queries
            engine_object = routing_result['metadata'].get('engine_object')
            if engine_object is not None:
                system.specialized_engine = engine_object
                system.specialized_intent = routing_result['metadata']['intent']
                print(f"✅ Stored specialized engine object: {engine_name}")
            else:
                print(f"⚠️  Engine object not found in routing metadata for {engine_name}, will use general generator")
            
            # Ensure answer is None to force content pipeline
            routing_result['answer'] = None
        
        # TIER 3 (General LLM) or unknown: Continue to content-based pipeline
        else:
            if tier:
                print(f"🎯 Query routed to: {engine_name} (Tier: {tier}), continuing to content pipeline")
            else:
                print(f"🎯 Query routed to: {engine_name}, continuing to content pipeline")
            print(f"🎯 Metadata engine returned None, continuing to content-based answering")
    
    except Exception as e:
        print(f"⚠️  Routing failed ({str(e)}), falling back to standard pipeline")
    
    # -----------------------------
    # 5. PHASE 4: Get feedback-optimized parameters
    # -----------------------------
    # Use intent from routing result instead of re-classifying (avoids duplicate score printing)
    try:
        if routing_intent:
            # Reuse intent from routing result - already classified once
            intent_name = routing_intent
        else:
            # Fallback: only classify if routing didn't provide intent
            intent = system.router.intent_classifier.classify(query)
            intent_name = intent.value if hasattr(intent, 'value') else str(intent)
    except:
        intent_name = None
    
    # Get optimized parameters from feedback history
    optimized_params = system.strategy_optimizer.get_optimized_parameters(
        intent=intent_name,
        days=30
    )
    
    if optimized_params.get("feedback_samples", 0) > 0:
        print(f"📊 Phase 4: Using feedback-optimized parameters ({optimized_params['feedback_samples']} samples)")
    
    # -----------------------------
    # 6. Adaptive decision (for content queries) - Phase 4 enhanced
    # -----------------------------
    decision = system.decision_engine.decide(
        doc_lang=document_language,
        query_lang=query_language,
        num_pages=num_pages,
        optimized_params=optimized_params  # Phase 4: Pass feedback-optimized params
    )

    translation_strategy = decision.get("translation_strategy", "full")
    retrieval_depth = decision.get("retrieval_depth", 5)  # Phase 4: Get optimized depth

    # -----------------------------
    # 6. Apply translation strategy
    # -----------------------------
    if translation_strategy == "none":
        processed_pages = pages

    elif translation_strategy == "full":
        print("🔄 Applying full document translation...")
        # Use resolved query_language as target (user may have selected it)
        translation_target = query_language
        processed_pages = [
            translate_text(page, translation_target)[0]
            for page in pages
        ]

    elif translation_strategy == "partial":
        processed_pages = pages

    else:
        processed_pages = pages

    # -----------------------------
    # 7. INDEX DOCUMENT WITH FAISS (NEW)
    # -----------------------------
    print("🔍 Indexing document with FAISS...")
    
    # Index the processed pages
    if not system.current_document_indexed or system.current_pages != processed_pages:
        system.index_document(processed_pages, chunk_size=500, chunk_overlap=50)
    
    # -----------------------------
    # 8. SEMANTIC RETRIEVAL WITH FAISS - Phase 4 optimized
    # -----------------------------
    print("🎯 Retrieving relevant chunks with semantic search...")
    
    # Phase 4: Use feedback-optimized retrieval depth
    k = retrieval_depth
    print(f"   Using retrieval depth: {k} (optimized from feedback)" if optimized_params.get("feedback_samples", 0) > 0 else f"   Using retrieval depth: {k}")
    
    # Use FAISS to find semantically similar chunks
    faiss_results = system.retriever.retrieve(sanitized_query, k=k)  # Phase 5: Use sanitized query
    
    # Extract chunks and metadata
    retrieved_chunks = [r['chunk'] for r in faiss_results]
    chunks_metadata = [
        {
            "page": r['metadata']['page'],
            "score": r['score'],
            "chunk_index": r['metadata']['chunk_index']
        }
        for r in faiss_results
    ]
    
    print(f"   Retrieved {len(retrieved_chunks)} chunks")
    for i, meta in enumerate(chunks_metadata, 1):
        print(f"   {i}. Page {meta['page']} (similarity: {1/(1+meta['score']):.2%})")
    
    # Calculate average similarity early for diagnostic logging
    if chunks_metadata:
        avg_similarity = sum(1/(1+m['score']) for m in chunks_metadata) / len(chunks_metadata)
    else:
        avg_similarity = 0.0

    # -----------------------------
    # 9. Partial translation (after retrieval)
    # -----------------------------
    if translation_strategy == "partial":
        print("🔄 Applying partial translation to retrieved chunks...")
        # Use resolved query_language as target
        translation_target = query_language
        retrieved_chunks = [
            translate_text(chunk, translation_target)[0]
            for chunk in retrieved_chunks
        ]

    # -----------------------------
    # 10. LLM-based grounded answer
    # -----------------------------
    print("🤖 Generating answer with LLM...")
    
    # Use sanitized query for answer generation
    answer_query = sanitized_query
    
    # Check if a specialized engine was identified during routing (TIER 2)
    if hasattr(system, 'specialized_engine') and system.specialized_engine is not None:
        engine_name = system.specialized_engine.__class__.__name__
        print(f"🎯 Using specialized engine: {engine_name}")
        
        # Validate that the engine object has a process method
        if not hasattr(system.specialized_engine, 'process'):
            print(f"⚠️  Specialized engine {engine_name} does not have a process method, falling back to general generator")
            answer = generate_answer(
                retrieved_chunks, 
                answer_query,
                answer_language=answer_language
            )
        else:
            try:
                # Check if the specialized engine supports answer_language parameter
                import inspect
                sig = inspect.signature(system.specialized_engine.process)
                params = sig.parameters
                
                # Prepare arguments for specialized engine
                # All specialized engines expect: query, pages, relevant_chunks
                engine_args = {
                    'query': answer_query,
                    'pages': processed_pages,
                    'relevant_chunks': retrieved_chunks
                }
                
                # Add answer_language if the engine supports it (e.g., SummarizationEngine)
                if 'answer_language' in params:
                    engine_args['answer_language'] = answer_language
                
                # Call the specialized engine with retrieved chunks (RAG-grounded)
                answer = system.specialized_engine.process(**engine_args)
                
                if answer and len(answer.strip()) > 0:
                    print(f"✅ Specialized engine ({engine_name}) generated answer ({len(answer)} characters)")
                else:
                    raise ValueError(f"Specialized engine {engine_name} returned empty answer")
                    
            except Exception as e:
                print(f"⚠️  Specialized engine ({engine_name}) failed: {str(e)}")
                print(f"   Falling back to general generator")
                import traceback
                traceback.print_exc()
                # Fall back to general generator
                answer = generate_answer(
                    retrieved_chunks, 
                    answer_query,
                    answer_language=answer_language
                )
    else:
        # Use general generator (default behavior for TIER 3 or when no specialized engine is set)
        answer = generate_answer(
            retrieved_chunks, 
            answer_query,
            answer_language=answer_language
        )
    
    # DIAGNOSTIC LOG: Raw LLM output before safety checks
    print("🔍 [DIAGNOSTIC] Raw LLM answer (before safety checks):")
    print(f"   Length: {len(answer)} characters")
    print(f"   Preview: {answer[:200]}{'...' if len(answer) > 200 else ''}")
    print(f"   Avg Similarity: {avg_similarity:.4f} ({avg_similarity:.2%})")
    
    # -----------------------------
    # PHASE 5: Non-blocking Output Safety Check
    # -----------------------------
    # Only rejects if zero chunks retrieved
    output_safety = system.policy_enforcer.enforce_output_safety(
        answer=answer,
        retrieved_chunks=retrieved_chunks,
        query=sanitized_query,
        confidence="Medium",  # Will be updated after confidence calculation
        target_language=answer_language
    )
    
    if not output_safety["is_valid"]:
        # Only case: zero chunks retrieved
        print("⚠️  Phase 5: No chunks retrieved, using fallback message")
        print(f"   Reason: {output_safety.get('reason', 'Unknown')}")
        answer = output_safety["validated_answer"]
    elif output_safety.get("warnings"):
        # Soft warnings only (non-blocking)
        print(f"⚠️  Phase 5: Output safety warnings: {', '.join(output_safety['warnings'])}")

    # -----------------------------
    # 11. Explainability (TEXT + META)
    # -----------------------------
    # Use the same query and chunks that were used for answer generation
    # This ensures answer and explanation are synchronized
    explanation_text, explanation_meta = generate_explanation(
        chunks=retrieved_chunks,  # Same chunks used for answer generation
        translation_path=translation_strategy,
        query=sanitized_query,  # Phase 5: Use sanitized query (same as answer_query)
        query_language=query_language
    )

    # Add FAISS retrieval info to explanation
    explanation_meta['retrieval_method'] = 'FAISS Semantic Search'
    explanation_meta['chunks_metadata'] = chunks_metadata

    # Print structured explanation ONLY to console
    print("📋 Explanation metadata:", explanation_meta)

    # -----------------------------
    # 12. Confidence scoring with grounding score integration
    # -----------------------------
    # Calculate grounding score (token-level overlap with normalization)
    grounding_score = None
    if retrieved_chunks and answer:
        grounding_score = compute_grounding_score(
            answer=answer,
            retrieved_chunks=retrieved_chunks,
            document_language=document_language,
            answer_language=answer_language
        )
        print(f"📊 Grounding score: {grounding_score:.4f} ({grounding_score:.2%})")
    
    # Note: avg_similarity already calculated earlier for diagnostic logging
    if not chunks_metadata:  # Safety check in case chunks_metadata is empty
        avg_similarity = 0.0
    
    # Compute confidence with grounding score integration
    confidence_result = compute_confidence(
        num_chunks=len(retrieved_chunks),
        translation_strategy=translation_strategy,
        grounding_score=grounding_score,
        document_language=document_language,
        answer_language=answer_language
    )
    
    base_confidence_value = confidence_result["base_confidence"]
    confidence = confidence_result["confidence"]
    
    if confidence_result.get("grounding_penalty_applied"):
        print(f"📊 Grounding penalty applied: {base_confidence_value} -> {confidence}")
    
    # Phase 4: Calibrate confidence based on feedback
    # Determine engine name (routing_result might not exist if routing was skipped)
    engine_name = 'ContentEngine'  # Default
    if 'routing_result' in locals() and routing_result:
        engine_name = routing_result.get('metadata', {}).get('engine', 'ContentEngine')
    
    calibrated_confidence = system.confidence_calibrator.calibrate_confidence(
        base_confidence=confidence,  # Use confidence after grounding penalty
        intent=intent_name,
        engine=engine_name,
        days=30
    )
    
    confidence = calibrated_confidence["calibrated_confidence"]
    if calibrated_confidence.get("feedback_based"):
        print(f"📊 Phase 4: Confidence calibrated to {confidence}")
    
    # -----------------------------
    # PHASE 5: Non-blocking Uncertainty Handling
    # -----------------------------
    # Only adjusts confidence and logs warnings, never modifies answer
    uncertainty_result = system.policy_enforcer.enforce_uncertainty_handling(
        answer=answer,
        confidence=confidence,
        num_chunks=len(retrieved_chunks),
        avg_similarity=avg_similarity,
        target_language=answer_language,
        query_intent=intent_name,
        document_language=document_language,
        query_language=query_language
    )
    
    # Apply confidence adjustment if needed (non-blocking)
    if uncertainty_result.get("confidence_adjusted"):
        confidence = uncertainty_result.get("final_confidence", confidence)
        warnings = uncertainty_result.get("warnings", [])
        print(f"⚠️  Phase 5: Confidence adjusted to {confidence}")
        if warnings:
            print(f"   Warnings: {', '.join(warnings)}")
        crosslingual = uncertainty_result.get('uncertainty_result', {}).get('is_crosslingual', False)
        if crosslingual:
            print(f"   Note: Cross-lingual scenario detected (lower similarity threshold used)")
    
    # -----------------------------
    # Answer Translation (if answer language differs from query language)
    # -----------------------------
    if language_resolver.should_translate_answer(answer_language, query_language):
        print(f"🔄 Translating answer to {answer_language}...")
        try:
            answer = translate_text(answer, answer_language)[0]
        except Exception as e:
            print(f"⚠️  Answer translation failed: {e}, using answer in query language")

    # -----------------------------
    # 13. Final output with Phase 4 & Phase 5 metadata
    # -----------------------------
    result = {
        "answer": answer,
        "confidence": confidence,
        "explanation_text": explanation_text,
        "decision_used": decision,
        "document_language": document_language,
        "query_language": query_language,
        "answer_language": answer_language,  # Explicit language selection
        "query_intent": intent_name,  # Phase 4: Include intent for feedback
        "language_resolution": language_result,  # Full language resolution info
        "num_chunks_used": len(retrieved_chunks),
        "routing_used": True,
        "retrieval_method": "FAISS Semantic Search",
        "avg_similarity_score": f"{avg_similarity:.2%}",
        "grounding_score": f"{grounding_score:.4f}" if grounding_score is not None else None,
        "chunks_metadata": chunks_metadata,
        # Phase 4: Additional metadata for feedback logging
        "base_confidence": base_confidence_value,
        "calibrated_confidence_info": calibrated_confidence.get("explanation", ""),
        "optimization_applied": optimized_params.get("feedback_samples", 0) > 0,
        "optimization_explanation": optimized_params.get("explanation", ""),
        # Phase 5: Safety metadata
        "safety_checks_passed": True,
        "query_safety": query_safety,
        "output_safety": output_safety,
        "uncertainty_handling": uncertainty_result,
    }
    
    # -----------------------------
    # PHASE 5: Audit Logging
    # -----------------------------
    execution_time = (time.time() - start_time) * 1000
    safety_decisions = {
        "query_safety": query_safety,
        "output_safety": output_safety,
        "uncertainty_handling": uncertainty_result
    }
    
    system.policy_enforcer.audit_query_execution(
        query=query,  # Original query for audit
        result=result,
        safety_decisions=safety_decisions,
        execution_time_ms=execution_time
    )
    
    return result


def run_doclingo_with_routing_info(pdf_file, query, target_lang="en", verbose=False):
    """
    Enhanced version that provides detailed routing information.
    Use this for debugging or when you want to see routing decisions.
    """
    result = run_doclingo(pdf_file, query, target_lang)
    
    if verbose:
        print("\n" + "="*60)
        print("📋 ROUTING & PROCESSING SUMMARY")
        print("="*60)
        print(f"Query: {query}")
        print(f"Document Language: {result.get('document_language', 'Unknown')}")
        print(f"Query Language: {result.get('query_language', 'Unknown')}")
        print(f"Retrieval Method: {result.get('retrieval_method', 'Unknown')}")
        print(f"Avg Similarity: {result.get('avg_similarity_score', 'N/A')}")
        
        if 'query_intent' in result:
            print(f"Query Intent: {result['query_intent']}")
        
        if 'decision_used' in result:
            print(f"Decision Used: {result['decision_used']}")
        
        print(f"Chunks Used: {result.get('num_chunks_used', 0)}")
        print(f"Confidence: {result['confidence']}")
        print("="*60)
    
    return result


# Backward compatibility function
def route_query(query, pages, document_info=None):
    """
    Legacy function for backward compatibility.
    Returns answer directly or None if it should go to full pipeline.
    """
    try:
        system = get_doclingo_system()
        result = system.router.route(
            query=query,
            pages=pages,
            document_info=document_info,
            return_metadata=True
        )
        
        # Only return answer if handled by specialized engine
        if result['metadata']['engine'] != 'ContentEngine':
            return result['answer']
        
        return None  # Let main pipeline handle it
    
    except Exception as e:
        print(f"⚠️  Query routing failed: {str(e)}")
        return None

'''
Example usage
if __name__ == "__main__":
    # Test with a sample PDF
    pdf_path = "sample_document.pdf"
    test_queries = [
        "How many pages does this document have?",  # Metadata query
        "What is the main topic discussed?",         # Content query (uses FAISS)
        "Summarize the key findings",                 # Content query (uses FAISS)
    ]
    
    print("="*60)
    print("DocLingo with FAISS Integration Test")
    print("="*60)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-"*60)
        
        result = run_doclingo_with_routing_info(
            pdf_file=pdf_path,
            query=query,
            target_lang="en",
            verbose=True
        )
        
        print(f"\n💬 Answer: {result['answer']}")
        print()

        '''