# DocLingo Query Understanding & Routing System

A production-ready, modular query routing system for document Q&A with multilingual support using OpenAI LLMs.

## 🎯 Features

- **Intelligent Intent Classification**: Deterministic, explainable query classification
- **Multi-Engine Architecture**: Specialized engines for different query types
- **Multilingual Support**: Ask questions in any language, get answers in the same language
- **Zero Hallucination**: Programmatic engines for metadata, counting, and analytical queries
- **Extensible Design**: Easy to add new query types and engines
- **OpenAI Integration**: Seamless integration with GPT-4 and GPT-3.5

## 📁 Project Structure

```
query_engine/
├── intent_classifier.py      # Query intent classification
├── router.py                  # Central query dispatcher
├── metadata_engine.py         # Document property queries
├── aggregate_engine.py        # Counting & frequency queries
├── analytical_engine.py       # Computational queries
├── content_engine.py          # Semantic queries with OpenAI
├── main.py                    # Integration & examples
└── requirements.txt           # Dependencies
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Set up OpenAI API Key

```bash
# Linux/Mac
export OPENAI_API_KEY='your-api-key-here'

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"
```

### 3. Basic Usage

```python
from main import DocLingoQuerySystem

# Initialize system
system = DocLingoQuerySystem()

# Prepare your document
pages = [
    "Your document content page 1...",
    "Your document content page 2...",
]

document_info = {
    "title": "Sample Document",
    "author": "John Doe",
    "date": "2024-01-15",
    "type": "Report",
    "language": "English"
}

# Ask a question
answer = system.query_document(
    query="What is the main topic of this document?",
    pages=pages,
    document_info=document_info,
    verbose=True  # Shows routing information
)

print(answer)
```

### 4. Multilingual Usage

```python
# Ask in Spanish, get answer in Spanish
answer = system.query_multilingual(
    query="¿Cuántas páginas tiene este documento?",
    query_language="es",
    pages=pages,
    document_language="en",
    document_info=document_info
)

print(answer)
```

## 📊 Query Categories Supported

### 1. **Metadata Queries** (No LLM)
- Page count, word count, document properties
- Publication date, author, title
- Example: "How many pages does this document have?"

### 2. **Aggregate Queries** (No LLM)
- Counting sections, chapters, references
- Frequency analysis, pattern matching
- Example: "How many tables are in the document?"

### 3. **Analytical Queries** (Programmatic + LLM for phrasing)
- Age calculations, time spans
- Statistical analysis, trend identification
- Example: "How old is this document?"

### 4. **Content Queries** (LLM-based)
- Summarization, interpretation
- Comparison, causation analysis
- Example: "Summarize the main findings"

### 5. **Structural Queries** (No LLM)
- Document organization, hierarchy
- Table of contents
- Example: "What is the structure of this document?"

## 🔧 Advanced Usage

### Custom Document Processing

```python
# Initialize with custom API key
system = DocLingoQuerySystem(openai_api_key="your-key")

# Process multiple queries at once
queries = [
    "How many pages?",
    "Who is the author?",
    "What are the key findings?"
]

results = system.batch_query(
    queries=queries,
    pages=pages,
    document_info=document_info
)

for result in results:
    print(f"Query: {result['query']}")
    print(f"Answer: {result['answer']}")
    print(f"Engine: {result['metadata']['engine']}")
    print("---")
```

### Using with Vector Search (FAISS)

```python
# If you have pre-computed relevant chunks from FAISS
relevant_chunks = your_faiss_retrieval(query, embeddings)

response = system.router.route(
    query=query,
    pages=pages,
    document_info=document_info,
    relevant_chunks=relevant_chunks  # Pass pre-retrieved chunks
)
```

## 🎨 Customization

### Adding New Query Types

1. Add new intent in `intent_classifier.py`:

```python
class QueryIntent(Enum):
    YOUR_NEW_INTENT = "your_new_intent"
```

2. Add patterns in `_initialize_patterns()`:

```python
QueryIntent.YOUR_NEW_INTENT: [
    {
        "keywords": ["your", "keywords"],
        "patterns": [r"\byour\s+pattern\b"]
    }
]
```

3. Create new engine or route to existing engine in `router.py`.

### Changing LLM Model

Edit `content_engine.py`:

```python
self.model = "gpt-4"  # or "gpt-4o-mini", "gpt-3.5-turbo"
```

## 📈 Performance Tips

1. **Precompute Metadata**: Call `metadata_engine.compute_metadata()` once
2. **Use FAISS**: Replace simple retrieval with vector search
3. **Batch Processing**: Use `batch_query()` for multiple questions
4. **Cache Results**: Implement caching for repeated queries
5. **Adjust Temperature**: Lower for factual, higher for creative

## 🧪 Testing

Run the example:

```bash
python main.py
```

Expected output shows routing decisions and answers for various query types.

## 🐛 Troubleshooting

**Issue**: "OpenAI API key not set"
- **Solution**: Set `OPENAI_API_KEY` environment variable

**Issue**: Slow responses
- **Solution**: Use `gpt-4o-mini` instead of `gpt-4`

**Issue**: Wrong engine routing
- **Solution**: Add more specific patterns in `intent_classifier.py`

**Issue**: Hallucinated answers
- **Solution**: Ensure using specialized engines for non-content queries

## 🔒 Best Practices

1. **Never route metadata queries to LLM** - Use MetadataEngine
2. **Validate inputs** - Check pages and document_info format
3. **Handle errors gracefully** - All engines return Optional[str]
4. **Use verbose mode** - During development to understand routing
5. **Monitor API usage** - OpenAI calls cost money

## 📄 License

This code is provided as-is for the DocLingo project.

## 🤝 Contributing

To extend this system:
1. Follow the modular architecture
2. Keep engines independent
3. Add comprehensive docstrings
4. Test with diverse query types

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review example usage in `main.py`
3. Ensure all dependencies are installed
4. Verify OpenAI API key is valid

---

**Built with ❤️ for intelligent document understanding**