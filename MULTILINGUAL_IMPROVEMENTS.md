# Multilingual Output, Improved Language Handling & Advanced PDF Processing

## Overview

This document describes three major improvements implemented for DocLingo:
1. **Multilingual Fallback & Error Messages** - All system messages in query language
2. **Strong Multilingual LLM Behavior** - Explicit language instructions, Indian language support
3. **Advanced PDF Processing** - PDF Plumber + OCR for scanned documents

## Change 1: Multilingual Fallback & Error Messages

### Problem Solved
Previously, fallback and error messages were hardcoded in English, even when queries were in other languages.

### Solution
Created `language_manager/multilingual_messages.py` with `MultilingualMessageGenerator` class that:
- Translates all system messages to query language
- Centralizes message generation
- Provides consistent multilingual fallback messages

### Updated Components
- `safety_engine/uncertainty_handler.py` - Uses multilingual messages
- `safety_engine/output_guard.py` - Uses multilingual fallback messages
- `main.py` - Uses multilingual messages for "no content" and query rejection
- `answer_engine/generator.py` - Uses multilingual "no answer" message

### Message Types
All messages are now multilingual:
- No content found
- No answer available
- Low similarity warning
- Insufficient chunks warning
- Uncertain answer
- Query rejected
- Processing error

## Change 2: Strong Multilingual LLM Behavior

### Problem Solved
- Limited language support
- No explicit language instructions to LLM
- Technical terms appearing in answers
- Inconsistent language output

### Solution

#### 1. Explicit Language Instructions
- All LLM prompts now explicitly specify output language
- Example: "You MUST answer the question in Hindi (hi)"
- Language name and code both provided for clarity

#### 2. Technical Term Removal
- System prompts explicitly forbid technical terms:
  - "chunks" → "sections"
  - "embeddings", "similarity scores", "retrieval", "FAISS" → removed
- Context formatting uses "Section" instead of "Chunk"
- Answers use natural, user-friendly language

#### 3. Full Language Coverage
- Supports all languages from Deep Translator
- Special support for Indian languages:
  - Hindi (hi), Malayalam (ml), Tamil (ta), Telugu (te)
  - Kannada (kn), Marathi (mr), Urdu (ur), Bengali (bn)
  - Gujarati (gu), Punjabi (pa), Odia (or), Assamese (as)

#### 4. Consistent Language Output
- Answer language always matches:
  - User-selected answer language (if provided), OR
  - Query language (default rule)

### Updated Components
- `answer_engine/generator.py`:
  - Added `answer_language` parameter
  - Updated system prompt with explicit language instruction
  - Removed technical terms from prompts
  - Changed "Chunks" to "Sections" in user prompt
  
- `query_engine/content_engine.py`:
  - Added `answer_language` parameter to `process()`
  - Updated `_build_system_prompt()` to include language instruction
  - Updated `_build_user_prompt()` to specify output language
  - Added `_get_language_name()` helper method
  
- `query_engine/router.py`:
  - Added `answer_language` parameter to `route()`
  - Passes answer language to content engine

- `main.py`:
  - Passes `answer_language` to `generate_answer()`
  - Passes `answer_language` to router

## Change 3: Advanced PDF Processing

### Problem Solved
- Basic PDF text extraction couldn't handle:
  - Image-based PDFs
  - Scanned documents
  - Complex layouts and tables

### Solution

#### 1. PDF Plumber Integration
- Replaced PyPDF2 with PDF Plumber as primary extraction method
- Better handling of:
  - Tables (extracted as structured text)
  - Complex layouts
  - Multi-column documents
- Falls back to PyPDF2 if PDF Plumber fails

#### 2. OCR Support
- Integrated Tesseract OCR via `pytesseract`
- Automatically detects when OCR is needed:
  - If text extraction returns empty page
  - Attempts OCR as fallback
- Supports scanned/image-based PDFs

#### 3. Unified Processing Pipeline
```
PDF File
    ↓
[PDF Plumber] → Extract text + tables
    ↓ (if empty)
[OCR (Tesseract)] → Extract from images
    ↓
[Text Processing] → Chunking → FAISS → Query
```

