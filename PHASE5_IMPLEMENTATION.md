# Phase 5: Safety, Governance & Robustness

## Overview

Phase 5 has been successfully implemented, adding comprehensive safety, governance, and robustness features to DocLingo. All safety checks are **deterministic, explainable, and auditable** - no black-box ML models.

## Implemented Components

### 1. Query Guard
**File**: `safety_engine/query_guard.py`

- **`QueryGuard`** class: Validates and sanitizes user queries
  - Detects prompt injection attempts (15+ patterns)
  - Validates query length (min 3, max 5000 characters)
  - Detects suspicious patterns (encoding, scripts, etc.)
  - Sanitizes queries (removes control characters, normalizes whitespace)
  - Returns safety decision: ALLOW, DENY, or WARN

### 2. Output Guard
**File**: `safety_engine/output_guard.py`

- **`OutputGuard`** class: Validates generated answers
  - Checks grounding against retrieved chunks (overlap analysis)
  - Detects excessive speculation (multiple speculative phrases)
  - Validates answer length (min 10, max 5000 characters)
  - Detects confidence mismatches
  - Provides safe fallback answers when validation fails

### 3. Uncertainty Handler
**File**: `safety_engine/uncertainty_handler.py`

- **`UncertaintyHandler`** class: Forces explicit uncertainty responses
  - Detects low-confidence cases
  - Checks for insufficient chunks (< 2)
  - Validates similarity scores (< 0.5)
  - Generates human-readable uncertainty messages
  - Prevents misleading answers when evidence is weak

### 4. Audit Logger
**File**: `safety_engine/audit_logger.py`

- **`AuditLogger`** class: Comprehensive query execution logging
  - Logs every query execution (JSONL format)
  - Includes: query, intent, engine, retrieval method, chunks, confidence, safety decisions
  - Logs safety decisions separately
  - Supports log retrieval and search
  - Human-readable and machine-parseable

### 5. Policy Enforcer
**File**: `safety_engine/policy_enforcer.py`

- **`PolicyEnforcer`** class: Central safety enforcement entry point
  - Coordinates all safety checks in correct order
  - Prevents bypassing of governance logic
  - Provides convenience methods for full pipeline enforcement
  - Ensures consistent behavior across all query engines

## Integration Points

### Main Pipeline (`main.py`)

1. **Query Safety Check** (Before routing)
   - Validates query before any processing
   - Rejects unsafe queries immediately
   - Uses sanitized query for all subsequent operations

2. **Output Safety Check** (After answer generation)
   - Validates answer after LLM generation
   - Checks grounding against retrieved chunks
   - Uses fallback answer if validation fails

3. **Uncertainty Handling** (Before final response)
   - Applies uncertainty messages when confidence is low
   - Prevents misleading answers

4. **Audit Logging** (After completion)
   - Logs complete query execution
   - Includes all safety decisions
   - Records execution time

## Safety Features

### Prompt Injection Detection

Detects common attack patterns:
- "Ignore previous instructions"
- "You are now..."
- "Act as..."
- "System: ..."
- "Override safety"
- And 10+ more patterns

### Grounding Validation

- Calculates word overlap between answer and retrieved chunks
- Requires minimum 10% overlap for valid answers
- Flags answers with < 30% overlap as potentially speculative

### Uncertainty Detection

Forces explicit uncertainty when:
- Confidence is "Low"
- Less than 2 chunks retrieved
- Average similarity < 50%
- Medium confidence with weak evidence

### Audit Trail

Every query execution is logged with:
- Timestamp
- Query text
- Detected intent
- Engine used
- Retrieval method
- Number of chunks
- Translation strategy
- Confidence score
- Safety decisions
- Execution time

## Usage

### Automatic Safety Enforcement

All safety checks run automatically - no configuration needed:

1. **Query Safety**: Runs before routing
2. **Output Safety**: Runs after answer generation
3. **Uncertainty Handling**: Runs before final response
4. **Audit Logging**: Runs after completion

### Accessing Audit Logs

```python
from safety_engine.audit_logger import AuditLogger

logger = AuditLogger()
recent_logs = logger.get_recent_logs(limit=50)

# Search logs
results = logger.search_logs(
    query_text="climate",
    intent="summarization",
    date_from="2024-01-01"
)
```

### Manual Safety Checks

```python
from safety_engine.policy_enforcer import PolicyEnforcer

enforcer = PolicyEnforcer()

# Check query safety
query_safety = enforcer.enforce_query_safety("What is the document about?")
if not query_safety["allowed"]:
    print(f"Query rejected: {query_safety['reason']}")

# Check output safety
output_safety = enforcer.enforce_output_safety(
    answer="...",
    retrieved_chunks=["..."],
    query="...",
    confidence="High"
)
```

## Safety Decision Flow

```
User Query
    ↓
[Query Guard] → DENY? → Return Safe Rejection
    ↓ ALLOW
[Query Routing]
    ↓
[Answer Generation]
    ↓
[Output Guard] → INVALID? → Use Fallback Answer
    ↓ VALID
[Uncertainty Handler] → Low Confidence? → Add Uncertainty Message
    ↓
[Final Answer]
    ↓
[Audit Logger] → Log Complete Execution
```

## Key Features

✅ **Deterministic**: All checks use explicit rules  
✅ **Explainable**: Every decision includes reason  
✅ **Auditable**: Complete execution logs  
✅ **Non-intrusive**: Doesn't break existing functionality  
✅ **Transparent**: Safety decisions visible in results  
✅ **Robust**: Handles edge cases and failures gracefully  

## Design Constraints Met

✅ No LLM retraining  
✅ No black-box ML models  
✅ No query classification logic changes  
✅ No grounding constraint weakening  
✅ No explainability or feedback logic removal  
✅ All logic is deterministic, explainable, testable, auditable  

## Files Created

- `safety_engine/query_guard.py` - Query validation and prompt injection detection
- `safety_engine/output_guard.py` - Answer validation and grounding checks
- `safety_engine/uncertainty_handler.py` - Explicit uncertainty responses
- `safety_engine/audit_logger.py` - Comprehensive audit logging
- `safety_engine/policy_enforcer.py` - Central safety enforcement
- `safety_engine/__init__.py` - Module exports

## Files Modified

- `main.py` - Integrated Phase 5 safety checks into pipeline

## Audit Log Format

Each log entry (JSONL format):
```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "query": "What is the document about?",
  "query_intent": "summarization",
  "document_language": "en",
  "query_language": "en",
  "engine_used": "SummarizationEngine",
  "retrieval_method": "FAISS Semantic Search",
  "num_chunks_retrieved": 5,
  "translation_strategy": "none",
  "confidence_score": "High",
  "base_confidence": "High",
  "answer_length": 245,
  "avg_similarity_score": "85.2%",
  "execution_time_ms": 1234.56,
  "safety_decisions": {
    "query_safety": {...},
    "output_safety": {...},
    "uncertainty_handling": {...}
  },
  "optimization_applied": true
}
```

## Notes

- All safety checks are rule-based (no ML models)
- Safety decisions are logged for auditability
- Failed queries return safe rejection messages
- Invalid answers use safe fallback responses
- Uncertainty is explicitly communicated to users
- All logs are human-readable JSON format

