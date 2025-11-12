# Stuck Detection System

## Overview
Comprehensive stuck detection and recovery system to prevent infinite loops, repeated failures, and system hangs across all AGI components.

## Detection Systems

### 1. **Cloud LLM Failure Detection**
- **Tracks:** Consecutive failures of cloud LLM (Gemini + Claude)
- **Threshold:** 5 consecutive failures
- **Action:** Logged with warning counter
- **Recovery:** Combined with Local MoE check (see #4)

### 2. **Local MoE Failure Detection**
- **Tracks:** Consecutive failures of Local MoE (4x Qwen3-VL + Phi-4)
- **Threshold:** 5 consecutive failures
- **Action:** Logged with warning counter
- **Recovery:** Combined with Cloud LLM check (see #4)

### 3. **Repeated Action Detection**
- **Tracks:** Same action being executed consecutively
- **Threshold:** 10 repeated actions
- **Trigger:** `action == last_successful_action` for 10 cycles
- **Recovery:**
  ```
  [STUCK-DETECTION] ⚠️ Repeated action 'move_forward' 10 times!
  [STUCK-DETECTION] Forcing variety - choosing random different action
  [STUCK-DETECTION] Switched to: jump
  ```
- **Behavior:** Forces a random different action from available actions

### 4. **All Systems Failing Detection**
- **Tracks:** Both Cloud LLM AND Local MoE failing simultaneously
- **Threshold:** Both >= 5 consecutive failures
- **Trigger:** Critical system failure
- **Recovery:**
  ```
  [STUCK-DETECTION] ⚠️⚠️⚠️ ALL LLM SYSTEMS FAILING!
  [STUCK-DETECTION] Cloud: 5, Local MoE: 5
  [STUCK-DETECTION] Forcing random exploration action
  ```
- **Behavior:** 
  - Forces random action from: `['move_forward', 'jump', 'look_around', 'activate']`
  - Resets all failure counters
  - Breaks out of failure loop

### 5. **Auxiliary Exploration Error Detection**
- **Tracks:** Errors in auxiliary exploration loop (move, look, turn, camera)
- **Threshold:** 20 errors
- **Recovery:**
  ```
  [STUCK-DETECTION] ⚠️ Auxiliary exploration has 20 errors, pausing for 5s
  ```
- **Behavior:**
  - Pauses auxiliary loop for 5 seconds
  - Resets error counter
  - Allows system to recover

### 6. **Planning Timeout Protection**
- **Tracks:** Entire `_plan_action()` call duration
- **Threshold:** 30 seconds
- **Recovery:**
  ```
  [REASONING] ⚠️ Planning timed out after 30s, using fallback
  [REASONING] WARNING: No action returned by _plan_action, using fallback
  ```
- **Behavior:** Falls back to safe 'explore' action

## Failure Counters

### Tracked Variables
```python
self.cloud_llm_failures = 0        # Cloud LLM consecutive failures
self.local_moe_failures = 0        # Local MoE consecutive failures
self.heuristic_failures = 0        # Heuristic system failures
self.auxiliary_errors = 0          # Auxiliary exploration errors
self.last_successful_action = None # Last action executed
self.repeated_action_count = 0     # Consecutive same actions
```

### Thresholds
```python
self.max_consecutive_failures = 5  # Max LLM failures before alert
self.max_repeated_actions = 10     # Max same action repetitions
```

## Reset Conditions

### Success Resets
- **Cloud LLM success:** `self.cloud_llm_failures = 0`
- **Local MoE success:** `self.local_moe_failures = 0`
- **Different action:** `self.repeated_action_count = 0`

### Recovery Resets
- **All systems failing:** Resets cloud, local, heuristic counters
- **Repeated action limit:** Resets `repeated_action_count = 0`
- **Auxiliary errors:** Resets `auxiliary_errors = 0` after pause

## Example Scenarios

### Scenario 1: Cloud LLM Temporary Failure
```
Cycle 1: Cloud fails → failures=1
Cycle 2: Cloud fails → failures=2
Cycle 3: Cloud fails → failures=3
Cycle 4: Cloud succeeds → failures=0 (reset)
```

### Scenario 2: Repeated Action Loop
```
Cycle 1-9: move_forward (count=9)
Cycle 10: move_forward → STUCK DETECTED
  → Switches to random action (e.g., 'jump')
  → count=0
```

### Scenario 3: Total System Failure
```
Cloud: 5 failures
Local MoE: 5 failures
→ ALL SYSTEMS FAILING!
→ Force random: 'activate'
→ Reset all counters
```

### Scenario 4: Auxiliary Errors
```
Errors: 1-19 (logged periodically)
Error 20: STUCK DETECTED
  → Pause 5 seconds
  → Reset errors=0
  → Resume
```

## Benefits

1. **Prevents Infinite Loops:** Detects and breaks repeated action patterns
2. **Handles LLM Failures:** Gracefully degrades when LLMs fail
3. **Automatic Recovery:** Self-healing without manual intervention
4. **Maintains Gameplay:** Always produces an action, never hangs
5. **Comprehensive Coverage:** All major systems monitored
6. **Clear Logging:** Easy to diagnose issues from logs

## Monitoring

All stuck detection events are logged with `[STUCK-DETECTION]` prefix for easy filtering:
```bash
grep "STUCK-DETECTION" logs.txt
```

## Future Enhancements

- Visual embedding similarity detection (stuck in same location)
- Coherence drop detection (consciousness degradation)
- Performance degradation detection (planning time increasing)
- Network connectivity monitoring
