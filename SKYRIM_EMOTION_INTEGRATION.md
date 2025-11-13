# Skyrim AGI Emotion Integration

## Overview

Based on the session analysis from **skyrim_agi_20251113_085956**, this document describes how to integrate the **HuiHui Emotion System** into Skyrim AGI for emotion-aware gameplay.

## Session Analysis Insights

The 39.5-minute session revealed key emotional triggers:

### Combat Scenarios (Dominant Context)
- **Health Critical** situations → FEAR, SADNESS
- **Successful kills** → JOY, FORTITUDE, PRIDE
- **Taking damage** → FEAR, ANXIETY
- **Stuck/trapped** → FRUSTRATION, SHAME
- **Healing priority** (0.84 confidence) → HOPE, RELIEF

### Resource Management
- **ResourcesLow** predicate → ANXIETY, CONCERN
- **StaminaLow** → FATIGUE (passive sadness)
- **Successful resource acquisition** → RELIEF, JOY

### Adaptive Behaviors
- **Dodge/Block success** → FORTITUDE (active strength)
- **Bash/Attack success** → DESIRE, AGGRESSION
- **Failed actions** → SHAME, FRUSTRATION

## Emotion-to-Action Mapping

Based on Spinoza's affects theory and Skyrim gameplay:

| Emotion | Intensity | Recommended Actions | Decision Weights |
|---------|-----------|---------------------|------------------|
| **FEAR** | High (>0.7) | Retreat, Heal, Defensive | ↑ Caution, ↓ Aggression |
| **FORTITUDE** | High (>0.7) | Attack, Bash, Power Attack | ↑ Aggression, ↓ Caution |
| **JOY** | Medium-High | Continue strategy, Explore | ↑ All drives |
| **SADNESS** | High | Heal, Retreat, Regroup | ↓ All drives |
| **CURIOSITY** | Any | Explore, Investigate, Loot | ↑ Exploration |
| **HOPE** | Medium | Cautious advance, Heal | ↑ Exploration, ↑ Caution |
| **SHAME** | High | Change strategy, Learn | ↓ Aggression |
| **PRIDE** | Medium | Maintain strategy | ↑ Confidence |

## Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Skyrim AGI                           │
│                                                         │
│  ┌──────────────┐      ┌──────────────────┐           │
│  │  Perception  │─────▶│  Game State      │           │
│  │  (Vision)    │      │  (Health, etc.)  │           │
│  └──────────────┘      └────────┬─────────┘           │
│                                  │                      │
│                                  ▼                      │
│                    ┌─────────────────────────┐         │
│                    │ Emotion Integration     │         │
│                    │ (HuiHui Engine)         │         │
│                    └────────┬────────────────┘         │
│                             │                           │
│                             ▼                           │
│         ┌───────────────────────────────────┐          │
│         │   Emotion State                   │          │
│         │   - Primary: FEAR                 │          │
│         │   - Intensity: 0.85               │          │
│         │   - Valence: -0.80                │          │
│         │   - Decision Weights:             │          │
│         │     * Caution: 0.9                │          │
│         │     * Aggression: 0.2             │          │
│         └───────────┬───────────────────────┘          │
│                     │                                   │
│                     ▼                                   │
│  ┌──────────────────────────────────────────┐          │
│  │  Action Planning                         │          │
│  │  (Emotion-Influenced)                    │          │
│  │  - Retreat recommended (high caution)    │          │
│  │  - Healing prioritized (fear response)   │          │
│  └──────────────────────────────────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Implementation Steps

### 1. Add Emotion Integration to SkyrimAGI

```python
# In skyrim_agi.py __init__

from .emotion_integration import SkyrimEmotionIntegration, SkyrimEmotionContext
from ..emotion import EmotionConfig

# Add to component initialization
print("  [X/11] Emotion system (HuiHui)...")
self.emotion_integration = SkyrimEmotionIntegration(
    emotion_config=EmotionConfig(
        lm_studio_url=self.config.lm_studio_url,
        model_name="huihui-moe-60b-a38",
        temperature=0.8,
        decay_rate=0.1
    )
)
```

