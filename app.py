"""
DocLingo - Phase 6: Enhanced UI/UX with Performance Optimizations
Clean, professional interface with intelligent caching for speed.
"""

import streamlit as st
import hashlib
import time
from typing import Optional, Dict, Any
from io import BytesIO

from main import run_doclingo, DocLingoSystem
from feedback_manager.feedback_logger import FeedbackLogger

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="DocLingo",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CUSTOM CSS FOR CLEAN UI
# ============================================================================
st.markdown("""
    <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Header styling */
        h1 {
            color: #1f4788;
            border-bottom: 3px solid #4a90e2;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }
        
        /* Answer box styling */
        .answer-box {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #4a90e2;
            margin: 1rem 0;
        }
        
        /* Confidence badge styling */
        .confidence-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            margin: 0.5rem 0;
        }
        
        .confidence-high {
            background-color: #d4edda;
            color: #155724;
        }
        
        .confidence-medium {
            background-color: #fff3cd;
            color: #856404;
        }
        
        .confidence-low {
            background-color: #f8d7da;
            color: #721c24;
        }
        
        /* Status messages */
        .status-message {
            padding: 0.75rem;
            border-radius: 6px;
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }
        
        .status-info {
            background-color: #e7f3ff;
            color: #004085;
            border-left: 3px solid #004085;
        }
        
        /* Section dividers */
        .section-divider {
            margin: 2rem 0;
            border-top: 2px solid #e0e0e0;
        }
        
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# PERFORMANCE: CACHED FUNCTIONS
# ============================================================================

@st.cache_resource
def get_doclingo_system() -> DocLingoSystem:
    """Cache the DocLingo system instance (expensive to initialize)"""
    return DocLingoSystem()

@st.cache_resource
def get_feedback_logger() -> FeedbackLogger:
    """Cache the feedback logger instance"""
    return FeedbackLogger()

def compute_file_hash(file_bytes: bytes) -> str:
    """Compute hash of file for caching purposes"""
    return hashlib.md5(file_bytes).hexdigest()

@st.cache_data
def process_document_cached(file_bytes: bytes, file_hash: str) -> Dict[str, Any]:
    """
    Cache document processing results.
    Uses file_hash as part of cache key to ensure cache invalidation on file change.
    Only caches serializable data (pages, metadata), not reader objects.
    """
    from document_processor.pdf_loader import load_pdf
    from document_processor.text_extractor import extract_text_from_reader
    from language_manager.language_detector import detect_language
    
    # Create a file-like object from bytes
    pdf_file = BytesIO(file_bytes)
    
    # Load and extract
    reader = load_pdf(pdf_file)
    pages = extract_text_from_reader(reader)
    
    if not pages:
        return {
            "pages": [],
            "document_language": "en",
            "num_pages": 0,
            "metadata": {}
        }
    
    # Detect language (cached separately)
    document_language = detect_language(pages[0])
    
    # Extract metadata (only serializable data)
    metadata = {"page_count": len(pages)}
    try:
        if hasattr(reader, 'metadata') and reader.metadata:
            if reader.metadata.get('/Title'):
                metadata['title'] = str(reader.metadata.get('/Title'))
            if reader.metadata.get('/Author'):
                metadata['author'] = str(reader.metadata.get('/Author'))
            if reader.metadata.get('/CreationDate'):
                metadata['date'] = str(reader.metadata.get('/CreationDate'))
    except:
        pass
    
    # Return only serializable data (not reader object)
    return {
        "pages": pages,
        "document_language": document_language,
        "num_pages": len(pages),
        "metadata": metadata
    }

@st.cache_data
def detect_query_language_cached(query: str) -> str:
    """Cache language detection for queries"""
    from language_manager.language_detector import detect_language
    return detect_language(query)

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """Render clean header"""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1>📄 DocLingo</h1>
            <p style="color: #666; font-size: 1.1rem;">Intelligent Document Q&A System</p>
        </div>
    """, unsafe_allow_html=True)

def render_confidence_badge(confidence: str):
    """Render confidence badge with appropriate styling"""
    confidence_lower = confidence.lower()
    if "high" in confidence_lower:
        class_name = "confidence-high"
        emoji = "✅"
    elif "medium" in confidence_lower:
        class_name = "confidence-medium"
        emoji = "⚠️"
    else:
        class_name = "confidence-low"
        emoji = "❓"
    
    st.markdown(f"""
        <div class="confidence-badge {class_name}">
            {emoji} Confidence: <strong>{confidence}</strong>
        </div>
    """, unsafe_allow_html=True)

