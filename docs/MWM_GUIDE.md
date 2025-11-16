## MWM (Mental World Model) – Engineering Guide

**Version**: 0.1  
**Date**: November 16, 2025  
**Status**: Design + Initial Implementation ✅

---

## Overview

The **MWM (Mental World Model)** is the agent's internal state of mind.

It fuses:
- **GWM**: Engine-truth world features (threat, enemies, cover, etc.)
- **IWM**: Visual latents + prediction (future visual states)
- **Self-state**: Health, mode, confidence, etc.
- **Affect**: Threat, curiosity, value scores
- **Hypotheses**: Predicted future states

The MWM is represented as a **latent vector** plus **structured decoded fields**, and is implemented as a PyTorch module with three core functions:
1. **encode(...)** – update mental latent from observations
2. **predict(...)** – mentally simulate the next state given an action
3. **decode(...)** – map the latent back to interpretable features

The MWM is embedded into `BeingState` and then into a higher-level `PersonModel`.

---

## Architecture

### High-Level Data Flow

```
Game Engine
  └─ GWM (Game World Model) → world features: y_world_t

Renderer
  └─ IWM (Image World Model) → visual latents: v_t

MWM (Mental World Model)
  ├─ z_t: latent mental state (vector)
  ├─ decode(z_t) → world/self/affect views
  └─ predict(z_t, a_t) → ẑ_{t+1}

PersonModel
  ├─ mwm: MentalWorldModelState   (z_t + decoded slices)
  ├─ traits: TraitProfile
  ├─ memory: MemoryProfile
  └─ capabilities: CapabilityProfile

ActionArbiter / Policies
  └─ π(a_t | mwm, traits, memory, capabilities)
```

**The MWM sits between perception (GWM/IWM) and decision (ActionArbiter/LLM).**

---

## Data Structures

### 1. Latent + Decoded State

**WorldSlice** (decoded world features):
```python
class WorldSlice(BaseModel):
    threat_level: float              # 0-1
    num_enemies: int
    num_enemies_in_los: int
    nearest_enemy_id: Optional[str]
    nearest_enemy_distance: Optional[float]
    nearest_enemy_bearing_deg: Optional[float]
    best_cover_spot_id: Optional[str]
    best_cover_distance: Optional[float]
    escape_vector_x: float
    escape_vector_y: float
    loot_available: bool
```

**SelfSlice** (decoded self-state):
```python
class SelfSlice(BaseModel):
    health: float          # 0-1
    stamina: float         # 0-1
    magicka: float         # 0-1
    is_sneaking: bool
    in_combat: bool
    confidence: float      # 0-1: self-assessed
```

**AffectSlice** (decoded affective state):
```python
class AffectSlice(BaseModel):
    threat: float          # 0-1: perceived threat
    curiosity: float       # 0-1: drive to explore
    value_estimate: float  # expected long-term value
    surprise: float        # prediction error
```

**Hypothesis** (mental simulation result):
```python
class Hypothesis(BaseModel):
    horizon_steps: int
    expected_threat: float
    expected_value: float
    action_sequence: Optional[List[str]]
```

### 2. MentalWorldModelState

**Complete mental state**:
```python
class MentalWorldModelState(BaseModel):
    # Latent vector (stored as list for Pydantic)
    latent: Optional[List[float]] = None  # [256]
    
    # Decoded slices
    world: Optional[WorldSlice] = None
    self_state: Optional[SelfSlice] = None
    affect: Optional[AffectSlice] = None
    hypotheses: Optional[HypothesisSlice] = None
    
    # Meta
    timestamp: float = 0.0
    update_count: int = 0
```

### 3. PersonModel (Higher-level)

```python
class TraitProfile(BaseModel):
    aggression: float            # 0-1
    caution: float               # 0-1
    stealth_preference: float    # 0-1
    exploration_drive: float     # 0-1

class PersonModel(BaseModel):
    mwm: MentalWorldModelState
    traits: TraitProfile
    memory: MemoryProfile        # placeholder
    capabilities: CapabilityProfile  # placeholder
```

---

## PyTorch Module: MentalWorldModelModule

