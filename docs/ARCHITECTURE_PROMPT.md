# DocLingo System Architecture Flowchart Prompt

Use this prompt with an AI tool (ChatGPT, Claude, Mermaid, draw.io, etc.) to generate a black and white flowchart of the DocLingo system architecture.

---

## PROMPT FOR AI:

Create a detailed black and white flowchart diagram showing the complete DocLingo system architecture workflow from user query input to final answer output. Use only black, white, and shades of gray. Ensure all text has correct spelling and proper grammar.

### System Overview:
DocLingo is a multilingual document question-answering system that uses intelligent query routing, semantic search (FAISS), and LLM-based answer generation with safety checks and feedback-driven optimization.

### Complete Workflow (in order):

1. **START: User Query Input**
   - User submits query (text)
   - User may optionally specify: document language, query language, answer language

2. **Phase 5: Query Safety Check** (First step - mandatory)
   - Policy Enforcer validates query
   - Check for prompt injection, malicious content, system override attempts
   - Decision: Query Allowed? 
     - If NO → Return rejection message, audit log, END
     - If YES → Continue (may sanitize query if warnings present)

3. **Document Loading & Extraction**
   - Load PDF file using PDF Loader
   - Extract text from all pages using Text Extractor
   - Decision: Pages extracted?
     - If NO → Return "No readable content" message, END
     - If YES → Continue

4. **Language Resolution**
   - Language Resolver processes language settings
   - If user provided explicit language selections → Use user selections
   - If not provided → Auto-detect using Language Detector
   - Resolve: Document Language, Query Language, Answer Language
   - Output: Final language configuration

5. **Document Metadata Extraction**
   - Extract document metadata (page count, title, author, date if available)
   - Store metadata for routing decisions

6. **Intelligent Query Routing** (3-Tier System)
   - Intent Classifier analyzes query
   - Classify query intent (Metadata, Aggregate, Analytical, Summarization, Interpretation, Comparison, etc.)
   
   **TIER 1: Programmatic Engines** (Fast, no LLM needed)
   - Try Metadata Engine (page count, document info queries)
   - Try Aggregate Engine (counting, structural queries)
   - Try Analytical Engine (calculations, statistics)
   - Decision: TIER 1 handled query?
     - If YES → Return answer directly, skip retrieval, END
     - If NO → Continue to TIER 2

   **TIER 2: Specialized LLM Engines** (Category-specific)
   - Route based on intent: Summarization Engine, Interpretation Engine, Comparison Engine, Causation Engine, Opinion Stance Engine, Critical Analysis Engine, Procedural Engine, Contextual Engine
   - Decision: TIER 2 engine available?
     - If YES → Store engine info, continue to content pipeline (for retrieval)
     - If NO → Continue to TIER 3

   **TIER 3: General Content Engine** (Fallback)
   - Content Engine handles all other queries
   - Continue to content pipeline

7. **Phase 4: Feedback Optimization**
   - Strategy Optimizer retrieves feedback history
   - Get optimized parameters (retrieval depth, translation strategy) based on past performance
   - Use feedback data if available (last 30 days)

8. **Adaptive Decision Engine**
   - Decision Engine analyzes: document language, query language, page count, optimized parameters
   - Determine: Translation Strategy (none, full, partial)
   - Determine: Retrieval Depth (number of chunks, optimized from feedback)

9. **Document Translation** (Conditional)
   - Decision: Translation Strategy?
     - If "none" → Skip translation, use original pages
     - If "full" → Translate all pages to query language
     - If "partial" → Keep original, translate later after retrieval
   - Output: Processed pages (translated or original)

10. **FAISS Indexing**
    - Chunk document pages (size: 500 chars, overlap: 50 chars)
    - Generate embeddings using OpenAI embeddings (text-embedding-3-small)
    - Build FAISS vector index
    - Store chunks with metadata (page numbers, chunk indices)
    - Decision: Already indexed?
      - If YES → Skip re-indexing
      - If NO → Create new index

11. **Semantic Retrieval with FAISS**
    - Generate query embedding
    - Search FAISS index for top-k most similar chunks (k = retrieval depth from step 8)
    - Calculate similarity scores (L2 distance converted to similarity)
    - Extract: chunks, metadata (page numbers, scores)
    - Output: Retrieved chunks with similarity scores

12. **Partial Translation** (Conditional)
    - Decision: Translation Strategy was "partial"?
      - If YES → Translate only retrieved chunks to query language
      - If NO → Skip translation

13. **Answer Generation with LLM**
    - Answer Generator receives: retrieved chunks, query, answer language
    - Build context from chunks (format with page citations if enabled)
    - Create system prompt (language-aware, intent-aware)
    - Create user prompt with query and context
    - Call OpenAI API (GPT-4o-mini) with prompts
    - Generate answer strictly from provided context (document-grounded)
    - Output: LLM-generated answer

14. **Phase 5: Output Safety Check**
    - Policy Enforcer validates generated answer
    - Check: Grounding score (answer supported by retrieved chunks)
    - Check: Hallucination detection
    - Check: Language compliance
    - Check: Safety violations
    - Decision: Answer valid?
      - If NO → Use fallback answer, log warning
      - If YES → Continue
    - Output: Validated answer

15. **Confidence Calculation**
    - Confidence Calibrator computes confidence score
    - Factors: number of chunks, similarity scores, feedback history
    - Output: Confidence level (High, Medium, Low)

16. **Explanation Generation**
    - Explanation Generator creates human-readable explanation
    - Include: translation path, retrieval method, chunks used, language resolution
    - Output: Explanation text and metadata

17. **Feedback Logging** (Phase 4)
    - Feedback Logger records query, answer, confidence, execution time
    - Store for future optimization

18. **Final Response Assembly**
    - Combine: answer, confidence, explanation, metadata
    - Include: document language, query language, answer language
    - Include: query intent, retrieval method, number of chunks used
    - Include: language resolution details

19. **END: Return Final Response to User**
    - Return complete response object to user

### Additional Components (Background):
- **Feedback Manager**: Continuously learns from user feedback to optimize parameters
- **Safety Engine**: Monitors and enforces safety policies throughout the pipeline
- **Language Manager**: Handles multilingual support, translation, and language detection
- **Vector Store**: FAISS index for semantic search
- **Embedding Manager**: Manages text embeddings for semantic search

### Flowchart Requirements:
- Use rectangular boxes for processes
- Use diamond shapes for decision points
- Use arrows to show flow direction
- Label all components clearly
- Show parallel paths where applicable (e.g., TIER 1/2/3 routing)
- Use clear hierarchy and grouping
- Include feedback loops where applicable (Phase 4 optimization)
- Show early exit points (TIER 1 direct answers, safety rejections)
- Use consistent terminology throughout
- Ensure all text is spelled correctly

### Color Scheme:
- Background: White
- Boxes/Shapes: Black borders
- Text: Black
- Decision diamonds: Gray fill (light gray)
- Process boxes: White fill with black border
- Arrows: Black lines
- Optional: Use different line weights or dashed lines for different flow types (main flow vs. feedback loops)

### Key Decision Points to Highlight:
1. Query Safety Check (allowed/rejected)
2. Document extraction success
3. TIER 1 routing (handled/not handled)
4. TIER 2 routing (available/not available)
5. Translation strategy selection
6. Output safety validation

Generate a professional, clear flowchart that accurately represents this complete workflow.