### 2. Process Emotions in Main Loop

```python
# In main gameplay loop

async def _process_cycle(self, cycle: int):
    # 1. Perceive game state
    game_state = await self.perception.perceive()
    
    # 2. Build emotion context from game state
    emotion_context = SkyrimEmotionContext(
        in_combat=(game_state.scene_type == SceneType.COMBAT),
        health_percent=game_state.health / 100.0,
        stamina_percent=game_state.stamina / 100.0,
        health_critical=(game_state.health < 30),
        stamina_low=(game_state.stamina < 30),
        enemy_nearby=game_state.in_combat,
        coherence_delta=consciousness_state.coherence_delta,
        adequacy_score=consciousness_state.adequacy
    )
    
    # 3. Process emotion
    emotion_state = await self.emotion_integration.process_game_state(
        game_state=game_state.__dict__,
        context=emotion_context
    )
    
    # 4. Use emotion to influence decisions
    if self.emotion_integration.should_retreat():
        # Emotion suggests retreat
        action = self._plan_retreat_action(game_state)
    elif self.emotion_integration.should_be_aggressive():
        # Emotion suggests aggression
        action = self._plan_aggressive_action(game_state)
    else:
        # Normal planning with emotion weights
        action = self._plan_action_with_emotion(
            game_state,
            emotion_state
        )
    
    # 5. Log emotion state
    self.emotion_integration.log_emotion_state(cycle)
```

### 3. Emotion-Influenced Action Planning

```python
def _plan_action_with_emotion(
    self,
    game_state: GameState,
    emotion_state: EmotionState
) -> Action:
    """Plan action influenced by emotional state."""
    
    # Get emotion modifiers
    aggression = self.emotion_integration.get_decision_modifier('aggression')
    caution = self.emotion_integration.get_decision_modifier('caution')
    exploration = self.emotion_integration.get_exploration_drive()
    
    # Adjust action probabilities based on emotion
    if game_state.in_combat:
        if aggression > 0.7:
            # High aggression → offensive actions
            action_probs = {
                'power_attack': 0.4,
                'bash': 0.3,
                'attack': 0.2,
                'block': 0.1
            }
        elif caution > 0.7:
            # High caution → defensive actions
            action_probs = {
                'block': 0.4,
                'dodge': 0.3,
                'heal': 0.2,
                'retreat': 0.1
            }
        else:
            # Balanced approach
            action_probs = {
                'attack': 0.3,
                'block': 0.3,
                'dodge': 0.2,
                'bash': 0.2
            }
    else:
        if exploration > 0.7:
            # High exploration drive
            action_probs = {
                'explore': 0.5,
                'loot': 0.3,
                'investigate': 0.2
            }
        else:
            # Normal exploration
            action_probs = {
                'move_forward': 0.5,
                'look_around': 0.3,
                'wait': 0.2
            }
    
    # Select action
    return self._select_action_from_probs(action_probs)
```

### 4. Session Reporting with Emotions

```python
def get_session_report(self) -> Dict[str, Any]:
    """Generate session report including emotional analysis."""
    
    base_report = self._get_base_report()
    
    # Add emotion summary
    emotion_summary = self.emotion_integration.get_session_summary()
    
    base_report['emotion_analysis'] = {
        'dominant_emotion': emotion_summary['dominant_emotion'],
        'average_valence': emotion_summary['average_valence'],
        'average_intensity': emotion_summary['average_intensity'],
        'combat_emotions': emotion_summary['combat_emotions'],
        'exploration_emotions': emotion_summary['exploration_emotions'],
        'final_weights': emotion_summary['current_weights']
    }
    
    return base_report
```

## Expected Emotional Patterns

Based on the session analysis, we expect:

### Combat-Heavy Sessions
- **Dominant emotions**: FEAR (30%), FORTITUDE (25%), DESIRE (20%)
- **Average valence**: -0.2 to 0.1 (slightly negative due to danger)
- **Average intensity**: 0.6-0.8 (high due to combat stress)

