# IWM + GWM Integration - Complete World Understanding

**How visual and tactical world models work together**

---

## Two Complementary Systems

### IWM (Image World Model)
- **Type**: Neural network (ViT-B/16 + predictor)
- **Input**: RGB images (224×224)
- **Output**: 768-d visual latents
- **Capability**: "What will I see if I do X?"
- **Use Case**: Visual prediction, anomaly detection

### GWM (Game World Model)
- **Type**: Structured state modeling
- **Input**: Engine snapshots (JSON)
- **Output**: Tactical features (dict)
- **Capability**: "How dangerous is this? Where's cover?"
- **Use Case**: Threat assessment, tactical planning

---

## Data Flow

```
┌──────────────┐
│ Game Engine  │
│   (Skyrim)   │
└──┬───────┬───┘
   │       │
   │       └─────────────┐
   │                     │
   │ Screenshots         │ State JSON
   │ (visual)            │ (structured)
   │                     │
   ↓                     ↓
┌──────────┐      ┌──────────┐
│   IWM    │      │   GWM    │
│ Service  │      │ Service  │
└────┬─────┘      └────┬─────┘
     │                 │
     │ Latents         │ Features
     │ [768]           │ {threat,cover,...}
     │                 │
     └────────┬────────┘
              │
              ↓
       ┌──────────────┐
       │ BeingState   │
       │ .vision_*    │
       │ .gwm_*       │
       └──────┬───────┘
              │
              ↓
       ┌──────────────┐
       │ActionArbiter │
       └──────────────┘
```

---

## BeingState: Unified View

```python
@dataclass
class BeingState:
    # IWM fields
    vision_core_latent: np.ndarray  # [768] current visual latent
    vision_prediction_surprise: float  # Prediction error
    vision_mrr: float  # Visual model confidence
    
    # GWM fields
    game_world: Dict[str, Any]  # Full tactical features
    gwm_threat_level: float  # 0-1: danger
    gwm_num_enemies: int
    gwm_nearest_enemy_distance: float
    gwm_stealth_safety: float
    
    # Both systems contribute to one unified state
```

---

## Integration Patterns

### Pattern 1: Anomaly Detection

**Problem**: High visual surprise in dangerous situation

```python
# IWM detects visual anomaly
if being_state.vision_prediction_surprise > 2.0:
    # GWM checks tactical context
    if being_state.gwm_threat_level > 0.7:
        logger.critical("Visual anomaly in combat - unexpected change!")
        # Escalate to LLM for interpretation
        await escalate_to_gpt(
            visual_surprise=being_state.vision_prediction_surprise,
            threat_level=being_state.gwm_threat_level,
            context="Unexpected visual change during high-threat situation"
        )
```

### Pattern 2: Confidence Gating

**Problem**: When to trust which model

```python
# High visual confidence + high threat = trust both
if being_state.vision_mrr > 0.7 and being_state.gwm_threat_level > 0.5:
    # Visual world model is confident, GWM detects threat
    # Use IWM for "what will happen" + GWM for "how dangerous"
    await plan_action_with_both_models()

# Low visual confidence but structured state available
elif being_state.vision_mrr < 0.4 and being_state.game_world:
    # Fall back to GWM tactical features
    await plan_action_from_gwm_only()

# Both low confidence
else:
    # Conservative/safe behavior
    await escalate_to_llm()
```

### Pattern 3: Multi-Modal Planning

**Problem**: Plan actions using both visual and tactical futures

```python
async def plan_action_sequence(being_state, candidate_actions):
    best_action = None
    best_score = -999.0
    
    for action_sequence in candidate_actions:
        # IWM: Predict visual outcomes
        visual_rollout = await iwm.rollout(
            being_state.vision_core_latent,
            action_sequence
        )
        
        # Visual score: low surprise = good
        visual_score = 1.0 - np.mean([r.uncertainty for r in visual_rollout])
        
        # GWM: Assess tactical outcomes
        # (Requires action-conditioned GWM - Phase 3)
        tactical_score = compute_tactical_score(
            action_sequence,
            being_state.game_world
        )
        
        # Combined score
        total_score = 0.5 * visual_score + 0.5 * tactical_score
        
        if total_score > best_score:
            best_score = total_score
            best_action = action_sequence
    
    return best_action
```

### Pattern 4: Escape Planning

**Problem**: Player needs to escape, use both models

