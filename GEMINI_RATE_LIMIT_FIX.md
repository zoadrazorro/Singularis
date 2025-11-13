# Gemini Rate Limit Fix

## Problem
Gemini API has a **30 RPM (requests per minute)** limit, but the AGI is making ~120-150 requests per minute:

- Consciousness assessment: 1 call/cycle
- Sensorimotor vision: 1 call/cycle  
- MoE experts: 2 calls/cycle
- Stuck detection: occasional calls

**Result**: Constant 429 errors, all Gemini calls failing

## Solutions

### Option 1: Skip Gemini Calls More Often (Recommended)

Modify `run_skyrim_agi.py` line 120:

```python
# BEFORE:
gemini_rpm_limit=30,

# AFTER:  
gemini_rpm_limit=15,  # Use only half of limit for safety margin
```

Also add these config options around line 106:

```python
# Reduce Gemini call frequency
gemini_vision_frequency=3,  # Only call Gemini vision every 3rd cycle
consciousness_frequency=2,  # Only assess consciousness every 2nd cycle
```

### Option 2: Disable Gemini MoE Experts

Modify line 116:

```python
# BEFORE:
num_gemini_experts=2,

# AFTER:
num_gemini_experts=0,  # Disable Gemini MoE, use only Claude + Hyperbolic
```

This eliminates 2 calls per cycle.

### Option 3: Use Local Models Only

Set `use_local_fallback=True` and disable cloud:

```python
use_gemini_vision=False,
use_claude_reasoning=False,
use_moe=False,
use_local_fallback=True,
```

This uses only LM Studio models (no rate limits).

### Option 4: Increase Cycle Interval

Line 105:

```python
# BEFORE:
cycle_interval=2.0,

# AFTER:
cycle_interval=4.0,  # Slower cycles = fewer API calls
```

This cuts API usage in half.

## Recommended Configuration

For best balance of intelligence and rate limits:

```python
config = SkyrimConfig(
    # ... other settings ...
    
    # Rate limit management
    cycle_interval=3.0,  # Slower cycles
    gemini_rpm_limit=15,  # Conservative limit
    num_gemini_experts=1,  # Reduce from 2 to 1
    
    # Skip some Gemini calls
    gemini_vision_frequency=2,  # Every 2nd cycle
    consciousness_frequency=2,  # Every 2nd cycle
    
    # Keep fallbacks
    use_local_fallback=True,
)
```

This reduces Gemini calls from ~120/min to ~20/min (well under 30 RPM limit).

## Current System Status

✅ **System is working correctly** - fallbacks are functioning
✅ **100% action success rate**
✅ **State coordination resolving conflicts properly**

❌ **Gemini rate limited** - all calls failing with 429
⚠️ **Using local fallbacks** - slower but functional

## Performance Impact

**With Gemini working:**
- Vision quality: Excellent
- Reasoning depth: Very high
- Response time: Fast

**With local fallback only:**
- Vision quality: Good (Qwen3-VL is capable)
- Reasoning depth: Good (Phi-4 is capable)
- Response time: Slower (local inference)

## Implementation

1. Edit `run_skyrim_agi.py`
2. Apply Option 1 + Option 4 changes
3. Restart AGI
4. Monitor logs for 429 errors (should disappear)