def render_status_message(message: str, type: str = "info"):
    """Render status message"""
    st.markdown(f"""
        <div class="status-message status-{type}">
            {message}
        </div>
    """, unsafe_allow_html=True)

def render_answer_section(answer: str):
    """Render answer in a prominent, readable format"""
    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    st.markdown("### 💬 Answer")
    st.markdown(f'<div style="font-size: 1.1rem; line-height: 1.8; color: #333;">{answer}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application logic"""
    
    # Render header
    render_header()
    
    # Initialize cached components
    system = get_doclingo_system()
    feedback_logger = get_feedback_logger()
    
    # ========================================================================
    # DOCUMENT UPLOAD SECTION
    # ========================================================================
    st.markdown("### 📤 Document Upload")
    
    uploaded_pdf = st.file_uploader(
        "Upload a PDF document to analyze",
        type=["pdf"],
        help="Upload any PDF document. DocLingo will analyze it and answer your questions.",
        label_visibility="collapsed"
    )
    
    # Show file info if uploaded
    if uploaded_pdf is not None:
        file_size_mb = len(uploaded_pdf.getvalue()) / (1024 * 1024)
        st.caption(f"📎 **{uploaded_pdf.name}** ({file_size_mb:.2f} MB)")
        
        # Compute file hash for caching and session state tracking
        file_bytes = uploaded_pdf.getvalue()
        file_hash = compute_file_hash(file_bytes)
        
        # Track current document in session state for optimization
        if 'current_file_hash' not in st.session_state or st.session_state.current_file_hash != file_hash:
            st.session_state.current_file_hash = file_hash
            st.session_state.document_processed = False
        
        # Process document (cached) - only show spinner if not already processed
        if not st.session_state.document_processed:
            with st.spinner("📄 Processing document..."):
                try:
                    doc_result = process_document_cached(file_bytes, file_hash)
                    pages = doc_result["pages"]
                    
                    if not pages:
                        st.error("⚠️ No readable content found in the document. Please upload a different PDF.")
                        st.stop()
                    
                    # Store in session state
                    st.session_state.document_processed = True
                    st.session_state.doc_result = doc_result
                    
                except Exception as e:
                    st.error(f"❌ Error processing document: {str(e)}")
                    st.stop()
        else:
            # Use cached result from session state
            doc_result = st.session_state.doc_result
        
        # Show document info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pages", doc_result["num_pages"])
        with col2:
            st.metric("Language", doc_result["document_language"].upper())
        with col3:
            if doc_result["metadata"].get("title"):
                st.caption(f"📑 {doc_result['metadata']['title'][:30]}...")
            else:
                st.caption("📄 Document ready")
    else:
        st.info("👆 Please upload a PDF document to get started.")
        st.stop()
    
    st.divider()
    
    # ========================================================================
    # LANGUAGE SETTINGS SECTION (Collapsible)
    # ========================================================================
    with st.expander("🌐 Language Settings (Optional)", expanded=False):
        st.caption("Customize language detection and output. Leave blank for automatic detection.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            user_doc_lang = st.selectbox(
                "Document Language",
                options=[None, "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", 
                         "hi", "ml", "ta", "te", "kn", "mr", "ur", "bn", "gu", "pa", "or", "as"],
                format_func=lambda x: "Auto-detect" if x is None else x.upper(),
                key="doc_lang",
                help="Specify the language of the document"
            )
        
        with col2:
            user_query_lang = st.selectbox(
                "Query Language",
                options=[None, "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar",
                         "hi", "ml", "ta", "te", "kn", "mr", "ur", "bn", "gu", "pa", "or", "as"],
                format_func=lambda x: "Auto-detect" if x is None else x.upper(),
                key="query_lang",
                help="Specify the language of your question"
            )
        
        with col3:
            user_answer_lang = st.selectbox(
                "Answer Language",
                options=[None, "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar",
                         "hi", "ml", "ta", "te", "kn", "mr", "ur", "bn", "gu", "pa", "or", "as"],
                format_func=lambda x: "Same as query" if x is None else x.upper(),
                key="answer_lang",
                help="Specify the language for the answer"
            )
    
    st.divider()
    
    # ========================================================================
    # QUERY INPUT SECTION
    # ========================================================================
    st.markdown("### ❓ Ask a Question")
    
    query = st.text_input(
        "Enter your question about the document",
        placeholder="e.g., What is the main topic of this document?",
        help="Ask any question about the uploaded document",
        label_visibility="collapsed"
    )
    
    if not query:
        st.info("💡 Enter a question above to get started.")
        st.stop()
    
    # ========================================================================
    # PROCESSING AND ANSWER GENERATION
    # ========================================================================
    st.divider()
    
    # Create a container for status updates
    status_container = st.empty()
    
    # Process query
    with st.spinner("🤔 Analyzing your question..."):
        try:
            start_time = time.time()
            
            # Show processing status
            status_container.info("🔍 Processing query... This may take a few moments.")
            
            # Run DocLingo pipeline
            result = run_doclingo(
                uploaded_pdf,
                query,
                user_doc_lang=user_doc_lang,
                user_query_lang=user_query_lang,
                user_answer_lang=user_answer_lang
            )
            
            processing_time = time.time() - start_time
            
            # Clear status
            status_container.empty()
            
        except Exception as e:
            status_container.empty()
            st.error(f"❌ Error processing query: {str(e)}")
            st.exception(e)
            st.stop()
    
    # ========================================================================
    # ANSWER DISPLAY SECTION
    # ========================================================================
    st.markdown("## 📋 Results")
    
    # Render answer prominently
    render_answer_section(result.get("answer", "No answer generated."))
    
    # Confidence score
    st.markdown("<br>", unsafe_allow_html=True)
    confidence = result.get("confidence", "Unknown")
    render_confidence_badge(confidence)
    
    # Processing time (subtle)
    st.caption(f"⏱️ Processed in {processing_time:.2f} seconds")
    
    st.divider()
    
    # ========================================================================
    # EXPLANATION SECTION (Collapsible)
    # ========================================================================
    with st.expander("ℹ️ Why this answer? (Explanation)", expanded=False):
        explanation_text = result.get("explanation_text", "No explanation available.")
        st.markdown(f'<div style="line-height: 1.6;">{explanation_text}</div>', unsafe_allow_html=True)
        
        # Additional metadata if available
        if result.get("language_resolution"):
            st.markdown("---")
            st.caption("**Language Detection:**")
            lang_res = result.get("language_resolution", {})
            if lang_res.get("resolution_explanation"):
                st.caption(lang_res["resolution_explanation"])
    
    # ========================================================================
    # OPTIMIZATION INFO (Collapsible, if available)
    # ========================================================================
    if result.get("optimization_applied"):
        with st.expander("📊 Feedback-Based Optimization", expanded=False):
            opt_info = result.get("optimization_applied", {})
            st.caption("This answer was optimized based on previous user feedback.")
            if result.get("optimization_explanation"):
                st.caption(result["optimization_explanation"])
    
    # ========================================================================
    # CONFIDENCE CALIBRATION INFO (Collapsible, if available)
    # ========================================================================
    if result.get("calibrated_confidence_info"):
        with st.expander("🎯 Confidence Calibration", expanded=False):
            st.caption(result.get("calibrated_confidence_info", ""))
    
    st.divider()
    
    # ========================================================================
    # FEEDBACK SECTION
    # ========================================================================
    st.markdown("### 📝 Rate this Answer")
    st.caption("Help improve DocLingo by rating the quality of this answer")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        rating = st.slider(
            "Rating",
            min_value=1,
            max_value=10,
            value=5,
            step=1,
            key="feedback_rating",
            help="1 = Poor, 5 = Average, 10 = Excellent"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        submit_feedback = st.button("Submit Feedback", type="primary", use_container_width=True)
    
    if submit_feedback:
        with st.spinner("💾 Saving feedback..."):
            try:
                success = feedback_logger.log_feedback_from_result(
                    rating=rating,
                    query=query,
                    result=result
                )
                
                if success:
                    st.success(f"✅ Thank you! Your feedback (rating: {rating}/10) has been recorded.")
                    time.sleep(1)
                    st.rerun()  # Refresh to show updated state
                else:
                    st.error("❌ Failed to save feedback. Please try again.")
            except Exception as e:
                st.error(f"❌ Error saving feedback: {str(e)}")

# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    main()