### Updated Components
- `document_processor/pdf_loader.py`:
  - Uses PDF Plumber as primary method
  - Falls back to PyPDF2 for compatibility
  - Handles both file paths and Streamlit uploaders

- `document_processor/text_extractor.py`:
  - Enhanced extraction with PDF Plumber
  - Table extraction support
  - OCR integration with automatic fallback
  - Better error handling

### Dependencies
New optional dependencies (see `requirements_enhanced.txt`):
- `pdfplumber>=0.10.0` - Advanced PDF processing
- `pytesseract>=0.3.10` - OCR wrapper
- `Pillow>=10.0.0` - Image processing

**Note**: Tesseract OCR engine must be installed separately:
- macOS: `brew install tesseract`
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- Windows: Download from GitHub

## Integration Points

### Language Flow
```
User Query (any language)
    ↓
[Language Detection/Selection]
    ↓
[Language Resolution]
    ↓
[LLM Generation] → Explicit language instruction
    ↓
[Answer Translation] (if needed)
    ↓
[Multilingual Messages] → All fallbacks in query language
```

### PDF Processing Flow
```
PDF Upload
    ↓
[PDF Plumber] → Extract text + tables
    ↓ (if insufficient)
[OCR Detection] → Check if page is image-based
    ↓ (if needed)
[Tesseract OCR] → Extract text from images
    ↓
[Text Chunking] → FAISS Indexing → Query Processing
```

## Key Features

### Multilingual Support
✅ All system messages in query language  
✅ Explicit LLM language instructions  
✅ Full Indian language support  
✅ Natural, non-technical answers  
✅ Consistent language output  

### PDF Processing
✅ PDF Plumber for better extraction  
✅ Automatic OCR for scanned documents  
✅ Table extraction support  
✅ Graceful fallback mechanisms  
✅ Backward compatible with PyPDF2  

## Files Created

- `language_manager/multilingual_messages.py` - Multilingual message generator
- `requirements_enhanced.txt` - Additional dependencies

## Files Modified

- `answer_engine/generator.py` - Multilingual LLM prompts, technical term removal
- `query_engine/content_engine.py` - Multilingual support, language instructions
- `query_engine/router.py` - Pass answer language to engines
- `safety_engine/uncertainty_handler.py` - Multilingual uncertainty messages
- `safety_engine/output_guard.py` - Multilingual fallback messages
- `safety_engine/policy_enforcer.py` - Pass language to handlers
- `document_processor/pdf_loader.py` - PDF Plumber integration
- `document_processor/text_extractor.py` - OCR support, table extraction
- `main.py` - Integration of all changes

## Usage Examples

### Multilingual Query (Hindi)
```python
result = run_doclingo(
    pdf_file="document.pdf",
    query="यह दस्तावेज़ किस बारे में है?",
    user_query_lang="hi",
    user_answer_lang="hi"
)
# Answer will be in Hindi, all messages in Hindi
```

### Scanned PDF
```python
# System automatically detects scanned PDF
# Falls back to OCR if text extraction fails
result = run_doclingo("scanned_document.pdf", "What is this about?")
```

### Indian Language Support
```python
# Malayalam query
result = run_doclingo(
    pdf_file="doc.pdf",
    query="ഈ രേഖയുടെ പ്രധാന വിഷയം എന്താണ്?",
    user_query_lang="ml"
)
# Answer in Malayalam, all messages in Malayalam
```

## Design Constraints Met

✅ No existing features removed  
✅ FAISS and query routing unchanged  
✅ No LLM retraining  
✅ No hardcoded language-specific answers  
✅ Deterministic, explainable, backward compatible  

## Testing Recommendations

1. **Multilingual Messages**: Test with queries in various languages
2. **LLM Language Output**: Verify answers match query/answer language
3. **Technical Terms**: Ensure no technical terms appear in answers
4. **PDF Processing**: Test with:
   - Regular PDFs (text-based)
   - Scanned PDFs (image-based)
   - PDFs with tables
   - Complex layouts
5. **OCR**: Test with image-only PDFs

## Notes

- OCR is optional - system works without it (just won't handle scanned PDFs)
- PDF Plumber is preferred but falls back to PyPDF2
- All language support depends on Deep Translator capabilities
- Multilingual messages use Google Translate (same as document translation)
- Language instructions are explicit in every LLM call