```python
async def plan_escape(being_state):
    # GWM: Get escape direction
    escape_vector = being_state.game_world['escape_vector']
    
    # Generate candidate escape actions
    escape_actions = generate_movement_sequence(escape_vector, steps=5)
    
    # IWM: Check if escape path looks safe visually
    visual_rollout = await iwm.rollout(
        being_state.vision_core_latent,
        escape_actions
    )
    
    # If high visual surprise along escape path, might be obstacle
    if max(r.uncertainty for r in visual_rollout) > 3.0:
        logger.warning("Escape path has visual obstacle")
        # Try alternate path
        return generate_alternate_escape(escape_vector, avoid_obstacle=True)
    
    return escape_actions
```

### Pattern 5: Stealth Assessment

**Problem**: Should player enter stealth?

```python
async def assess_stealth_viability(being_state):
    # GWM: Tactical stealth assessment
    gwm_stealth_safe = being_state.gwm_stealth_safety > 0.6
    
    # IWM: Visual prediction if we crouch
    current_latent = being_state.vision_core_latent
    crouch_action_params = [0.0, 0.0, 1.0, 0.0]  # "crouch" encoding
    
    predicted_latent = await iwm.predict_next(
        current_latent,
        crouch_action_params
    )
    
    # Low prediction surprise = stable situation (good for stealth)
    visual_stable = predicted_latent.uncertainty < 1.0
    
    # Combine
    if gwm_stealth_safe and visual_stable:
        return "STEALTH_RECOMMENDED"
    elif not gwm_stealth_safe:
        return "TOO_DANGEROUS"
    else:
        return "UNCERTAIN"
```

---

## ActionArbiter Integration

```python
class ActionArbiter:
    def __init__(self):
        self.iwm = IWMClient("http://localhost:8001")
        self.gwm = GWMClient("http://localhost:8002")
    
    async def update_world_models(self, being_state):
        """Update both world models."""
        # Both models update BeingState
        # No need to synchronize - they're independent
        pass
    
    async def request_action(self, being_state, candidates):
        """Select action using both models."""
        
        # Score candidates using GWM tactical features
        tactical_scores = {}
        for action in candidates:
            score = self._score_tactical(action, being_state.game_world)
            tactical_scores[action] = score
        
        # Filter to top 3 tactical candidates
        top_tactical = sorted(candidates, key=lambda a: tactical_scores[a], reverse=True)[:3]
        
        # Use IWM to predict visual outcomes for top candidates
        visual_scores = {}
        for action in top_tactical:
            action_params = self._action_to_params(action)
            pred = await self.iwm.predict_next(
                being_state.vision_core_latent,
                action_params
            )
            # Low uncertainty = confident prediction = good
            visual_scores[action] = 1.0 - pred.uncertainty
        
        # Combined scoring
        final_scores = {}
        for action in top_tactical:
            final_scores[action] = (
                0.6 * tactical_scores[action] +
                0.4 * visual_scores[action]
            )
        
        # Select best
        best_action = max(final_scores, key=final_scores.get)
        
        logger.info(
            f"Selected {best_action}: "
            f"tactical={tactical_scores[best_action]:.2f}, "
            f"visual={visual_scores[best_action]:.2f}"
        )
        
        return best_action
    
    def _score_tactical(self, action, gwm_features):
        """Score action based on GWM features."""
        score = 0.5
        
        # Defensive actions good in high threat
        if gwm_features['threat_level'] > 0.7:
            if action.type in ['move_to_cover', 'block', 'heal']:
                score += 0.3
        
        # Offensive actions good in low threat
        if gwm_features['threat_level'] < 0.3:
            if action.type in ['attack', 'loot']:
                score += 0.3
        
        # Escape actions good when outnumbered
        if gwm_features['num_enemies_total'] > 3:
            if action.type == 'flee':
                score += 0.4
        
        return score
```

---

## LLM Integration: Full Context