### Interface

```python
class MentalWorldModelModule(nn.Module):
    def __init__(self, latent_dim: int = 256):
        # Encoders: GWM, IWM, self → latent
        # Recurrent update: GRU fusion
        # Dynamics: action-conditioned prediction
        # Decoders: latent → world, self, affect
        
    def encode(
        self,
        z_prev: torch.Tensor,      # [B, D]
        gwm_feats: torch.Tensor,   # [B, 16]
        iwm_latent: torch.Tensor,  # [B, 768]
        self_feats: torch.Tensor,  # [B, 8]
    ) -> torch.Tensor:
        """Update z_t from inputs."""
        
    def predict(
        self,
        z_t: torch.Tensor,         # [B, D]
        action_feats: torch.Tensor,  # [B, 16]
    ) -> torch.Tensor:
        """Predict z_{t+1} given action."""
        
    def decode(
        self,
        z_t: torch.Tensor,         # [B, D]
    ) -> Dict[str, torch.Tensor]:
        """Decode to world, self, affect."""
```

### Architecture Details

**Dimensions**:
- GWM: 16 features (threat, enemies, cover, etc.)
- IWM: 768 features (visual latent from ViT-B/16)
- Self: 8 features (health, stamina, mode, confidence)
- Action: 16 features (type, magnitude, direction)
- Latent: 256 (configurable)

**Encoders**:
```python
# GWM: 16 → 128 → 256
self.gwm_encoder = nn.Sequential(
    nn.Linear(16, 128),
    nn.LayerNorm(128),
    nn.ReLU(),
    nn.Dropout(0.1),
    nn.Linear(128, latent_dim),
)

# IWM: 768 → 512 → 256
self.iwm_encoder = nn.Sequential(...)

# Self: 8 → 64 → 256
self.self_encoder = nn.Sequential(...)
```

**Latent Update** (recurrent fusion):
```python
self.latent_update = nn.GRUCell(
    input_size=latent_dim * 3,  # gwm + iwm + self
    hidden_size=latent_dim,
)
```

**Dynamics** (action-conditioned prediction):
```python
self.action_encoder = nn.Sequential(...)
self.dynamics = nn.GRUCell(
    input_size=latent_dim,
    hidden_size=latent_dim,
)
```

**Decoders**:
```python
# World: 256 → 128 → 16
self.world_decoder = nn.Sequential(...)

# Self: 256 → 64 → 8
self.self_decoder = nn.Sequential(...)

# Affect: 256 → 64 → 4
self.affect_decoder = nn.Sequential(...)
```

---

## Inputs & Feature Encodings

### 1. GWM Features → gwm_feats

```python
def pack_gwm_features(gwf: GameWorldFeatures) -> np.ndarray:
    return np.array([
        gwf.threat_level,
        gwf.num_enemies,
        gwf.num_enemies_in_los,
        gwf.nearest_enemy_distance or 0.0,
        gwf.best_cover_distance or 0.0,
        gwf.stealth_safety_score,
        # ... add more as needed
    ], dtype=np.float32)
```

Shape: `[16]`

### 2. IWM Latent → iwm_latent

From IWM service: `[768]` vector per frame.

### 3. Self-state → self_feats

```python
def pack_self_features(being_state) -> np.ndarray:
    return np.array([
        being_state.player_health,
        being_state.player_stamina,
        being_state.player_magicka,
        float(being_state.is_sneaking),
        float(being_state.in_combat),
        being_state.confidence_score,
        # expand as needed
    ], dtype=np.float32)
```

Shape: `[8]`

### 4. Action Encoding → action_feats

```python
def pack_action_features(action, action_type: str) -> np.ndarray:
    # One-hot for action type [12]
    # Continuous params [4]: magnitude, direction, duration, priority
    return np.concatenate([one_hot, continuous])
```

Shape: `[16]`

---

## Integration with BeingState

### 1. Add MWM Field

