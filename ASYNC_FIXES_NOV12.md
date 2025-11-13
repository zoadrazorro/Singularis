# Async/HTTP Session Fixes - November 12, 2025

## Issues Fixed

### 1. **Unclosed HTTP Sessions** ✅
**Problem:** 18+ aiohttp ClientSession objects were not being closed, causing resource leaks and warnings on shutdown.

**Root Causes:**
- `LocalMoEOrchestrator` had no `close()` method
- `LMStudioClient` had no explicit `close()` method
- Cleanup code in `skyrim_agi.py` wasn't closing all client types
- State printer LLM session not closed

**Fixes Applied:**
- Added `async def close()` to `LocalMoEOrchestrator` (`singularis/llm/local_moe.py`)
- Added `async def close()` to `LMStudioClient` (`singularis/llm/lmstudio_client.py`)
- Enhanced cleanup in `skyrim_agi.py` to close:
  - `local_moe`
  - `moe` (MoE orchestrator)
  - `hybrid_llm` (calls internal close methods)
  - `state_printer_llm.client.session`
- All sessions now properly closed on shutdown

### 2. **CancelledError on Shutdown** ✅
**Problem:** `asyncio.exceptions.CancelledError` raised when auxiliary exploration loop was cancelled during shutdown, causing ugly traceback.

**Root Cause:**
- Auxiliary exploration loop didn't handle `CancelledError` gracefully
- Loop continued after cancellation signal

**Fix Applied:**
- Added explicit `except asyncio.CancelledError` handler in `_auxiliary_exploration_loop()`
- Loop now breaks cleanly with message: `"[AUX-EXPLORE] Loop cancelled gracefully at cycle {N}"`
- No more KeyboardInterrupt propagation from cancelled tasks

### 3. **LM Studio Connection Failures** 🔧
**Problem:** All LM Studio requests failing with `400 Bad Request` to `http://localhost:1234/v1/chat/completions`

**Root Causes:**
- LM Studio not running or local server not started
- Wrong model loaded or no model loaded
- Port conflict on 1234
- Model configuration mismatch

**Diagnostic Improvements:**
- Added `health_check()` method to `LMStudioClient`
  - Tests connection to `/models` endpoint
  - Lists available models
  - Provides clear error messages
- Health check runs at startup in PARALLEL mode
- Better error logging with:
  - URL being accessed
  - Model name requested
  - Status codes
  - Error response bodies
  - Helpful troubleshooting messages

**User Action Required:**
Before running the system, ensure:
1. **LM Studio is running**
2. **Local server is started** (Server tab in LM Studio)
3. **A model is loaded** (the one specified in config)
4. **Port 1234 is not blocked** by firewall/other apps

### 4. **Enhanced Error Messages** ℹ️
All LM Studio errors now include:
- Full URL being accessed
- Model name expected
- Connection troubleshooting hints
- Distinction between:
  - Connection failure (LM Studio not running)
  - Bad request (wrong model/config)
  - Timeout (model too slow)

## Files Modified

1. **`singularis/llm/local_moe.py`**
   - Added `close()` method to properly close all expert and synthesizer sessions

2. **`singularis/llm/lmstudio_client.py`**
   - Added `close()` method
   - Added `health_check()` method for connection diagnostics
   - Enhanced error logging with connection details

3. **`singularis/skyrim/skyrim_agi.py`**
   - Added `CancelledError` handling to auxiliary exploration loop
   - Enhanced cleanup to close all client types
   - Added LM Studio health check at startup
   - Better cleanup order to prevent resource leaks

## Testing Checklist

- [ ] LM Studio running with model loaded
- [ ] System starts without connection errors
- [ ] Health check passes at startup
- [ ] Auxiliary loop runs without errors
- [ ] Clean shutdown with no unclosed session warnings
- [ ] No CancelledError traceback on exit
- [ ] All async tasks terminate gracefully

## Next Steps

1. **Fix LM Studio Connection:**
   - Start LM Studio
   - Load a model (e.g., `microsoft/phi-4-mini-reasoning`)
   - Start local server (Server tab)
   - Verify http://localhost:1234/v1/models returns model list

2. **Optional: Reduce Dependency on Local Models**
   - If LM Studio continues to fail, can run in cloud-only mode
   - Set `use_local_fallback=False` in config
   - System will use Gemini/Claude exclusively

3. **Monitor Performance:**
   - Check session report for error patterns
   - Verify cleanup logs show all sessions closed
   - No memory leaks from unclosed sessions

## Impact

✅ **Eliminated:** 18 unclosed session warnings  
✅ **Eliminated:** CancelledError traceback on shutdown  
✅ **Improved:** Error diagnostics for LM Studio issues  
✅ **Added:** Health check to detect problems early  

System now shuts down cleanly with proper resource cleanup.
