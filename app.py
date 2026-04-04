# """
# DocLingo - Phase 6: Enhanced UI/UX with Performance Optimizations
# Clean, professional interface with intelligent caching for speed.
# """

# import streamlit as st
# import hashlib
# import time
# from typing import Optional, Dict, Any
# from io import BytesIO

# from main import run_doclingo, DocLingoSystem
# from feedback_manager.feedback_logger import FeedbackLogger

# # ============================================================================
# # PAGE CONFIGURATION
# # ============================================================================
# st.set_page_config(
#     page_title="DocLingo",
#     page_icon="📄",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # ============================================================================
# # CUSTOM CSS FOR CLEAN UI
# # ============================================================================
# st.markdown("""
#     <style>
#         /* Main container styling */
#         .main .block-container {
#             padding-top: 2rem;
#             padding-bottom: 2rem;
#         }
        
#         /* Header styling */
#         h1 {
#             color: #1f4788;
#             border-bottom: 3px solid #4a90e2;
#             padding-bottom: 0.5rem;
#             margin-bottom: 1.5rem;
#         }
        
#         /* Answer box styling */
#         .answer-box {
#             background-color: #f8f9fa;
#             padding: 1.5rem;
#             border-radius: 8px;
#             border-left: 4px solid #4a90e2;
#             margin: 1rem 0;
#         }
        
#         /* Confidence badge styling */
#         .confidence-badge {
#             display: inline-block;
#             padding: 0.5rem 1rem;
#             border-radius: 20px;
#             font-weight: 600;
#             margin: 0.5rem 0;
#         }
        
#         .confidence-high {
#             background-color: #d4edda;
#             color: #155724;
#         }
        
#         .confidence-medium {
#             background-color: #fff3cd;
#             color: #856404;
#         }
        
#         .confidence-low {
#             background-color: #f8d7da;
#             color: #721c24;
#         }
        
#         /* Status messages */
#         .status-message {
#             padding: 0.75rem;
#             border-radius: 6px;
#             margin: 0.5rem 0;
#             font-size: 0.9rem;
#         }
        
#         .status-info {
#             background-color: #e7f3ff;
#             color: #004085;
#             border-left: 3px solid #004085;
#         }
        
#         /* Section dividers */
#         .section-divider {
#             margin: 2rem 0;
#             border-top: 2px solid #e0e0e0;
#         }
        
#         /* Hide Streamlit default elements */
#         #MainMenu {visibility: hidden;}
#         footer {visibility: hidden;}
#         header {visibility: hidden;}
#     </style>
# """, unsafe_allow_html=True)

# # ============================================================================
# # PERFORMANCE: CACHED FUNCTIONS
# # ============================================================================

# @st.cache_resource
# def get_doclingo_system() -> DocLingoSystem:
#     """Cache the DocLingo system instance (expensive to initialize)"""
#     return DocLingoSystem()

# @st.cache_resource
# def get_feedback_logger() -> FeedbackLogger:
#     """Cache the feedback logger instance"""
#     return FeedbackLogger()

# def compute_file_hash(file_bytes: bytes) -> str:
#     """Compute hash of file for caching purposes"""
#     return hashlib.md5(file_bytes).hexdigest()

# @st.cache_data
# def process_document_cached(file_bytes: bytes, file_hash: str) -> Dict[str, Any]:
#     """
#     Cache document processing results.
#     Uses file_hash as part of cache key to ensure cache invalidation on file change.
#     Only caches serializable data (pages, metadata), not reader objects.
#     """
#     from document_processor.pdf_loader import load_pdf
#     from document_processor.text_extractor import extract_text_from_reader
#     from language_manager.language_detector import detect_language
    
#     # Create a file-like object from bytes
#     pdf_file = BytesIO(file_bytes)
    
#     # Load and extract
#     reader = load_pdf(pdf_file)
#     pages = extract_text_from_reader(reader)
    
#     if not pages:
#         return {
#             "pages": [],
#             "document_language": "en",
#             "num_pages": 0,
#             "metadata": {}
#         }
    
#     # Detect language (cached separately)
#     document_language = detect_language(pages[0])
    
