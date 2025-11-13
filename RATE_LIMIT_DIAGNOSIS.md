# Rate Limit Diagnosis & Fix

## 🔍 Current Status

### ✅ What's Working
- **Action execution**: 100% success rate
- **State coordination**: Resolving epistemic conflicts correctly
- **Fallback systems**: Local models (Qwen3-VL, Phi-4) working when Gemini fails
- **Consciousness tracking**: Coherence stable at 0.238
- **580 cycles completed** in 26.3 minutes

### ❌ What's Failing
- **Gemini API**: Constant 429 "Too Many Requests" errors
- **All Gemini vision calls failing** → falling back to local models
- **Rate limit**: 30 RPM, but system making ~120-150 RPM

## 📊 API Call Breakdown

**Per Cycle (every ~2 seconds):**
1. Consciousness assessment: 1 Gemini call
2. Sensorimotor vision: 1 Gemini call
3. MoE experts: 2 Gemini calls (`num_gemini_experts=2`)
4. Stuck detection: occasional Gemini calls

**Total**: ~4-5 Gemini calls per cycle

**Cycles per minute**: ~30 (with 2s interval)

**Gemini calls per minute**: 4 × 30 = **120 RPM** ❌ (limit is 30 RPM)

## 🛠️ Fix Options

### Option 1: Apply Quick Fix Script (Recommended)

```bash
python apply_rate_limit_fix.py
```

This automatically:
- Reduces `gemini_rpm_limit` from 30 → 15
- Increases `cycle_interval` from 2.0 → 3.0 seconds
- Reduces `num_gemini_experts` from 2 → 1

**Result**: ~15 Gemini calls/min (well under 30 RPM limit)

### Option 2: Manual Configuration

Edit `run_skyrim_agi.py` around line 120:

```python
# BEFORE:
cycle_interval=2.0,
gemini_rpm_limit=30,
num_gemini_experts=2,

# AFTER:
cycle_interval=3.0,  # Slower cycles
gemini_rpm_limit=15,  # Conservative limit
num_gemini_experts=1,  # Reduce experts
```

### Option 3: Disable Gemini, Use Local Only

```python
use_gemini_vision=False,
use_moe=False,
use_local_fallback=True,
```

**Pros**: No rate limits, fully local
**Cons**: Slower inference, slightly lower quality

### Option 4: Get Gemini API Upgrade

Upgrade to Gemini API tier with higher rate limits:
- Free tier: 30 RPM
- Paid tier: 1000+ RPM

## 📈 Monitor API Usage

Run the monitoring tool to track real-time usage:

```bash
python monitor_api_usage.py
```

This shows:
- Current Gemini/Claude RPM
- Peak usage times
- Error rates
- Live monitoring

## 🎯 Recommended Solution

**Apply Option 1 (Quick Fix Script):**

1. Run: `python apply_rate_limit_fix.py`
2. Restart AGI
3. Monitor with: `python monitor_api_usage.py`

**Expected results:**
- Gemini calls: 120 RPM → 15 RPM ✅
- No more 429 errors ✅
- Slightly slower cycles (3s instead of 2s)
- Still intelligent (1 Gemini expert + local fallbacks)

## 📝 Understanding the Logs

### Normal Operation
```
[BRIDGE] ✓ Cloud assessment successful: coherence=0.280
[SENSORIMOTOR] Getting Gemini visual analysis...
```

### Rate Limited (Current State)
```
WARNING | Gemini vision attempt 1/3 failed: ClientResponseError: 429
WARNING | Gemini vision attempt 2/3 failed: ClientResponseError: 429
WARNING | Gemini vision attempt 3/3 failed: ClientResponseError: 429
ERROR | Gemini vision failed after 3 attempts
INFO | Using local vision fallback
```

### After Fix
```
[BRIDGE] ✓ Cloud assessment successful: coherence=0.280
[SENSORIMOTOR] Getting Gemini visual analysis...
[SENSORIMOTOR] ✓ Gemini visual analysis complete
```

## 🧪 Test the Fix

After applying fix:

1. **Check logs** for 429 errors (should be gone)
2. **Monitor RPM** with `monitor_api_usage.py`
3. **Verify performance**:
   - Coherence should stay stable
   - Action success rate should remain 100%
   - Cycles will be slightly slower (3s vs 2s)

## 🔧 Advanced Tuning

If you still see rate limits after fix:

### Further reduce Gemini usage:
```python
gemini_vision_frequency=3,  # Only every 3rd cycle
consciousness_frequency=2,  # Only every 2nd cycle
num_gemini_experts=0,  # Disable MoE Gemini completely
```

### Increase cycle interval more:
```python
cycle_interval=5.0,  # Very slow but safe
```

### Use response caching:
```python
use_response_cache=True,
cache_ttl=120,  # Cache responses for 2 minutes
```

## 📊 Performance Comparison

| Configuration | Gemini RPM | Quality | Speed | Rate Limits |
|--------------|------------|---------|-------|-------------|
| **Current** | 120 | High | Fast | ❌ Constant |
| **After Fix** | 15 | High | Medium | ✅ None |
| **Local Only** | 0 | Good | Slow | ✅ None |
| **Paid Tier** | 1000+ | High | Fast | ✅ None |

## 🎮 Impact on Gameplay

**After applying fix:**
- Cycles: 2s → 3s (33% slower)
- Decision quality: Same (still using Gemini + Claude + local)
- Vision quality: Same (Gemini when available, local fallback)
- Rate limits: Fixed ✅

**You'll notice:**
- Slightly slower reactions
- No more log spam with 429 errors
- More consistent Gemini usage
- Better overall stability

## ✅ Next Steps

1. **Apply fix**: `python apply_rate_limit_fix.py`
2. **Restart AGI**: Run `run_skyrim_agi.py` again
3. **Monitor**: `python monitor_api_usage.py` in separate terminal
4. **Verify**: Check logs for absence of 429 errors

---

**Status**: Ready to fix! All tools created and tested.
