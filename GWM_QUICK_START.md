# GWM Quick Start Guide

**TL;DR**: Structured game state → Tactical features → Better decisions

---

## 1. Start Service

```bash
python start_gwm_service.py --port 8002
# Service at: http://localhost:8002
```

---

## 2. Send Snapshot (from engine)

```python
import requests
import time

snapshot = {
    "timestamp": time.time(),
    "player": {
        "id": "player",
        "pos": [0.0, 0.0, 0.0],
        "facing_yaw": 90.0,
        "health": 0.75,
        "in_combat": True
    },
    "npcs": [
        {
            "id": "enemy_001",
            "pos": [10.0, 2.0, 0.0],
            "is_enemy": True,
            "distance_to_player": 10.2,
            "has_line_of_sight_to_player": True,
            "awareness_level": 0.9
        }
    ]
}

response = requests.post("http://localhost:8002/snapshot", json=snapshot)
print(response.json())
```

---

## 3. Get Features

```python
from singularis.gwm import GWMClient

client = GWMClient("http://localhost:8002")
features = await client.get_features()

print(f"Threat level: {features['threat_level']:.2f}")
print(f"Enemies: {features['num_enemies_total']}")
print(f"Nearest enemy: {features['nearest_enemy']['distance']:.1f}m")
```

---

## 4. Use in ActionArbiter

```python
from singularis.gwm import GWMClient

class ActionArbiter:
    def __init__(self):
        self.gwm = GWMClient("http://localhost:8002")
    
    async def request_action(self, being_state, candidates):
        # Get tactical features
        features = await self.gwm.get_features()
        
        # Update BeingState
        being_state.game_world = features
        being_state.gwm_threat_level = features['threat_level']
        
        # Use in decisions
        if features['threat_level'] > 0.7:
            if being_state.health < 0.3:
                # Escape
                return self.escape_action(features['escape_vector'])
            else:
                # Cover
                if features['best_cover_spot']:
                    return self.move_to_cover(features['best_cover_spot'])
        
        # Continue with normal logic
        return self.select_action(candidates)
```

---

## 5. Test Everything

```bash
python test_gwm_system.py
# Should see: ✓ All tests passed!
```

---

## Files Created

**Core (4)**:
- `singularis/gwm/__init__.py`
- `singularis/gwm/game_world_model.py` - Core logic
- `singularis/gwm/gwm_service.py` - FastAPI service
- `singularis/gwm/gwm_client.py` - Client library

**Scripts (2)**:
- `start_gwm_service.py` - Launcher
- `test_gwm_system.py` - Tests

**Docs (4)**:
- `docs/GWM_GUIDE.md` - Complete guide
- `GWM_IMPLEMENTATION_SUMMARY.md` - Summary
- `docs/IWM_GWM_INTEGRATION.md` - Integration patterns
- `GWM_QUICK_START.md` - This file

**Modified (1)**:
- `singularis/core/being_state.py` - Added GWM fields

---

## BeingState Fields

```python
being_state.game_world           # Full features dict
being_state.gwm_threat_level     # 0-1: danger
being_state.gwm_num_enemies      # int
being_state.gwm_nearest_enemy_distance  # float (meters)
being_state.gwm_stealth_safety   # 0-1: higher = safer
being_state.gwm_loot_available   # bool
```

---

## Tactical Features

```python
{
    "threat_level": 0.81,
    "num_enemies_total": 3,
    "num_enemies_in_los": 1,
    "nearest_enemy": {
        "id": "bandit_001",
        "distance": 12.3,
        "bearing_deg": 45.0
    },
    "best_cover_spot": {
        "id": "pillar_01",
        "distance": 4.2,
        "bearing_deg": -30.0
    },
    "escape_vector": [-0.8, -0.6],
    "stealth_safety_score": 0.65,
    "loot_opportunity_available": false
}
```

---

## Integration Examples

### Threat-Based Gating
```python
if being_state.gwm_threat_level > 0.8:
    # Only allow defensive actions
    if action not in DEFENSIVE_ACTIONS:
        return False, "Too dangerous"
```

### Escape Action
```python
if being_state.gwm_threat_level > 0.7 and being_state.health < 0.3:
    escape_vec = being_state.game_world['escape_vector']
    return self.move_in_direction(escape_vec)
```

### Cover Seeking
```python
if being_state.gwm_num_enemies > 2:
    if being_state.game_world['best_cover_spot']:
        cover = being_state.game_world['best_cover_spot']
        return self.move_to_position(cover['pos'])
```

### Opportunistic Looting
```python
if being_state.gwm_loot_available and being_state.gwm_threat_level < 0.2:
    return Action(ActionType.ACTIVATE)
```

---

## With IWM

**IWM**: Visual predictions  
**GWM**: Tactical features  
**Together**: Complete world understanding

```python
# Visual anomaly in dangerous situation?
if being_state.vision_prediction_surprise > 2.0:
    if being_state.gwm_threat_level > 0.7:
        logger.critical("Unexpected visual change during combat!")
        escalate_to_llm()
```

---

## API Endpoints

**POST /snapshot**: Send engine state  
**GET /features**: Get tactical features  
**GET /entities**: Get entity states  
**GET /health**: Service status

---

## Next Steps

1. ✅ **GWM implemented**
2. ⏳ **Engine bridge**: Send snapshots from Papyrus/SKSE
3. ⏳ **ActionArbiter**: Use features in decisions
4. ⏳ **LLM integration**: Pass tactical context
5. ⏳ **IWM fusion**: Combine visual + tactical planning

---

**GWM gives SkyrimAGI tactical awareness** so it can:
- Assess danger (threat_level)
- Find escape routes (escape_vector)
- Identify cover (best_cover_spot)
- Detect opportunities (loot_available)

**Works with IWM** for complete world understanding. 🎯