### Exploration Sessions
- **Dominant emotions**: CURIOSITY (40%), JOY (25%), HOPE (20%)
- **Average valence**: 0.2 to 0.5 (positive)
- **Average intensity**: 0.4-0.6 (moderate)

### Mixed Sessions (like the analyzed one)
- **Dominant emotions**: FEAR (25%), FORTITUDE (20%), CURIOSITY (15%)
- **Average valence**: -0.1 to 0.2 (neutral to slightly positive)
- **Average intensity**: 0.5-0.7 (moderate-high)

## Emotion-Based Metrics

New metrics to track:

1. **Emotional Coherence**: How well emotions match situation
2. **Emotional Stability**: Variance in emotion intensity over time
3. **Emotional Adaptability**: Speed of emotion transitions
4. **Emotion-Action Alignment**: How well actions match emotional state

## Configuration

```python
# In SkyrimConfig

@dataclass
class SkyrimConfig:
    # ... existing fields ...
    
    # Emotion system
    use_emotion_system: bool = True
    emotion_model: str = "huihui-moe-60b-a38"
    emotion_temperature: float = 0.8
    emotion_decay_rate: float = 0.1
    
    # Emotion influence on decisions
    emotion_influence_weight: float = 0.3  # How much emotions affect decisions
    emotion_override_threshold: float = 0.85  # When emotions override logic
```

## Testing

Test emotion integration with:

```bash
python examples/test_skyrim_emotion.py
```

This will:
1. Simulate various game scenarios
2. Compute emotional responses
3. Show emotion-influenced decisions
4. Generate emotion distribution charts

## Performance Impact

- **LLM-based emotion**: +500-1000ms per cycle
- **Rule-based emotion**: +<1ms per cycle
- **Memory overhead**: ~100KB per 1000 emotions
- **Recommended**: Use rule-based for real-time, LLM for analysis

## Future Enhancements

1. **Emotion Memory**: Remember emotional responses to locations/NPCs
2. **Emotion Learning**: Learn which emotions lead to better outcomes
3. **Emotion Contagion**: Model NPC emotional states
4. **Emotion-Based Dialogue**: Choose dialogue options based on emotions
5. **Emotional Fatigue**: Model emotional exhaustion from prolonged combat

## Example Session Output

```
[EMOTION] Cycle 540: fear (intensity=0.85, valence=-0.80, PASSIVE)
  → High caution (0.9), Low aggression (0.2)
  → Recommended: RETREAT and HEAL

[EMOTION] Cycle 585: fortitude (intensity=0.72, valence=0.60, ACTIVE)
  → High aggression (0.8), Low caution (0.3)
  → Recommended: ATTACK and BASH

[EMOTION] Cycle 915: curiosity (intensity=0.65, valence=0.40, ACTIVE)
  → High exploration (0.8)
  → Recommended: EXPLORE and INVESTIGATE

Session Summary:
  Dominant Emotion: fear (28%)
  Average Valence: -0.15 (slightly negative)
  Average Intensity: 0.68 (moderate-high)
  Combat Emotions: {fear: 15, fortitude: 12, desire: 8}
  Exploration Emotions: {curiosity: 10, joy: 5, hope: 3}
```

## Integration Checklist

- [ ] Add `SkyrimEmotionIntegration` to `SkyrimAGI.__init__`
- [ ] Initialize emotion engine in `initialize_llm`
- [ ] Build `SkyrimEmotionContext` from game state
- [ ] Process emotions in main loop
- [ ] Use emotion weights in action planning
- [ ] Log emotion states for debugging
- [ ] Add emotion summary to session reports
- [ ] Test with various scenarios
- [ ] Tune emotion influence weights
- [ ] Document emotional patterns

---

**Status**: Ready for integration  
**Priority**: High (adds emotional intelligence to combat/exploration)  
**Estimated Integration Time**: 2-3 hours  
**Testing Time**: 1-2 hours