Extend `BeingState`:
```python
class BeingState(BaseModel):
    # Existing
    game_world: Optional[GameWorldFeatures] = None  # GWM
    vision_core_latent: Optional[np.ndarray] = None  # IWM
    
    # New MWM
    mwm: Optional[Dict[str, Any]] = None  # MentalWorldModelState as dict
    
    # Quick-access fields
    mwm_threat_perception: float = 0.0
    mwm_curiosity: float = 0.0
    mwm_value_estimate: float = 0.0
    mwm_surprise: float = 0.0
    mwm_confidence: float = 0.5
    mwm_timestamp: float = 0.0
```

### 2. Update Function

```python
from singularis.mwm import update_mwm_from_inputs

def update_being_state_mwm(
    being_state: BeingState,
    mwm_module: MentalWorldModelModule,
    device: torch.device
):
    """Update MWM in being_state."""
    
    # Get current MWM state (or initialize)
    if being_state.mwm:
        mwm_state = MentalWorldModelState(**being_state.mwm)
    else:
        mwm_state = MentalWorldModelState()
    
    # Update MWM
    new_mwm_state = update_mwm_from_inputs(
        mwm_state=mwm_state,
        gwm_features=being_state.game_world,
        iwm_latent=being_state.vision_core_latent,
        being_state=being_state,
        mwm_module=mwm_module,
        device=device
    )
    
    # Write back to BeingState
    being_state.mwm = new_mwm_state.model_dump()
    being_state.mwm_threat_perception = new_mwm_state.affect.threat if new_mwm_state.affect else 0.0
    being_state.mwm_curiosity = new_mwm_state.affect.curiosity if new_mwm_state.affect else 0.0
    being_state.mwm_value_estimate = new_mwm_state.affect.value_estimate if new_mwm_state.affect else 0.0
    being_state.mwm_surprise = new_mwm_state.affect.surprise if new_mwm_state.affect else 0.0
    being_state.mwm_confidence = new_mwm_state.self_state.confidence if new_mwm_state.self_state else 0.5
    being_state.mwm_timestamp = time.time()
```

---

## ActionArbiter / Policy Usage

### 1. Basic Read Pattern

```python
mwm = being_state.mwm
if mwm and mwm['world'] and mwm['affect']:
    threat = mwm['affect']['threat']
    curiosity = mwm['affect']['curiosity']
    value_est = mwm['affect']['value_estimate']
    nearest_enemy = mwm['world']['nearest_enemy_id']
    
    # Use these to score candidate actions
```

### 2. Predictive Use (Mental Simulation)

```python
from singularis.mwm import score_action_with_mwm

def score_actions_with_mwm(
    candidates: List[Action],
    being_state: BeingState,
    mwm_module: MentalWorldModelModule,
    device: torch.device
) -> Dict[Action, float]:
    """Score actions using mental simulation."""
    
    scores = {}
    mwm_state = MentalWorldModelState(**being_state.mwm)
    
    for action in candidates:
        # Mentally simulate action
        score = score_action_with_mwm(
            action,
            mwm_state,
            mwm_module,
            device
        )
        scores[action] = score
    
    return scores
```

**Score formula**: `value_estimate - threat`

### 3. Combine with Heuristics

```python
def select_action(
    candidates: List[Action],
    being_state: BeingState,
    mwm_module: MentalWorldModelModule
) -> Action:
    # Score with MWM
    mwm_scores = score_actions_with_mwm(candidates, being_state, mwm_module, device)
    
    # Score with heuristics
    heuristic_scores = score_actions_heuristic(candidates, being_state)
    
    # Combine
    final_scores = {}
    for action in candidates:
        final_scores[action] = (
            0.4 * mwm_scores[action] +
            0.6 * heuristic_scores[action]
        )
    
    return max(final_scores, key=final_scores.get)
```

---

## Training Hooks (Scaffolding)

### Log Format

On each tick, log:
```python
{
  "timestamp": 12345.67,
  "gwm_features": { "threat_level": 0.7, ... },
  "iwm_latent": [0.1, 0.2, ...],  # [768]
  "self_state": { "health": 0.65, ... },
  "action_type": "move_forward",
  "action_params": { "duration": 1.0 },
  "reward_proxy": 0.12,
  "next_gwm_features": { ... },
  "next_iwm_latent": [ ... ],
  "was_successful": true
}
```

