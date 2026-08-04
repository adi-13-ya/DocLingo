# Explicit Language Selection & Intelligent Fallback

## Overview

This feature adds explicit user-controlled language selection to DocLingo while preserving all existing automatic behavior. Users can now explicitly select document, query, and answer languages, reducing unnecessary translation and providing more control.

## Implementation

### New Module

**File**: `language_manager/language_resolver.py`

- **`LanguageResolver`** class: Resolves final languages based on user selections and automatic detection
  - Accepts optional user-selected languages (document, query, answer)
  - Accepts detected languages as fallback
  - Resolves final languages following deterministic rules
  - Provides helper methods for detection and translation decisions

### Language Resolution Rules

1. **User selects all three languages** → Use user selections, skip detection
2. **User selects only document language** → Use it, detect query, answer = query
3. **User selects query language** → Use it, answer = query (unless answer explicitly selected)
4. **User selects answer language** → Use it, translate answer if needed
5. **User selects nothing** → Auto-detect both, answer = query (current behavior)

**Critical Rule**: `answer_language` always defaults to `query_language` if not explicitly set.

### Integration Points

#### `main.py`

- Updated `run_doclingo()` function signature:
  ```python
  def run_doclingo(
      pdf_file, 
      query, 
      target_lang="en",  # Legacy parameter
      user_doc_lang: Optional[str] = None,
      user_query_lang: Optional[str] = None,
      user_answer_lang: Optional[str] = None
  )
  ```

- Language resolution happens before routing:
  - Checks if user provided explicit selections
  - Auto-detects only when needed
  - Resolves final languages using `LanguageResolver`
  - Uses resolved languages for translation decisions

- Answer translation:
  - Translates answer if `answer_language` differs from `query_language`
  - Only happens when user explicitly selects different answer language

#### `app.py`

- Added optional language selection UI:
  - Document language selector (optional)
  - Query language selector (optional)
  - Answer language selector (optional)
  - All default to "Auto-detect" or "Same as query"
  - Collapsed in expander (not intrusive)

- Passes language selections to `run_doclingo()`:
  - Passes `None` if user doesn't select (preserves auto-detection)

## Usage

### Automatic Behavior (Default)

If user doesn't select any languages:
- Document language: Auto-detected
- Query language: Auto-detected
- Answer language: Same as query language

### Explicit Selection

User can select:
- **Document language**: Skip detection, use selection
- **Query language**: Skip detection, use selection
- **Answer language**: Translate answer to selected language

### Examples

**Example 1: User selects document language only**
- User selects: Document = "es"
- System: Uses "es" for document, auto-detects query, answer = query

**Example 2: User selects query and answer languages**
- User selects: Query = "en", Answer = "fr"
- System: Auto-detects document, uses "en" for query, translates answer to "fr"

**Example 3: User selects all three**
- User selects: Document = "es", Query = "en", Answer = "fr"
- System: Uses all selections, skips detection, translates as needed

## Benefits

✅ **Reduced Translation**: Skip unnecessary translation when languages are known  
✅ **User Control**: Explicit control over language behavior  
✅ **Backward Compatible**: Works exactly as before when no selection made  
✅ **Intelligent Fallback**: Auto-detection when selections not provided  
✅ **Deterministic**: All decisions are rule-based and explainable  

## Design Constraints Met

✅ No automatic detection removal  
✅ No forced language selection  
✅ No user selection override  
✅ No new LLM calls for language resolution  
✅ No query routing or FAISS logic changes  
✅ All logic is deterministic, explainable, backward compatible  

## Files Created

- `language_manager/language_resolver.py` - Language resolution logic

## Files Modified

- `main.py` - Integrated language resolver into pipeline
- `app.py` - Added optional language selection UI

## Language Codes Supported

The UI supports common language codes:
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ru` - Russian
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean
- `ar` - Arabic
- `hi` - Hindi

(Any language code supported by the translation manager will work)

## Notes

- Language resolution happens early in the pipeline (after safety checks)
- Translation decisions use resolved languages, not detected ones
- Answer translation only occurs when answer language differs from query language
- All language decisions are logged in audit logs
- Language resolution info is included in result metadata