#     # Extract metadata (only serializable data)
#     metadata = {"page_count": len(pages)}
#     try:
#         if hasattr(reader, 'metadata') and reader.metadata:
#             if reader.metadata.get('/Title'):
#                 metadata['title'] = str(reader.metadata.get('/Title'))
#             if reader.metadata.get('/Author'):
#                 metadata['author'] = str(reader.metadata.get('/Author'))
#             if reader.metadata.get('/CreationDate'):
#                 metadata['date'] = str(reader.metadata.get('/CreationDate'))
#     except:
#         pass
    
#     # Return only serializable data (not reader object)
#     return {
#         "pages": pages,
#         "document_language": document_language,
#         "num_pages": len(pages),
#         "metadata": metadata
#     }

# @st.cache_data
# def detect_query_language_cached(query: str) -> str:
#     """Cache language detection for queries"""
#     from language_manager.language_detector import detect_language
#     return detect_language(query)

# # ============================================================================
# # UI COMPONENTS
# # ============================================================================

# def render_header():
#     """Render clean header"""
#     st.markdown("""
#         <div style="text-align: center; margin-bottom: 2rem;">
#             <h1>📄 DocLingo</h1>
#             <p style="color: #666; font-size: 1.1rem;">Intelligent Document Q&A System</p>
#         </div>
#     """, unsafe_allow_html=True)

# def render_confidence_badge(confidence: str):
#     """Render confidence badge with appropriate styling"""
#     confidence_lower = confidence.lower()
#     if "high" in confidence_lower:
#         class_name = "confidence-high"
#         emoji = "✅"
#     elif "medium" in confidence_lower:
#         class_name = "confidence-medium"
#         emoji = "⚠️"
#     else:
#         class_name = "confidence-low"
#         emoji = "❓"
    
#     st.markdown(f"""
#         <div class="confidence-badge {class_name}">
#             {emoji} Confidence: <strong>{confidence}</strong>
#         </div>
#     """, unsafe_allow_html=True)

# def render_status_message(message: str, type: str = "info"):
#     """Render status message"""
#     st.markdown(f"""
#         <div class="status-message status-{type}">
#             {message}
#         </div>
#     """, unsafe_allow_html=True)

# def render_answer_section(answer: str):
#     """Render answer in a prominent, readable format"""
#     st.markdown('<div class="answer-box">', unsafe_allow_html=True)
#     st.markdown("### 💬 Answer")
#     st.markdown(f'<div style="font-size: 1.1rem; line-height: 1.8; color: #333;">{answer}</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)

# # ============================================================================
# # MAIN APPLICATION
# # ============================================================================

# def main():
#     """Main application logic"""
    
#     # Render header
#     render_header()
    
#     # Initialize cached components
#     system = get_doclingo_system()
#     feedback_logger = get_feedback_logger()
    
#     # ========================================================================
#     # DOCUMENT UPLOAD SECTION
#     # ========================================================================
#     st.markdown("### 📤 Document Upload")
    
#     uploaded_pdf = st.file_uploader(
#         "Upload a PDF document to analyze",
#         type=["pdf"],
#         help="Upload any PDF document. DocLingo will analyze it and answer your questions.",
#         label_visibility="collapsed"
#     )
    
#     # Show file info if uploaded
#     if uploaded_pdf is not None:
#         file_size_mb = len(uploaded_pdf.getvalue()) / (1024 * 1024)
#         st.caption(f"📎 **{uploaded_pdf.name}** ({file_size_mb:.2f} MB)")
        
#         # Compute file hash for caching and session state tracking
#         file_bytes = uploaded_pdf.getvalue()
#         file_hash = compute_file_hash(file_bytes)
        
#         # Track current document in session state for optimization
#         if 'current_file_hash' not in st.session_state or st.session_state.current_file_hash != file_hash:
#             st.session_state.current_file_hash = file_hash
#             st.session_state.document_processed = False
        
#         # Process document (cached) - only show spinner if not already processed
#         if not st.session_state.document_processed:
#             with st.spinner("📄 Processing document..."):
#                 try:
#                     doc_result = process_document_cached(file_bytes, file_hash)
#                     pages = doc_result["pages"]
                    