### Logging Function

```python
from singularis.mwm.training import log_training_entry

# In main loop
log_training_entry(
    gwm_features=being_state.game_world,
    iwm_latent=being_state.vision_core_latent.tolist() if being_state.vision_core_latent is not None else None,
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

### Future Training

Later, you can:
1. Load logs: `TrainingDataset.load_jsonl("logs/mwm_training.jsonl")`
2. Initialize `MentalWorldModelModule`
3. Train with losses:
   - Reconstruct GWM features from `z_t`
   - Predict next-step features from `predict(z_t, a_t)`
   - Predict reward/affect

---

## Configuration

Add to config system:
```yaml
mwm:
  enabled: true
  latent_dim: 256
  device: "cuda:0"
  use_iwm: true
  use_gwm: true
  checkpoint_path: "checkpoints/mwm_core.pt"
  update_every_n_cycles: 1
```

Wire into:
- Module construction (`latent_dim`, `device`)
- Loading/saving checkpoints
- Enable/disable toggle

---

## Files Created

```
singularis/mwm/
├── __init__.py                  (Exports)
├── types.py                     (Data structures)
├── mwm_module.py                (PyTorch module)
├── integration.py               (Packing/unpacking utilities)
└── training/
    ├── __init__.py
    └── log_schema.py            (Training log format)

docs/MWM_GUIDE.md                (This file)
```

---

## What This Enables

### Before MWM

- ActionArbiter: "I have GWM (facts) and IWM (pixels), but they're separate"
- No unified mental state
- No predictive mental simulation
- No learned affect/value

### After MWM

- **Unified Mental State**: Fuses GWM + IWM + self into single latent
- **Mental Simulation**: "What will my mental state be if I do X?"
- **Affect Signals**: Learned threat perception, curiosity, value
- **Person Model**: Foundation for personality, traits, memory integration

**SkyrimAGI can now**:
- Maintain coherent mental state across modalities
- Mentally simulate action outcomes (beyond just visual)
- Learn affective responses (threat, curiosity, value)
- Build toward full person model (traits + memory + capabilities)

---

## Integration Patterns

### Pattern 1: MWM as Central State

```
GWM → \
IWM →  → MWM (latent z_t) → Decode → World/Self/Affect
Self → /                              ↓
                                 ActionArbiter
```

### Pattern 2: MWM + PersonModel

```
MWM (state of mind)
  ↓
PersonModel (personality, memory, skills)
  ↓
ActionArbiter (decisions modulated by traits)
```

### Pattern 3: Mental Simulation Loop

```
1. Current state: z_t
2. For each candidate action a_i:
   - Predict: ẑ_{t+1} = predict(z_t, a_i)
   - Decode: affect_i = decode(ẑ_{t+1})
   - Score: s_i = affect_i.value - affect_i.threat
3. Select action with best score
```

---

## Next Steps

1. ✅ **Implement core types** (`WorldSlice`, `SelfSlice`, `AffectSlice`, `MentalWorldModelState`)
2. ✅ **Implement MentalWorldModelModule** with real feature sizes
3. ⏳ **Wire `update_mwm_from_inputs` into main loop** (update every tick)
4. ⏳ **Expose MWM fields in BeingState** and use in ActionArbiter scoring
5. ⏳ **Add logging** for (GWM, IWM, self, action, reward)
6. ⏳ **Collect data** for offline training
7. ⏳ **Train MWM** with reconstruction + prediction + affect losses
8. ⏳ **Integrate PersonModel** (traits, memory, capabilities)

---

## Summary

**MWM provides a unified mental representation** that:
- Fuses GWM (structured state) + IWM (visual) + self-state
- Maintains a latent "state of mind" (256-d vector)
- Decodes to interpretable features (world, self, affect)
- Predicts mental futures given actions
- Enables mental simulation for action selection

**This is the foundation for**:
- Unified perception-action integration
- Learned affective responses
- PersonModel (personality, memory, skills)
- True mental simulation (beyond pixels or facts alone)

**MWM sits between perception and decision**, giving SkyrimAGI a coherent internal mental state. 🧠
