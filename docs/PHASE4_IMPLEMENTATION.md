# Phase 4: Feedback-Driven Self-Learning & Adaptive Optimization

## Overview

Phase 4 has been successfully implemented, enabling DocLingo to learn from user feedback and adapt its strategies over time. All implementation is **deterministic, explainable, and auditable** - no black-box ML models or LLM retraining.

## Implemented Components

### 1. Enhanced Feedback Collection Layer
**File**: `feedback_manager/feedback_logger.py`

- **`FeedbackLogger`** class: Collects rich metadata with each feedback
  - Rating (1-10 scale)
  - Query and answer text
  - Metadata: intent, engine, translation strategy, retrieval depth, confidence, etc.
  - Persists to JSONL format (one JSON object per line)
  - Backward compatible with existing `log_feedback()` function

### 2. Feedback Analytics Engine
**File**: `feedback_manager/feedback_analyzer.py`

- **`FeedbackAnalyzer`** class: Analyzes feedback statistics
  - Aggregates feedback by intent, engine, translation strategy, confidence level
  - Computes average ratings, min/max ratings, sample counts
  - Identifies best-performing strategies
  - Analyzes optimal retrieval depth based on feedback
  - All analysis is deterministic and explainable

### 3. Adaptive Strategy Optimizer
**File**: `decision_engine/strategy_optimizer.py`

- **`StrategyOptimizer`** class: Optimizes system parameters from feedback
  - Adjusts retrieval depth (top_k) based on feedback
  - Identifies preferred translation strategies
  - Provides intent-specific optimization
  - Returns explainable parameter adjustments
  - Requires minimum 5 feedback samples before optimization

### 4. Feedback-Aware Confidence Calibration
**File**: `confidence_engine/confidence_calibrator.py`

- **`ConfidenceCalibrator`** class: Calibrates confidence scores
  - Adjusts confidence levels based on historical feedback
  - Intent-specific calibration
  - Engine-specific calibration
  - Confidence-level performance analysis
  - Returns explainable calibration decisions

### 5. Enhanced Adaptive Decision Engine
**File**: `decision_engine/adaptive_engine.py`

- Updated **`AdaptiveDecisionEngine.decide()`** method:
  - Accepts optional `optimized_params` from Phase 4
  - Uses feedback-optimized translation strategy preferences
  - Incorporates feedback-optimized retrieval depth
  - Maintains backward compatibility (works without Phase 4 params)
  - All decisions remain deterministic and explainable

### 6. Main Pipeline Integration
**File**: `main.py`

- **`DocLingoSystem`** class enhanced with Phase 4 components:
  - `strategy_optimizer`: For parameter optimization
  - `confidence_calibrator`: For confidence calibration
  - `feedback_logger`: For feedback collection (metadata preparation)

- **`run_doclingo()`** function enhanced:
  - Gets feedback-optimized parameters before adaptive decision
  - Uses optimized retrieval depth for FAISS retrieval
  - Calibrates confidence scores based on feedback
  - Includes Phase 4 metadata in result for feedback logging

### 7. User Interface Enhancement
**File**: `app.py`

- Added feedback collection UI:
  - Rating slider (1-10 scale)
  - Submit feedback button
  - Success confirmation with visual feedback
  - Optional expansion panels showing:
    - Confidence calibration information
    - Optimization explanations

## How It Works

### Feedback Loop

1. **User receives answer** → DocLingo generates answer using current strategies
2. **User provides feedback** → Rating (1-10) submitted via UI
3. **Feedback logged** → Rich metadata stored in `feedback_log.json`
4. **Statistics aggregated** → FeedbackAnalyzer computes performance metrics
5. **Strategies optimized** → StrategyOptimizer adjusts parameters
6. **Future queries improved** → System uses optimized parameters

### Adaptation Mechanisms

#### 1. Retrieval Depth Optimization
- Analyzes which retrieval depths (number of chunks) correlate with better ratings
- Adjusts `top_k` parameter for FAISS retrieval
- Default: 5 chunks, optimized: 2-10 chunks based on feedback

#### 2. Translation Strategy Preference
- Identifies which translation strategies ("none", "partial", "full") perform best
- Prefers high-performing strategies when context allows
- Still respects language matching rules (same language = no translation)

#### 3. Confidence Calibration
- Adjusts confidence levels ("High", "Medium", "Low") based on actual user trust
- If "High" confidence queries consistently score low → reduces confidence
- If "Low" confidence queries consistently score high → increases confidence
- Intent-specific and engine-specific adjustments

## Key Features

✅ **Deterministic**: All adaptations use explicit rules, no randomness  
✅ **Explainable**: Every decision can be traced to feedback statistics  
✅ **Auditable**: All feedback data stored in human-readable JSON format  
✅ **No LLM Retraining**: Only system-level parameter adjustments  
✅ **Backward Compatible**: Works without feedback (uses defaults)  
✅ **Progressive Learning**: Improves as more feedback accumulates  

## Usage

### For End Users

1. Use DocLingo normally - ask questions, get answers
2. Rate answers using the 1-10 slider in the UI
3. System automatically improves over time based on your feedback
4. No configuration needed - works transparently

### For Developers

#### Accessing Feedback Statistics

```python
from feedback_manager.feedback_analyzer import FeedbackAnalyzer

analyzer = FeedbackAnalyzer()
stats = analyzer.get_statistics(days=30)
print(f"Average rating: {stats['average_rating']}")
print(f"Best translation strategy: {stats['by_translation_strategy']}")
```

#### Getting Optimized Parameters

```python
from decision_engine.strategy_optimizer import StrategyOptimizer

optimizer = StrategyOptimizer()
params = optimizer.get_optimized_parameters(intent="summarization", days=30)
print(f"Optimal retrieval depth: {params['retrieval_depth']}")
print(f"Explanation: {params['explanation']}")
```

#### Calibrating Confidence

```python
from confidence_engine.confidence_calibrator import ConfidenceCalibrator

calibrator = ConfidenceCalibrator()
result = calibrator.calibrate_confidence(
    base_confidence="High",
    intent="summarization",
    days=30
)
print(f"Calibrated: {result['calibrated_confidence']}")
```

## Data Storage

- **Feedback Log**: `feedback_log.json` (JSONL format)
  - One JSON object per line
  - Includes timestamp, rating, query, answer, and rich metadata
  - Human-readable and easily parseable

## Design Constraints Met

✅ No LLM retraining  
✅ No FAISS index structure changes  
✅ No query classification logic changes  
✅ No black-box ML models  
✅ No decisions inside prompts  
✅ All adaptation is rule-based and explainable  

## Future Enhancements (Optional)

Possible future improvements (not implemented):
- Export feedback statistics to CSV/Excel
- Visual dashboard for feedback analytics
- Per-user feedback tracking
- A/B testing framework for strategies
- Feedback weighting by recency

## Notes

- Minimum feedback threshold: 5 samples before optimization begins
- Confidence calibration requires: 10+ samples for reliable calibration
- Feedback is stored locally in `feedback_log.json`
- All optimizations are reversible (can clear feedback log to reset)