#                     if not pages:
#                         st.error("⚠️ No readable content found in the document. Please upload a different PDF.")
#                         st.stop()
                    
#                     # Store in session state
#                     st.session_state.document_processed = True
#                     st.session_state.doc_result = doc_result
                    
#                 except Exception as e:
#                     st.error(f"❌ Error processing document: {str(e)}")
#                     st.stop()
#         else:
#             # Use cached result from session state
#             doc_result = st.session_state.doc_result
        
#         # Show document info
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.metric("Pages", doc_result["num_pages"])
#         with col2:
#             st.metric("Language", doc_result["document_language"].upper())
#         with col3:
#             if doc_result["metadata"].get("title"):
#                 st.caption(f"📑 {doc_result['metadata']['title'][:30]}...")
#             else:
#                 st.caption("📄 Document ready")
#     else:
#         st.info("👆 Please upload a PDF document to get started.")
#         st.stop()
    
#     st.divider()
    
#     # ========================================================================
#     # LANGUAGE SETTINGS SECTION (Collapsible)
#     # ========================================================================
#     with st.expander("🌐 Language Settings (Optional)", expanded=False):
#         st.caption("Customize language detection and output. Leave blank for automatic detection.")
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             user_doc_lang = st.selectbox(
#                 "Document Language",
#                 options=[None, "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", 
#                          "hi", "ml", "ta", "te", "kn", "mr", "ur", "bn", "gu", "pa", "or", "as"],
#                 format_func=lambda x: "Auto-detect" if x is None else x.upper(),
#                 key="doc_lang",
#                 help="Specify the language of the document"
#             )
        
#         with col2:
#             user_query_lang = st.selectbox(
#                 "Query Language",
#                 options=[None, "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar",
#                          "hi", "ml", "ta", "te", "kn", "mr", "ur", "bn", "gu", "pa", "or", "as"],
#                 format_func=lambda x: "Auto-detect" if x is None else x.upper(),
#                 key="query_lang",
#                 help="Specify the language of your question"
#             )
        
#         with col3:
#             user_answer_lang = st.selectbox(
#                 "Answer Language",
#                 options=[None, "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar",
#                          "hi", "ml", "ta", "te", "kn", "mr", "ur", "bn", "gu", "pa", "or", "as"],
#                 format_func=lambda x: "Same as query" if x is None else x.upper(),
#                 key="answer_lang",
#                 help="Specify the language for the answer"
#             )
    
#     st.divider()
    
#     # ========================================================================
#     # QUERY INPUT SECTION
#     # ========================================================================
#     st.markdown("### ❓ Ask a Question")
    
#     query = st.text_input(
#         "Enter your question about the document",
#         placeholder="e.g., What is the main topic of this document?",
#         help="Ask any question about the uploaded document",
#         label_visibility="collapsed"
#     )
    
#     if not query:
#         st.info("💡 Enter a question above to get started.")
#         st.stop()
    
#     # ========================================================================
#     # PROCESSING AND ANSWER GENERATION
#     # ========================================================================
#     st.divider()
    
#     # Create a container for status updates
#     status_container = st.empty()
    
#     # Process query
#     with st.spinner("🤔 Analyzing your question..."):
#         try:
#             start_time = time.time()
            
#             # Show processing status
#             status_container.info("🔍 Processing query... This may take a few moments.")
            
#             # Run DocLingo pipeline
#             result = run_doclingo(
#                 uploaded_pdf,
#                 query,
#                 user_doc_lang=user_doc_lang,
#                 user_query_lang=user_query_lang,
#                 user_answer_lang=user_answer_lang
#             )
            
#             processing_time = time.time() - start_time
            
#             # Clear status
#             status_container.empty()
            
#         except Exception as e:
#             status_container.empty()
#             st.error(f"❌ Error processing query: {str(e)}")
#             st.exception(e)
#             st.stop()
    
#     # ========================================================================
#     # ANSWER DISPLAY SECTION
#     # ========================================================================
#     st.markdown("## 📋 Results")
    
#     # Render answer prominently
#     render_answer_section(result.get("answer", "No answer generated."))
    
#     # Confidence score
#     st.markdown("<br>", unsafe_allow_html=True)
#     confidence = result.get("confidence", "Unknown")
#     render_confidence_badge(confidence)
    
#     # Processing time (subtle)
#     st.caption(f"⏱️ Processed in {processing_time:.2f} seconds")
    
#     st.divider()
    
#     # ========================================================================
#     # EXPLANATION SECTION (Collapsible)
#     # ========================================================================
#     with st.expander("ℹ️ Why this answer? (Explanation)", expanded=False):
#         explanation_text = result.get("explanation_text", "No explanation available.")
#         st.markdown(f'<div style="line-height: 1.6;">{explanation_text}</div>', unsafe_allow_html=True)
        
#         # Additional metadata if available
#         if result.get("language_resolution"):
#             st.markdown("---")
#             st.caption("**Language Detection:**")
#             lang_res = result.get("language_resolution", {})
#             if lang_res.get("resolution_explanation"):
#                 st.caption(lang_res["resolution_explanation"])
    
#     # ========================================================================
#     # OPTIMIZATION INFO (Collapsible, if available)
#     # ========================================================================
#     if result.get("optimization_applied"):
#         with st.expander("📊 Feedback-Based Optimization", expanded=False):
#             opt_info = result.get("optimization_applied", {})
#             st.caption("This answer was optimized based on previous user feedback.")
#             if result.get("optimization_explanation"):
#                 st.caption(result["optimization_explanation"])
    
#     # ========================================================================
#     # CONFIDENCE CALIBRATION INFO (Collapsible, if available)
#     # ========================================================================
#     if result.get("calibrated_confidence_info"):
#         with st.expander("🎯 Confidence Calibration", expanded=False):
#             st.caption(result.get("calibrated_confidence_info", ""))
    
#     st.divider()
    
#     # ========================================================================
#     # FEEDBACK SECTION
#     # ========================================================================
#     st.markdown("### 📝 Rate this Answer")
#     st.caption("Help improve DocLingo by rating the quality of this answer")
    
#     col1, col2 = st.columns([3, 1])
    
#     with col1:
#         rating = st.slider(
#             "Rating",
#             min_value=1,
#             max_value=10,
#             value=5,
#             step=1,
#             key="feedback_rating",
#             help="1 = Poor, 5 = Average, 10 = Excellent"
#         )
    
#     with col2:
#         st.markdown("<br>", unsafe_allow_html=True)
#         submit_feedback = st.button("Submit Feedback", type="primary", use_container_width=True)
    
#     if submit_feedback:
#         with st.spinner("💾 Saving feedback..."):
#             try:
#                 success = feedback_logger.log_feedback_from_result(
#                     rating=rating,
#                     query=query,
#                     result=result
#                 )
                
#                 if success:
#                     st.success(f"✅ Thank you! Your feedback (rating: {rating}/10) has been recorded.")
#                     time.sleep(1)
#                     st.rerun()  # Refresh to show updated state
#                 else:
#                     st.error("❌ Failed to save feedback. Please try again.")
#             except Exception as e:
#                 st.error(f"❌ Error saving feedback: {str(e)}")

# # ============================================================================
# # RUN APPLICATION
# # ============================================================================
# if __name__ == "__main__":
#     main()



"""
DocLingo - Phase 6: Enhanced UI/UX with Black & Golden Theme
Premium interface with animations and modern styling.
"""

import streamlit as st
import hashlib
import time
import os
from typing import Optional, Dict, Any
from io import BytesIO

from main import run_doclingo, DocLingoSystem
from feedback_manager.feedback_logger import FeedbackLogger
from utils.llm_client import get_current_chat_model, set_current_chat_model

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
# CUSTOM CSS FOR BLACK & GOLDEN THEME WITH ANIMATIONS
# ============================================================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        /* Global styling */
        * {
            font-family: 'Poppins', sans-serif;
        }
        
        /* Main container styling */
        .main {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        }
        
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* Animated header */
        .header-container {
            text-align: center;
            margin-bottom: 3rem;
            animation: fadeInDown 0.8s ease-out;
        }
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .main-title {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FFD700 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            text-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from {
                filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.5));
            }
            to {
                filter: drop-shadow(0 0 20px rgba(255, 215, 0, 0.8));
            }
        }
        
        .subtitle {
            color: #FFD700;
            font-size: 1.2rem;
            font-weight: 300;
            letter-spacing: 2px;
        }
        
        /* Section headers */
        .section-header {
            color: #FFD700;
            font-size: 1.8rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #FFD700;
            animation: slideInLeft 0.6s ease-out;
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Answer box with premium styling */
        .answer-box {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            padding: 2rem;
            border-radius: 15px;
            border: 2px solid #FFD700;
            margin: 1.5rem 0;
            box-shadow: 0 8px 32px rgba(255, 215, 0, 0.2);
            animation: fadeInUp 0.8s ease-out;
            position: relative;
            overflow: hidden;
        }
        
        .answer-box::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 215, 0, 0.1) 0%, transparent 70%);
            animation: rotateGlow 10s linear infinite;
        }
        
        @keyframes rotateGlow {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .answer-header {
            color: #FFD700;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            position: relative;
            z-index: 1;
        }
        
        .answer-text {
            font-size: 1.15rem;
            line-height: 1.9;
            color: #e0e0e0;
            position: relative;
            z-index: 1;
        }
        
        /* Confidence badges */
        .confidence-container {
            display: inline-block;
            animation: fadeIn 1s ease-out 0.5s both;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .confidence-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: 25px;
            font-weight: 600;
            font-size: 1.1rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
            cursor: default;
        }
        
        .confidence-badge:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(255, 215, 0, 0.4);
        }
        
        .confidence-high {
            background: linear-gradient(135deg, #1a4d1a 0%, #2d7a2d 100%);
            border: 2px solid #4CAF50;
            color: #90EE90;
        }
        
        .confidence-medium {
            background: linear-gradient(135deg, #4d3d1a 0%, #7a6a2d 100%);
            border: 2px solid #FFA500;
            color: #FFD700;
        }
        
        .confidence-low {
            background: linear-gradient(135deg, #4d1a1a 0%, #7a2d2d 100%);
            border: 2px solid #FF6347;
            color: #FFB6C1;
        }
        
        /* Expandable sections */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border: 1px solid #FFD700;
            border-radius: 10px;
            color: #FFD700 !important;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background: linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%);
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
            transform: translateY(-2px);
        }
        
        .streamlit-expanderContent {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 0 0 10px 10px;
            color: #e0e0e0;
        }
        
        /* Input fields */
        .stTextInput input {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border: 2px solid #FFD700;
            border-radius: 10px;
            color: #FFD700;
            font-size: 1.1rem;
            padding: 0.75rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus {
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
            border-color: #FFA500;
        }
        
        /* File uploader */
        .stFileUploader {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border: 2px dashed #FFD700;
            border-radius: 15px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }
        
        .stFileUploader:hover {
            border-color: #FFA500;
            background: linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%);
        }
        
        /* Metrics */
        div[data-testid="metric-container"] {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border: 1px solid #FFD700;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
            animation: scaleIn 0.5s ease-out;
        }
        
        @keyframes scaleIn {
            from {
                opacity: 0;
                transform: scale(0.9);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        div[data-testid="metric-container"] label {
            color: #FFD700 !important;
        }
        
        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #FFA500 !important;
        }
        
        /* Buttons */
        .stButton button {
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: #000;
            border: none;
            border-radius: 25px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
        }
        
        .stButton button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 25px rgba(255, 215, 0, 0.6);
            background: linear-gradient(135deg, #FFA500 0%, #FFD700 100%);
        }
        
        /* Feedback buttons */
        .feedback-buttons {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin: 1rem 0;
        }
        
        .feedback-btn {
            flex: 1;
            min-width: 80px;
            padding: 1rem;
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border: 2px solid #FFD700;
            border-radius: 15px;
            color: #FFD700;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            font-size: 1.2rem;
        }
        
        .feedback-btn:hover {
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: #000;
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.5);
        }
        
        .feedback-btn.selected {
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: #000;
            border-color: #FFA500;
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.6);
        }
        
        /* Dividers */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #FFD700, transparent);
            margin: 2rem 0;
            animation: slideIn 1s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: scaleX(0);
            }
            to {
                opacity: 1;
                transform: scaleX(1);
            }
        }
        
        /* Info boxes */
        .stAlert {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border-left: 4px solid #FFD700;
            border-radius: 10px;
            color: #e0e0e0;
            animation: fadeInLeft 0.6s ease-out;
        }
        
        @keyframes fadeInLeft {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Select boxes */
        .stSelectbox select {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border: 2px solid #FFD700;
            border-radius: 10px;
            color: #FFD700;
        }
        
        /* Captions */
        .stCaption {
            color: #999 !important;
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: linear-gradient(135deg, #1a4d1a 0%, #2d7a2d 100%);
            border-left: 4px solid #4CAF50;
            animation: slideInRight 0.5s ease-out;
        }
        
        .stError {
            background: linear-gradient(135deg, #4d1a1a 0%, #7a2d2d 100%);
            border-left: 4px solid #FF6347;
            animation: shake 0.5s ease-out;
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Processing spinner */
        .stSpinner > div {
            border-top-color: #FFD700 !important;
        }
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
    """Render premium animated header"""
    st.markdown("""
        <div class="header-container">
            <div class="main-title">📄 DocLingo</div>
            <div class="subtitle">INTELLIGENT DOCUMENT Q&A SYSTEM</div>
        </div>
    """, unsafe_allow_html=True)

def render_confidence_badge(confidence: str):
    """Render animated confidence badge"""
    confidence_lower = confidence.lower()
    if "high" in confidence_lower:
        class_name = "confidence-high"
        emoji = "✅"
    elif "medium" in confidence_lower:
        class_name = "confidence-medium"
        emoji = "⚠️"
    else:
        class_name = "confidence-low"
        emoji = "❌"
    
    st.markdown(f"""
        <div class="confidence-container">
            <div class="confidence-badge {class_name}">
                <span>{emoji}</span>
                <span>Confidence: <strong>{confidence}</strong></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_section_header(text: str):
    """Render animated section header"""
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)

def render_answer_section(answer: str):
    """Render answer in premium animated box"""
    st.markdown(f"""
        <div class="answer-box">
            <div class="answer-header">
                💬 Answer
            </div>
            <div class="answer-text">{answer}</div>
        </div>
    """, unsafe_allow_html=True)

def render_feedback_buttons():
    """Render click-based feedback buttons"""
    st.markdown('<div class="section-header">📝 Rate this Answer</div>', unsafe_allow_html=True)
    st.caption("Click a number to rate the quality of this answer")
    
    # Initialize session state for selected rating
    if 'selected_rating' not in st.session_state:
        st.session_state.selected_rating = None
    
    # Create 10 columns for ratings 1-10
    cols = st.columns(10)
    
    for i, col in enumerate(cols):
        rating_value = i + 1
        with col:
            button_class = "selected" if st.session_state.selected_rating == rating_value else ""
            if st.button(str(rating_value), key=f"rating_{rating_value}", use_container_width=True):
                st.session_state.selected_rating = rating_value
    
    # Display selected rating
    if st.session_state.selected_rating:
        st.markdown(f"""
            <div style="text-align: center; margin: 1rem 0; color: #FFD700; font-size: 1.2rem;">
                Selected Rating: <strong>{st.session_state.selected_rating}/10</strong>
            </div>
        """, unsafe_allow_html=True)
    
    return st.session_state.selected_rating

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
    render_section_header("📤 Document Upload")
    
    uploaded_pdf = st.file_uploader(
        "Upload a PDF document to analyze",
        type=["pdf"],
        help="Upload any PDF document. DocLingo will analyze it and answer your questions.",
        label_visibility="collapsed"
    )
    
    # Show file info if uploaded
    if uploaded_pdf is not None:
        file_size_mb = len(uploaded_pdf.getvalue()) / (1024 * 1024)
        st.caption(f"🔍 **{uploaded_pdf.name}** ({file_size_mb:.2f} MB)")
        
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
    # MODEL SETTINGS SECTION (Collapsible)
    # ========================================================================
    with st.expander("🤖 Model Settings", expanded=False):
        st.caption("Choose your LLM provider and model. Default: OpenAI gpt-4o-mini.")

        col_model, col_key = st.columns([2, 2])

        with col_model:
            # Preset model options
            model_options = {
                "gpt-4o-mini (OpenAI)": "gpt-4o-mini",
                "gpt-4o (OpenAI)": "gpt-4o",
                "gemini/gemini-2.0-flash (Google)": "gemini/gemini-2.0-flash",
                "ollama/llama3 (Local)": "ollama/llama3",
                "Custom": "custom",
            }
            selected_label = st.selectbox(
                "LLM Model",
                options=list(model_options.keys()),
                key="model_select",
                help="Select the LLM model/provider to use for answering questions",
            )
            selected_model = model_options[selected_label]

            if selected_model == "custom":
                custom_model = st.text_input(
                    "Custom model name",
                    placeholder="e.g., ollama/mistral, anthropic/claude-3-haiku",
                    key="custom_model_input",
                )
                if custom_model:
                    selected_model = custom_model

            # Apply model selection
            if selected_model != "custom":
                set_current_chat_model(selected_model)

        with col_key:
            # Provider API key input
            provider_key_name = "OPENAI_API_KEY"
            if "gemini" in selected_model:
                provider_key_name = "GEMINI_API_KEY"
            elif "anthropic" in selected_model or "claude" in selected_model:
                provider_key_name = "ANTHROPIC_API_KEY"
            elif "ollama" in selected_model:
                provider_key_name = ""

            if provider_key_name:
                api_key_input = st.text_input(
                    f"{provider_key_name}",
                    type="password",
                    value=os.getenv(provider_key_name, ""),
                    key="api_key_input",
                    help=f"Enter your API key for the selected provider (or set {provider_key_name} in .env)",
                )
                if api_key_input:
                    os.environ[provider_key_name] = api_key_input
            else:
                st.info("No API key needed for local Ollama models.")

        st.caption(f"Active model: **{get_current_chat_model()}**")

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
    render_section_header("❓ Ask a Question")
    
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
    # RESULTS SECTION
    # ========================================================================
    render_section_header("📋 Results")
    
    # Render answer prominently
    render_answer_section(result.get("answer", "No answer generated."))
    
    # Confidence score
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("🎯 Confidence Level")
    confidence = result.get("confidence", "Unknown")
    render_confidence_badge(confidence)
    
    # Processing time and model info (subtle)
    st.caption(f"⏱️ Processed in {processing_time:.2f} seconds | Model: {get_current_chat_model()}")
    
    st.divider()
    
    # ========================================================================
    # EXPLANATION SECTION (Collapsible)
    # ========================================================================
    with st.expander("ℹ️ Explanation - Why this answer?", expanded=False):
        explanation_text = result.get("explanation_text", "No explanation available.")
        st.markdown(f'<div style="line-height: 1.6; color: #e0e0e0;">{explanation_text}</div>', unsafe_allow_html=True)
        
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
        with st.expander("🎯 Confidence Calibration Details", expanded=False):
            st.caption(result.get("calibrated_confidence_info", ""))
    
    st.divider()
    
    # ========================================================================
    # FEEDBACK SECTION - Click-based
    # ========================================================================
    selected_rating = render_feedback_buttons()
    
    # Submit button
    if selected_rating:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_feedback = st.button("✨ Submit Feedback", type="primary", use_container_width=True)
        
        if submit_feedback:
            with st.spinner("💾 Saving feedback..."):
                try:
                    success = feedback_logger.log_feedback_from_result(
                        rating=selected_rating,
                        query=query,
                        result=result
                    )
                    
                    if success:
                        st.success(f"✅ Thank you! Your feedback (rating: {selected_rating}/10) has been recorded.")
                        st.session_state.selected_rating = None  # Reset selection
                        time.sleep(1.5)
                        st.rerun()  # Refresh to show updated state
                    else:
                        st.error("❌ Failed to save feedback. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error saving feedback: {str(e)}")
    else:
        st.info("👆 Please select a rating above to submit feedback.")

# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    main()