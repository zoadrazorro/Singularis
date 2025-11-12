# Skyrim AGI Behavior Fixes

## Problems Identified

### 1. **Critical: RL System IndexError (100% failure rate)**
**Symptom:** `IndexError: index 21 is out of bounds for axis 0 with size 21`

**Root Cause:** The RL learner had 21 low-level actions (indices 0-20), but the planning layer was using high-level composite actions like `'explore'`, `'combat'`, `'rest'`, `'practice'`, `'interact'`, `'navigate'` which weren't in the action list.

**Impact:** Every RL-based planning attempt failed, forcing 100% fallback to heuristics. The AGI never used its learned Q-values.

**Fix:** Added 6 high-level composite actions to the RL learner's action list (now 27 total actions).

---

### 2. **Menu Learner Suggesting Wrong Actions**
**Symptom:** `[MENU] Using learned action: equip` followed by `[ACTION] Unknown action 'equip'`

**Root Cause:** Menu learner was being called even when NOT in a menu scene, suggesting menu-specific actions that weren't available.

**Impact:** Every action execution started with a failed menu suggestion, wasting time and confusing the pipeline.

**Fix:** 
- Only call menu learner when actually in menu scenes (INVENTORY, MAP, DIALOGUE)
- Validate suggested actions against allowed menu actions
- Exit menu learner when leaving menu scenes

---

### 3. **Repetitive, Non-Human Behavior**
**Symptom:** 
- 100% `explore` actions (68/68)
- 0 interactions with objects/NPCs
- 0 variety in behavior
- No looking around, jumping, or other human-like actions

**Root Cause:** Heuristic fallback always returned `'explore'` with no variety.

**Impact:** AGI behavior looked robotic and didn't mimic human gameplay.

**Fix:** Added probabilistic action selection:
- 15% chance to try `activate` (interact with objects/NPCs)
- 10% chance to `look_around` (situational awareness)
- 8% chance to `jump` (playful exploration)
- 20-40% chance to try different actions based on motivation
- Variety in movement (explore, move_forward, navigate)

---

### 4. **LLM Planning Never Used**
**Symptom:** `LLM-based: 0 (0.0%)`

**Root Cause:** RL planning failed before LLM could be tried.

**Impact:** The sophisticated LLM reasoning was never utilized.

**Fix:** With RL fixed, LLM planning will now be attempted when RL succeeds.

---

## Changes Made

### `reinforcement_learner.py`
```python
# Added 6 high-level composite actions
'explore',   # Composite: waypoint-based exploration
'combat',    # Composite: combat sequence
'rest',      # Composite: wait/heal
'practice',  # Composite: skill practice
'interact',  # Composite: activate objects
'navigate'   # Composite: directed movement

# Now 27 total actions (was 21)
```

### `skyrim_agi.py` - `_execute_action()`
```python
# Only call menu learner in actual menu scenes
if scene_type in [SceneType.INVENTORY, SceneType.MAP, SceneType.DIALOGUE]:
    # Menu learner logic
else:
    # Exit menu learner if active
    if self.menu_learner.current_menu:
        self.menu_learner.exit_menu()

# Added support for more action types
elif action == 'move_forward':
    await self.actions.move_forward(duration=1.5)
elif action == 'jump':
    await self.actions.execute(Action(ActionType.JUMP))
elif action == 'look_around':
    await self.actions.look_around()
# ... etc
```

### `skyrim_agi.py` - `_plan_action()` Heuristics
```python
# Added probabilistic variety
if random.random() < 0.15 and 'activate' in available_actions:
    return 'activate'  # Try to interact

if random.random() < 0.10:
    return 'look_around'  # Look around

if random.random() < 0.08 and 'jump' in available_actions:
    return 'jump'  # Playful jumping

# Motivation-based variety
if dominant_drive == 'curiosity':
    if 'activate' in available_actions and random.random() < 0.4:
        return 'activate'  # 40% chance to interact
    elif random.random() < 0.3:
        return 'move_forward'  # 30% chance to just move
    return 'explore'  # Otherwise explore
```

---

## Expected Improvements

### Immediate
1. ✅ **RL planning will work** - No more IndexError
2. ✅ **No more menu learner spam** - Clean action execution
3. ✅ **Action variety** - Will see activate, jump, look_around, move_forward
4. ✅ **More human-like** - Random exploration patterns

### Over Time (as RL learns)
1. 📈 **Better action selection** - RL will learn which actions work best
2. 📈 **Context-aware decisions** - Will learn when to interact vs explore
3. 📈 **Improved coherence** - Actions that increase Δ𝒞 will be reinforced
4. 📈 **Strategic behavior** - Will learn patterns like "low health → rest"

---

## Monitoring

Watch for these in the logs:

### Good Signs ✅
```
[RL] Q-values: explore=1.23, activate=0.98, move_forward=0.87
[RL-NEURON] Action: activate (tactical score: 0.85)
[HEURISTIC] → activate (random curiosity)
[ACTION] Interacting with object/NPC
```

### Bad Signs ⚠️
```
[_plan_action] ERROR: index X is out of bounds
[MENU] Using learned action: equip  # When not in menu
[HEURISTIC] → explore (autonomy/default)  # Every single time
```

---

## Next Steps

1. **Test the fixes** - Run the AGI and verify:
   - No more IndexError
   - Action variety (should see activate, jump, look_around)
   - RL planning succeeds
   
2. **Monitor RL learning** - Over multiple sessions:
   - Check if Q-values are differentiating
   - Verify actions with positive Δ𝒞 are reinforced
   - Watch for emergent strategic behavior

3. **Fine-tune probabilities** - Adjust if needed:
   - Increase `activate` probability if still not interacting enough
   - Adjust `look_around` frequency for more/less awareness
   - Balance exploration vs exploitation

4. **Consider adding**:
   - NPC detection → automatic `talk` action
   - Quest marker awareness → `quest_objective` action
   - Loot detection → `activate` on containers
   - Combat detection → automatic layer switching
