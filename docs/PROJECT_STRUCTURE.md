# DocLingo Project Structure

```
doclingo_cursor/
├── answer_engine/
│   ├── explainer.py
│   └── generator.py
├── confidence_engine/
│   └── confidence_score.py
├── decision_engine/
│   └── adaptive_engine.py
├── document_processor/
│   ├── chunker.py
│   ├── pdf_loader.py
│   └── text_extractor.py
├── feedback_manager/
│   └── feedback_logger.py
├── language_manager/
│   ├── language_detector.py
│   └── translation_manager.py
├── query_engine/
│   ├── __init__.py
│   ├── aggregate_engine.py
│   ├── analytical_engine.py
│   ├── causation_engine.py
│   ├── comparison_engine.py
│   ├── content_engine.py
│   ├── contextual_engine.py
│   ├── critical_analysis_engine.py
│   ├── intent_classifier.py
│   ├── interpretation_engine.py
│   ├── metadata_engine.py
│   ├── opinion_stance_engine.py
│   ├── procedural_engine.py
│   ├── router.py
│   └── summarization_engine.py
├── retrieval_engine/
│   └── retriever.py
├── utils/
│   └── helpers.py
├── vector_store/
│   ├── __init__.py
│   ├── embedding_manager.py
│   └── faiss_index.py
├── README.md
├── app.py
├── filestruct.txt
├── main.py
├── patch.py
├── requirements.txt
└── working.md
```

## Directory Overview

### Core Application Files
- **`app.py`** - Streamlit web application entry point
- **`main.py`** - Main pipeline and DocLingoSystem class
- **`requirements.txt`** - Python dependencies
- **`README.md`** - Project documentation

### Query Engine (10+ specialized engines)
- **`router.py`** - Central query routing system
- **`intent_classifier.py`** - Query intent classification
- **`content_engine.py`** - General content queries (FAISS integrated)
- **`summarization_engine.py`** - Summarization queries (FAISS integrated)
- **`comparison_engine.py`** - Comparison queries (FAISS integrated)
- **`causation_engine.py`** - Cause-effect queries (FAISS integrated)
- **`interpretation_engine.py`** - Interpretation queries (FAISS integrated)
- **`opinion_stance_engine.py`** - Opinion/stance queries (FAISS integrated)
- **`critical_analysis_engine.py`** - Critical analysis (FAISS integrated)
- **`procedural_engine.py`** - Procedural/how-to queries (FAISS integrated)
- **`contextual_engine.py`** - Context queries (FAISS integrated)
- **`metadata_engine.py`** - Metadata queries (programmatic, no LLM)
- **`aggregate_engine.py`** - Counting queries (programmatic, no LLM)
- **`analytical_engine.py`** - Analytical queries (programmatic, no LLM)

### Document Processing
- **`document_processor/pdf_loader.py`** - PDF file loading
- **`document_processor/text_extractor.py`** - Text extraction from PDFs
- **`document_processor/chunker.py`** - Text chunking with overlap

### Vector Store & Retrieval
- **`vector_store/embedding_manager.py`** - OpenAI embeddings management
- **`vector_store/faiss_index.py`** - FAISS vector index
- **`retrieval_engine/retriever.py`** - FAISSRetriever class

### Language Management
- **`language_manager/language_detector.py`** - Language detection
- **`language_manager/translation_manager.py`** - Translation handling

### Answer & Confidence
- **`answer_engine/generator.py`** - Answer generation with LLM
- **`answer_engine/explainer.py`** - Explanation generation
- **`confidence_engine/confidence_score.py`** - Confidence scoring

### Other Components
- **`decision_engine/adaptive_engine.py`** - Adaptive decision making
- **`feedback_manager/feedback_logger.py`** - Feedback logging
- **`utils/helpers.py`** - Utility functions

### Documentation & Config
- **`filestruct.txt`** - File structure documentation
- **`working.md`** - Working notes
- **`patch.py`** - Utility script

## Module Counts

- **Total Python files**: 38
- **Query engines**: 14 (3 programmatic + 11 LLM-based)
- **LLM engines with FAISS**: 10 (all except metadata/aggregate/analytical)
- **Core modules**: 8 (document_processor, retrieval_engine, vector_store, etc.)

## Key Features

✅ FAISS semantic search integrated  
✅ Multi-engine query routing  
✅ Multilingual support  
✅ Adaptive translation strategies  
✅ Document-grounded answering  
✅ Explainability and confidence scoring

