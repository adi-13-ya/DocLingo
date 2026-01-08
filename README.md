# DocLingo: Intelligent Multilingual Document Q&A System

<div align="center">

![DocLingo](https://img.shields.io/badge/DocLingo-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**An intelligent, adaptive, and safe document question-answering system with multilingual support, FAISS-powered semantic search, and feedback-driven learning.**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#-project-structure)
- [Key Components](#-key-components)
- [Advanced Features](#-advanced-features)
- [Performance Optimizations](#-performance-optimizations)
- [Configuration](#configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## Overview

**DocLingo** is a production-ready document intelligence system that enables users to ask questions about documents in any language and receive accurate, grounded answers. The system combines:

- **Intelligent Query Routing**: 3-tier architecture (Programmatic → Specialized LLM → General LLM)
- **FAISS Semantic Search**: Vector-based retrieval for improved answer quality
- **Multilingual Support**: 20+ languages including Indian languages (Hindi, Telugu, Tamil, etc.)
- **Safety & Governance**: Comprehensive validation, uncertainty handling, and audit logging
- **Adaptive Learning**: Feedback-driven optimization without retraining models
- **Professional UI**: Clean, responsive Streamlit interface with performance caching

---

## ✨ Features

### 🎯 Core Capabilities

- **Intelligent Intent Classification**: Automatically routes queries to the most appropriate engine
- **Multi-Engine Architecture**: 14 specialized engines for different query types
- **Zero Hallucination**: Programmatic engines for metadata, counting, and analytical queries
- **Document-Grounded Answers**: All answers strictly based on document content
- **Explainability**: Clear explanations of how answers were generated
- **Confidence Scoring**: Transparent confidence levels with feedback-based calibration

### 🌍 Multilingual Support

- **20+ Languages**: English, Spanish, French, German, Hindi, Telugu, Tamil, Malayalam, Bengali, and more
- **Automatic Language Detection**: Detects document and query languages
- **Explicit Language Selection**: Users can specify preferred languages
- **Native Language Answers**: Answers generated in the query language or user-selected language
- **Multilingual Error Messages**: All system messages translated to match query language

### 🔍 Advanced Retrieval

- **FAISS Semantic Search**: Vector-based similarity search for relevant content
- **Adaptive Retrieval Depth**: Optimized based on feedback history
- **Hybrid Retrieval**: Combines semantic search with keyword fallback
- **Chunk-Level Relevance**: Scores and ranks document sections by relevance

### 🛡️ Safety & Governance 

- **Query Safety Checks**: Detects and prevents prompt injection attacks
- **Output Validation**: Ensures answers are grounded in retrieved content
- **Uncertainty Handling**: Explicitly communicates when confidence is low
- **Audit Logging**: Comprehensive logs of all system decisions
- **Policy Enforcement**: Centralized safety policy management

### 📊 Adaptive Learning 

- **Feedback Collection**: Users can rate answers (1-10 scale)
- **Strategy Optimization**: System adapts retrieval depth and strategies based on feedback
- **Confidence Calibration**: Adjusts confidence scores using historical performance
- **Performance Analytics**: Tracks effectiveness by intent, engine, and strategy
- **Deterministic & Explainable**: All optimizations are transparent and auditable

### 🎨 Enhanced UI/UX 

- **Professional Design**: Clean, modern interface suitable for academic and professional use
- **Performance Caching**: Intelligent caching of document processing and embeddings
- **Loading Indicators**: Clear status messages during processing
- **Responsive Layout**: Works well on different screen sizes
- **Collapsible Sections**: Organized display of explanations and metadata

### 📄 Advanced PDF Processing

- **PDF Plumber Integration**: Better text and table extraction
- **OCR Support**: Handles scanned/image-based PDFs using Tesseract
- **Automatic Fallback**: Gracefully falls back to PyPDF2 if advanced libraries unavailable
- **Table Extraction**: Preserves table structure from PDFs

---

## 🏗️ Architecture

### 3-Tier Query Routing

```
┌─────────────────────────────────────────────────────────────┐
│                     User Query                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Intent Classifier   │
            └──────────┬───────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   TIER 1          TIER 2          TIER 3
 (Fast, Free)  (Specialized)    (General LLM)
        │              │              │
        ▼              ▼              ▼
  Metadata      Summarization    Content Engine
  Aggregate     Comparison       (Fallback)
  Analytical    Interpretation
                Causation
                Procedural
                etc.
```

### System Flow

```
Document Upload
    ↓
PDF Processing (PDF Plumber/OCR)
    ↓
Text Extraction & Chunking
    ↓
FAISS Indexing (Embeddings)
    ↓
Query Safety Check
    ↓
Intent Classification
    ↓
Query Routing (3-Tier)
    ↓
Semantic Retrieval (FAISS)
    ↓
Answer Generation (LLM)
    ↓
Output Validation
    ↓
Uncertainty Handling
    ↓
Final Answer + Explanation
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd doclingo_cursor

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install enhanced dependencies for OCR support
pip install -r requirements_enhanced.txt
```

### 2. Set Up OpenAI API Key

```bash
# Linux/Mac
export OPENAI_API_KEY='your-api-key-here'

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"

# Or create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 3. Run the Streamlit App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 4. Basic Usage

1. Upload a PDF document
2. Enter your question (in any language)
3. Optionally select languages for document, query, or answer
4. View the answer with explanation and confidence score
5. Rate the answer to help improve the system

---

## 📦 Installation

### Requirements

**Core Dependencies:**
- Python 3.8+
- Streamlit >= 1.28.0
- OpenAI >= 1.0.0
- FAISS-CPU >= 1.7.4
- PyPDF2 >= 3.0.0
- langdetect >= 1.0.9
- deep-translator >= 1.11.4
- python-dotenv >= 1.0.0

**Enhanced Dependencies (Optional):**
- pdfplumber >= 0.10.0 (better PDF extraction)
- pytesseract >= 0.3.10 (OCR support)
- Pillow >= 10.0.0 (image processing)

**System Requirements for OCR:**
- macOS: `brew install tesseract`
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- Windows: Download from [Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)

### Installation Steps

```bash
# Install all core dependencies
pip install -r requirements.txt

# For enhanced PDF processing (optional)
pip install -r requirements_enhanced.txt
```

---

## 💻 Usage

### Using the Streamlit UI

The easiest way to use DocLingo is through the web interface:

```bash
streamlit run app.py
```

**Features:**
- Drag-and-drop PDF upload
- Real-time language detection
- Interactive language selection
- Feedback submission (1-10 rating)
- Cached document processing for speed

### Programmatic Usage

```python
from main import run_doclingo

# Process a PDF and ask questions
result = run_doclingo(
    pdf_file="document.pdf",
    query="What is the main topic of this document?",
    user_doc_lang=None,      # Auto-detect
    user_query_lang=None,    # Auto-detect
    user_answer_lang=None    # Same as query
)

print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
print(f"Explanation: {result['explanation_text']}")
```

### Using the DocLingoSystem Class

```python
from main import DocLingoSystem
from document_processor.pdf_loader import load_pdf
from document_processor.text_extractor import extract_text_from_reader

# Initialize system
system = DocLingoSystem()

# Load document
reader = load_pdf("document.pdf")
pages = extract_text_from_reader(reader)

# Index document for FAISS search
system.index_document(pages, chunk_size=500, chunk_overlap=50)

# Query the document
result = run_doclingo(
    pdf_file="document.pdf",
    query="Summarize this document in 150 words",
    user_answer_lang="en"
)
```

### Multilingual Usage

```python
# Ask in Telugu, get answer in Telugu
result = run_doclingo(
    pdf_file="document.pdf",
    query="ఈ పత్రాన్ని 150 పదాలలో సంగ్రహించగలరా?",
    user_answer_lang="te"  # Telugu
)

# Ask in Hindi, get answer in Hindi
result = run_doclingo(
    pdf_file="document.pdf",
    query="इस दस्तावेज़ में कितने पृष्ठ हैं?",
    user_query_lang="hi",
    user_answer_lang="hi"
)
```

---

## 📁 Project Structure

```
doclingo_cursor/
├── app.py                          # Streamlit web application
├── main.py                         # Main pipeline and DocLingoSystem
├── requirements.txt                # Core dependencies
├── requirements_enhanced.txt       # Enhanced dependencies (optional)
│
├── answer_engine/                  # Answer generation
│   ├── generator.py               # LLM-based answer generation
│   └── explainer.py               # Explanation generation
│
├── confidence_engine/              # Confidence scoring
│   ├── confidence_score.py        # Base confidence calculation
│   └── confidence_calibrator.py   # Feedback-based calibration
│
├── decision_engine/                # Adaptive decision making
│   ├── adaptive_engine.py         # Translation strategy decisions
│   └── strategy_optimizer.py      # Feedback-driven optimization
│
├── document_processor/             # Document processing
│   ├── pdf_loader.py              # PDF loading (PDF Plumber/PyPDF2)
│   ├── text_extractor.py          # Text extraction (with OCR support)
│   └── chunker.py                 # Text chunking with overlap
│
├── feedback_manager/               # Feedback learning (Phase 4)
│   ├── feedback_logger.py         # Feedback collection
│   └── feedback_analyzer.py       # Feedback analytics
│
├── language_manager/               # Language handling
│   ├── language_detector.py       # Language detection
│   ├── language_resolver.py       # Language resolution logic
│   ├── translation_manager.py     # Translation handling
│   └── multilingual_messages.py   # Multilingual UI messages
│
├── query_engine/                   # Query processing (14 engines)
│   ├── router.py                  # Central query router
│   ├── intent_classifier.py       # Intent classification
│   ├── metadata_engine.py         # Metadata queries (programmatic)
│   ├── aggregate_engine.py        # Counting queries (programmatic)
│   ├── analytical_engine.py       # Analytical queries (programmatic)
│   ├── content_engine.py          # General content (LLM)
│   ├── summarization_engine.py    # Summarization (LLM + FAISS)
│   ├── comparison_engine.py       # Comparison (LLM + FAISS)
│   ├── causation_engine.py        # Cause-effect (LLM + FAISS)
│   ├── interpretation_engine.py   # Interpretation (LLM + FAISS)
│   ├── opinion_stance_engine.py   # Opinion/stance (LLM + FAISS)
│   ├── critical_analysis_engine.py # Critical analysis (LLM + FAISS)
│   ├── procedural_engine.py       # How-to queries (LLM + FAISS)
│   └── contextual_engine.py       # Context queries (LLM + FAISS)
│
├── retrieval_engine/               # Retrieval system
│   └── retriever.py               # FAISSRetriever class
│
├── safety_engine/                  # Safety & governance (Phase 5)
│   ├── policy_enforcer.py         # Central safety enforcement
│   ├── query_guard.py             # Query validation
│   ├── output_guard.py            # Answer validation
│   ├── uncertainty_handler.py     # Uncertainty detection
│   └── audit_logger.py            # Audit logging
│
├── vector_store/                   # Vector operations
│   ├── embedding_manager.py       # OpenAI embeddings
│   └── faiss_index.py             # FAISS index management
│
└── utils/                          # Utilities
    └── helpers.py                 # Helper functions
```

---

## 🔧 Key Components

### Query Engines (14 Total)

**TIER 1 - Programmatic (Fast, No LLM):**
- `metadata_engine.py`: Document properties (page count, author, date)
- `aggregate_engine.py`: Counting and frequency analysis
- `analytical_engine.py`: Calculations and statistical analysis

**TIER 2 - Specialized LLM (High Quality):**
- `summarization_engine.py`: Document summaries
- `comparison_engine.py`: Compare entities/concepts
- `causation_engine.py`: Cause-effect relationships
- `interpretation_engine.py`: Explain meanings
- `opinion_stance_engine.py`: Identify positions/arguments
- `critical_analysis_engine.py`: Limitations and weaknesses
- `procedural_engine.py`: Step-by-step instructions
- `contextual_engine.py`: Context-based queries

**TIER 3 - General LLM (Fallback):**
- `content_engine.py`: General content queries

### Safety & Governance

- **Query Guard**: Validates and sanitizes user queries
- **Output Guard**: Ensures answers are grounded and safe
- **Uncertainty Handler**: Detects and handles low-confidence cases
- **Audit Logger**: Comprehensive logging of all system decisions
- **Policy Enforcer**: Centralized safety policy management

### Feedback Learning System

- **Feedback Logger**: Collects user ratings with rich metadata
- **Feedback Analyzer**: Analyzes feedback patterns and effectiveness
- **Strategy Optimizer**: Adapts retrieval depth and strategies
- **Confidence Calibrator**: Adjusts confidence scores based on history

---

## 🚀 Advanced Features

### Feedback-Driven Optimization

The system learns from user feedback to improve over time:

```python
# After users rate answers, the system automatically:
# 1. Identifies best-performing strategies
# 2. Adjusts retrieval depth based on feedback
# 3. Calibrates confidence scores
# 4. Optimizes translation strategies
```

### Safety & Audit Logging

All queries and decisions are logged for audit:

```python
# Logs are stored in audit_log.jsonl
# Each entry includes:
# - Query and answer
# - Safety decisions
# - Confidence scores
# - Retrieval method
# - Engine used
```

### Advanced PDF Processing

Supports various PDF types:

```python
# Text-based PDFs: Uses PDF Plumber (if available)
# Scanned PDFs: Automatically uses OCR (if Tesseract installed)
# Fallback: Uses PyPDF2 if advanced libraries unavailable
```

---

## ⚡ Performance Optimizations

### Caching Strategy

- **Document Processing**: Cached based on file hash
- **FAISS Index**: Reused for same document across queries
- **Embeddings**: Cached to avoid recomputation
- **Language Detection**: Cached for repeated queries
- **System Initialization**: Resource caching for faster startup

### Optimization Tips

1. **First Query**: Normal processing time (indexing + retrieval)
2. **Subsequent Queries**: Much faster (cached index and embeddings)
3. **Same Document Re-upload**: Instant (cached processing)
4. **Batch Queries**: Efficient processing with shared resources

---

## ⚙️ Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional
LOG_LEVEL=INFO
FAISS_INDEX_TYPE=flat  # flat, ivf, hnsw
EMBEDDING_MODEL=text-embedding-3-small
```

### System Configuration

Edit `main.py` to customize:

```python
# FAISS configuration
retriever = FAISSRetriever(
    embedding_model="text-embedding-3-small",  # or "text-embedding-3-large"
    index_type="flat"  # "flat", "ivf", or "hnsw"
)

# Chunking configuration
system.index_document(
    pages,
    chunk_size=500,      # Characters per chunk
    chunk_overlap=50     # Overlap between chunks
)
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "OpenAI API key not set"**
```bash
# Solution: Set environment variable
export OPENAI_API_KEY='your-key-here'
```

**Issue: "ModuleNotFoundError: No module named 'pdfplumber'"**
```bash
# Solution: Install enhanced requirements
pip install -r requirements_enhanced.txt
# Or continue with PyPDF2 fallback (works but less accurate)
```

**Issue: "OCR not working"**
```bash
# Solution: Install Tesseract OCR
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
```

**Issue: "Output validation fails for multilingual answers"**
- ✅ Fixed in latest version: Language-aware validation now properly handles non-English content

**Issue: "Slow performance"**
- Use caching (enabled by default in Streamlit app)
- Reuse same document for multiple queries
- Consider using `gpt-4o-mini` instead of `gpt-4`

### Debug Mode

Enable verbose logging:

```python
# In main.py or your script
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 Query Types Supported

### Metadata Queries
- "How many pages does this document have?"
- "Who is the author?"
- "When was this document created?"

### Aggregate Queries
- "How many tables are in the document?"
- "Count the number of sections"
- "How many references are cited?"

### Analytical Queries
- "How old is this document?"
- "What is the average length of sections?"
- "What percentage of the document is in English?"

### Content Queries
- "What is the main topic?"
- "Summarize this document"
- "What are the key findings?"

### Comparison Queries
- "Compare X and Y"
- "What are the differences between A and B?"

### Procedural Queries
- "How do I perform this procedure?"
- "What are the steps to...?"

### And many more...

---

## 📚 Documentation

Additional documentation available:

- **`PROJECT_STRUCTURE.md`**: Detailed project structure
- **`PHASE4_IMPLEMENTATION.md`**: Feedback learning system
- **`PHASE5_IMPLEMENTATION.md`**: Safety and governance features
- **`PHASE6_UI_UX_IMPROVEMENTS.md`**: UI/UX enhancements
- **`EXPLICIT_LANGUAGE_SELECTION.md`**: Multilingual features
- **`MULTILINGUAL_IMPROVEMENTS.md`**: Language handling details

---

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the existing code style and architecture
4. Add comprehensive docstrings
5. Test your changes thoroughly
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style Guidelines

- Use type hints for all function signatures
- Add docstrings following Google style
- Keep functions focused and modular
- Write tests for new features
- Update documentation as needed

---

## 📝 License

This project is provided as-is for the DocLingo system.

---

## 🙏 Acknowledgments

- **OpenAI**: For GPT models and embeddings
- **FAISS**: For efficient similarity search
- **Streamlit**: For the web interface framework
- **Deep Translator**: For multilingual translation support
- **PDF Plumber**: For advanced PDF processing
- **Tesseract OCR**: For scanned document support

---

## 📞 Support

For issues, questions, or feature requests:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the documentation files
3. Check existing issues on the repository
4. Create a new issue with detailed information

---

<div align="center">

**Built with ❤️ for intelligent document understanding**

[Back to Top](#doclingo-intelligent-multilingual-document-qa-system)

</div>