```python
async def consult_llm_with_full_context(being_state):
    """Pass both IWM and GWM context to LLM."""
    
    prompt = f"""
VISUAL WORLD STATE (IWM):
- Visual latent: {being_state.vision_core_latent.shape}
- Prediction surprise: {being_state.vision_prediction_surprise:.2f}
  (High surprise = unexpected visual change)
- Visual model confidence: {being_state.vision_mrr:.2f}
  (Higher = more confident in predictions)

TACTICAL WORLD STATE (GWM):
- Threat level: {being_state.gwm_threat_level:.2f}/1.0
- Enemies: {being_state.gwm_num_enemies} total
- Nearest enemy: {being_state.gwm_nearest_enemy_distance:.1f}m away
- Stealth safety: {being_state.gwm_stealth_safety:.2f}/1.0
- Best cover available: {being_state.gwm_best_cover_distance:.1f}m away
- Loot opportunity: {being_state.gwm_loot_available}

PLAYER STATE:
- Health: {being_state.health:.2f}/1.0
- In combat: {being_state.in_combat}
- Current action: {being_state.last_action}

ANALYSIS:
The visual world model {'is confident' if being_state.vision_mrr > 0.7 else 'is uncertain'} 
and predicts {'stable' if being_state.vision_prediction_surprise < 1.0 else 'changing'} conditions.

The tactical situation is {'DANGEROUS' if being_state.gwm_threat_level > 0.7 else 'MODERATE' if being_state.gwm_threat_level > 0.4 else 'SAFE'}.

What should I do?
"""
    
    response = await llm.generate(prompt)
    return response
```

---

## Performance Considerations

### Latency Budget

| System | Operation | Latency | When |
|--------|-----------|---------|------|
| IWM | Encode | 10-15ms | Every frame |
| IWM | Predict | 5-8ms | Per candidate |
| IWM | Rollout (k=5) | 30-40ms | Planning |
| GWM | Features | <1ms | Every snapshot |
| **Total** | **Per decision** | **50-100ms** | Acceptable |

### Update Rates

- **IWM**: Update on every frame (vision)
- **GWM**: Update on every engine snapshot (10-30 Hz)
- **Out of sync**: OK! They're independent

### Fallback Strategy

```python
# Prefer both, fall back gracefully
if iwm_available and gwm_available:
    use_both_models()
elif gwm_available:
    use_gwm_only()  # Structured state still very useful
elif iwm_available:
    use_iwm_only()  # Visual predictions still helpful
else:
    use_heuristics_only()  # Conservative behavior
```

---

## What This Achieves

### Complete World Understanding

| Question | Answered By | How |
|----------|-------------|-----|
| "What do I see?" | IWM | Encode frame → latent |
| "What will I see?" | IWM | Predict next latent |
| "How dangerous is this?" | GWM | Threat level |
| "Where's cover?" | GWM | Best cover spot |
| "Should I fight or flee?" | Both | GWM threat + IWM prediction |
| "Is this situation changing?" | IWM | Prediction surprise |
| "Can I loot safely?" | GWM | Threat + loot opportunity |

### Example Scenario: Combat Ambush

```
1. Frame arrives → IWM encodes to latent
2. IWM predicts next frame (normal patrol)
3. Engine snapshot arrives → GWM updates
4. GWM computes: threat_level = 0.9 (3 enemies, all with LOS!)
5. Next frame arrives → IWM encodes
6. IWM surprise = 3.5 (high! didn't predict ambush)

ActionArbiter reasoning:
- High GWM threat (0.9) = danger
- High IWM surprise (3.5) = unexpected
- Player health = 0.4 = low
- Decision: ESCAPE (use GWM escape_vector + IWM to check path)
```

---

## Future: Phase 3 Integration

**Action-Conditioned IWM + GWM**:

```python
# Plan 5-step sequence
for action_sequence in candidates:
    # IWM: Visual predictions
    visual_future = await iwm.rollout(latent, action_sequence)
    
    # GWM: Tactical predictions (requires action-conditioned GWM)
    tactical_future = await gwm.predict_tactical(game_world, action_sequence)
    
    # Score both
    visual_score = score_visual_trajectory(visual_future)
    tactical_score = score_tactical_trajectory(tactical_future)
    
    # Select best combined outcome
```

This enables **true planning** with both visual and tactical futures.

---

## Summary

**IWM + GWM = Complete World Model**:

- **IWM**: "What it looks like" (visual)
- **GWM**: "What it means" (tactical)
- **Together**: "What to do" (decisions)

**Key Integration Points**:
1. ✅ Both update BeingState independently
2. ✅ ActionArbiter uses both for scoring
3. ✅ LLM gets full context (visual + tactical)
4. ✅ Anomaly detection uses both (surprise + threat)
5. ⏳ Planning uses both (Phase 3: action-conditioned models)

**This is proper world modeling** - not just "embeddings" or "heuristics", but actual predictive models (IWM) + structured state (GWM) working together. 🎯
