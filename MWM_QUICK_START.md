# MWM Quick Start Guide

**TL;DR**: Unified mental state = GWM + IWM + Self → Latent [256] → Affect/Value

---

## 1. Test System

```bash
python test_mwm_system.py
# Should see: ✓ All tests passed!
```

---

## 2. Wire into Main Loop

```python
from singularis.mwm import (
    MentalWorldModelModule,
    MentalWorldModelState,
    update_mwm_from_inputs
)

# Initialize (once)
mwm_module = MentalWorldModelModule(latent_dim=256).to(device)
mwm_module.eval()

# In cycle
if being_state.mwm:
    mwm_state = MentalWorldModelState(**being_state.mwm)
else:
    mwm_state = MentalWorldModelState()

new_mwm = update_mwm_from_inputs(
    mwm_state,
    being_state.game_world,       # GWM
    being_state.vision_core_latent,  # IWM
    being_state,
    mwm_module,
    device
)

# Write back
being_state.mwm = new_mwm.model_dump()
being_state.mwm_threat_perception = new_mwm.affect.threat
being_state.mwm_curiosity = new_mwm.affect.curiosity
being_state.mwm_value_estimate = new_mwm.affect.value_estimate
being_state.mwm_timestamp = time.time()
```

---

## 3. Use in ActionArbiter

```python
# Read MWM
mwm = being_state.mwm
if mwm and mwm['affect']:
    threat = mwm['affect']['threat']
    curiosity = mwm['affect']['curiosity']
    value = mwm['affect']['value_estimate']
    
    # Score actions
    if threat > 0.7 and being_state.health < 0.3:
        prefer_escape()
    elif curiosity > 0.6 and threat < 0.2:
        prefer_explore()
```

---

## 4. Mental Simulation

```python
from singularis.mwm import score_action_with_mwm

mwm_state = MentalWorldModelState(**being_state.mwm)

scores = {}
for action in candidates:
    score = score_action_with_mwm(action, mwm_state, mwm_module, device)
    scores[action] = score

best_action = max(scores, key=scores.get)
```

---

## 5. Log Training Data

```python
from singularis.mwm.training import log_training_entry

log_training_entry(
    gwm_features=being_state.game_world,
    iwm_latent=being_state.vision_core_latent.tolist(),
    self_state={
        "health": being_state.game_state.get('player_health', 1.0),
        "stamina": being_state.game_state.get('player_stamina', 1.0),
        # ...
    },
    action_type=str(action.action_type),
    action_params={"duration": action.duration},
    reward_proxy=compute_reward(),
    log_file=Path("logs/mwm_training.jsonl")
)
```

---

## BeingState Fields

```python
# Full MWM state
being_state.mwm: Dict[str, Any]

# Quick access
being_state.mwm_threat_perception: float  # Agent's perceived threat
being_state.mwm_curiosity: float          # Drive to explore
being_state.mwm_value_estimate: float     # Expected value
being_state.mwm_surprise: float           # Prediction error
being_state.mwm_confidence: float         # Self-assessed confidence
```

---

## MWM Decoded Slices

```python
{
    'world': {
        'threat_level': 0.75,
        'num_enemies': 2,
        'nearest_enemy_id': 'bandit_001',
        'escape_vector_x': -0.8,
        'escape_vector_y': -0.6
    },
    'self_state': {
        'health': 0.65,
        'stamina': 0.40,
        'is_sneaking': False,
        'in_combat': True,
        'confidence': 0.72
    },
    'affect': {
        'threat': 0.72,           # Perceived threat
        'curiosity': 0.15,         # Explore drive
        'value_estimate': 0.45,    # Expected value
        'surprise': 1.2            # Prediction error
    }
}
```

---

## Integration Patterns

### Basic Use
```python
if being_state.mwm_threat_perception > 0.7:
    if being_state.health < 0.3:
        return escape_action()
```

### Combine with GWM
```python
# Engine truth vs perception
gwm_threat = being_state.gwm_threat_level
mwm_threat = being_state.mwm_threat_perception

if mwm_threat > gwm_threat + 0.2:
    # Agent is paranoid OR learned from experience
    logger.info("Agent perceives more threat")
```

### Combine with IWM
```python
# Visual surprise + perceived threat
if being_state.vision_prediction_surprise > 2.0:
    if being_state.mwm_threat_perception > 0.7:
        # Unexpected change in dangerous situation
        escalate_to_llm()
```

---

## Files Created

**Core (5)**:
- `singularis/mwm/__init__.py`
- `singularis/mwm/types.py` - Data structures
- `singularis/mwm/mwm_module.py` - PyTorch module
- `singularis/mwm/integration.py` - Packing/unpacking
- `singularis/mwm/training/log_schema.py` - Training logs

**Scripts (1)**:
- `test_mwm_system.py` - Test suite

**Docs (3)**:
- `docs/MWM_GUIDE.md` - Complete guide
- `MWM_IMPLEMENTATION_SUMMARY.md` - Summary
- `MWM_QUICK_START.md` - This file

**Modified (1)**:
- `singularis/core/being_state.py` - Added MWM fields

---

## What MWM Provides

| Component | Provides | Use Case |
|-----------|----------|----------|
| **Latent** | Unified state [256] | Single mental representation |
| **World Slice** | Decoded world | Interpretable features |
| **Self Slice** | Decoded self | Agent's self-view |
| **Affect Slice** | Threat/curiosity/value | Emotional/motivational state |
| **Predict** | Future states | Mental simulation |

---

## MWM vs IWM vs GWM

| System | Input | Output | Use Case |
|--------|-------|--------|----------|
| **IWM** | RGB images | Visual latents [768] | "What will I see?" |
| **GWM** | Engine JSON | Tactical features [16] | "What's happening?" |
| **MWM** | IWM + GWM + Self | Mental latent [256] + Affect | "How do I feel?" |

**All three together = Complete world understanding** 🧠

---

## Next Steps

1. ✅ **MWM implemented**
2. ⏳ **Wire into main loop**: Update every cycle
3. ⏳ **Use in ActionArbiter**: Read `mwm_*` fields
4. ⏳ **Log training data**: Collect (GWM, IWM, action, reward)
5. ⏳ **Train MWM**: Use logs to train fusion model
6. ⏳ **Integrate PersonModel**: Traits + memory + capabilities

---

**MWM gives SkyrimAGI a unified mental state** that:
- Fuses perception (GWM + IWM + Self)
- Learns affect (threat, curiosity, value)
- Enables mental simulation (predict futures)
- Provides foundation for PersonModel

**This is the "mind" between perception and decision.** 🎯
