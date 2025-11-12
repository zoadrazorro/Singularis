# Visual Learning Pipeline for Sensorimotor Reasoning

## Overview
Multi-stage visual learning pipeline that feeds visual analysis from Gemini and local models into Claude Sonnet 4.5 for advanced sensorimotor and geospatial reasoning.

## Pipeline Architecture

### Stage 1: Gemini 2.0 Flash Vision Analysis
**Purpose:** Primary visual perception and spatial understanding

**Input:** Screenshot from game
**Prompt:** "Describe the visual scene focusing on: spatial layout, obstacles, pathways, terrain features, landmarks, and any navigational cues. Be specific about what's visible in each direction."

**Output:** Detailed visual description (512 tokens max)
**Timeout:** 15 seconds

**Example Output:**
```
The scene shows an indoor stone corridor with torches on the left wall. 
A wooden door is visible ahead at approximately 10 meters. The right 
side has a stone pillar partially blocking the view. The floor appears 
to be cobblestone with some debris. No immediate obstacles in the 
forward path, but the corridor narrows near the door.
```

### Stage 2: Local Qwen3-VL Analysis (Backup/Supplement)
**Purpose:** Supplementary visual analysis, especially for navigation

**Input:** Same screenshot
**Prompt:** "Analyze this Skyrim scene for navigation: describe obstacles, open paths, terrain type, and spatial features."

**Output:** Navigation-focused description (256 tokens max)
**Timeout:** 10 seconds

**Example Output:**
```
Open path forward. Stone walls on both sides. No visible obstacles 
in immediate path. Indoor dungeon terrain. Door ahead suggests 
transition point. Recommend forward movement.
```

### Stage 3: Visual Similarity Computation
**Purpose:** Detect if agent is stuck (not making visual progress)

**Method:** Cosine similarity between current and previous CLIP embeddings
**Threshold:** 0.95 (95% similar = stuck)

**Output:**
```
Visual similarity to last frame: 0.97 (STUCK)
```
or
```
Visual similarity to last frame: 0.73 (MOVING)
```

### Stage 4: Claude Sonnet 4.5 Sensorimotor Synthesis
**Purpose:** Deep reasoning combining all visual inputs with extended thinking

**Input:** 
- Gemini visual analysis
- Local visual analysis  
- Visual similarity metrics
- Game state (location, terrain, recent actions)
- Movement history

**System Prompt:**
```
You are a sensorimotor and geospatial reasoning expert for a Skyrim 
AI agent. You receive visual analysis from Gemini and local vision 
models. Use extended thinking to deeply analyze spatial relationships, 
movement patterns, and navigation strategies based on the visual 
information provided.
```

**Extended Thinking:** 10,000 token budget for deep reasoning

**Output Format:**
- Obstacle Status: [clear/blocked/uncertain]
- Navigation Recommendation: [action + reasoning based on visual analysis]
- Spatial Memory: [new/familiar/uncertain]
- Exploration Direction: [direction + reasoning from visual cues]
- Confidence: [0.0-1.0]

**Timeout:** 90 seconds

## RAG Memory Storage

### Stored Content
```
SENSORIMOTOR & GEOSPATIAL ANALYSIS:

VISUAL LEARNING (from Gemini & Local Models):
[Gemini analysis]
[Local analysis]

CLAUDE SONNET 4.5 ANALYSIS:
[Sensorimotor reasoning]

EXTENDED THINKING PROCESS:
[Internal reasoning chain]
```

### Context Metadata
```python
{
    'type': 'sensorimotor_geospatial',
    'location': 'Bleak Falls Barrow',
    'terrain': 'indoor_dungeon',
    'scene': 'exploration',
    'cycle': 25,
    'repeated_action': 'move_forward',
    'repeat_count': 3,
    'has_gemini_visual': True,
    'has_local_visual': True,
    'visual_similarity': '0.73 (MOVING)'
}
```

## Integration with Stuck Detection

### Visual Progress Tracking
The pipeline feeds into the stuck detection system:

1. **Repeated Action Detection:** 
   - If same action repeated 10+ times
   - **BUT** visual similarity < 0.95 (making progress)
   - → Allow continuation (e.g., walking forward while exploring)

2. **True Stuck Detection:**
   - Same action repeated 10+ times
   - **AND** visual similarity > 0.95 (not making progress)
   - → Force different action

### Example Scenarios

**Scenario 1: Exploring (Not Stuck)**
```
Action: move_forward (repeated 8x)
Visual similarity: 0.72 (MOVING)
Gemini: "New corridor section, different wall textures"
Result: ✓ Allow continuation - making visual progress
```

**Scenario 2: Stuck Against Wall**
```
Action: move_forward (repeated 10x)
Visual similarity: 0.98 (STUCK)
Gemini: "Same stone wall directly ahead, no change"
Result: ⚠️ STUCK DETECTED - force different action (turn/jump)
```

## Execution Flow

```
Every 5 cycles:
  ├─ Get Gemini visual analysis (15s timeout)
  ├─ Get Local visual analysis (10s timeout)
  ├─ Compute visual similarity
  ├─ Build comprehensive query
  ├─ Invoke Claude Sonnet 4.5 with extended thinking (90s timeout)
  ├─ Parse analysis + thinking
  └─ Store in RAG memory with full context
```

## Benefits

1. **Multi-Model Visual Understanding:**
   - Gemini: High-quality spatial descriptions
   - Local: Fast backup analysis
   - Claude: Deep synthesis with reasoning

2. **Stuck Detection Enhancement:**
   - Visual similarity prevents false positives
   - Allows exploration (repeated move_forward with progress)
   - Catches true stuck states (no visual change)

3. **Knowledge Accumulation:**
   - All visual learning stored in RAG
   - Spatial memory builds over time
   - Can retrieve similar situations

4. **Extended Thinking:**
   - Claude has 10,000 tokens to reason deeply
   - Can analyze complex spatial relationships
   - Provides detailed navigation strategies

## Performance Characteristics

- **Total Time:** ~115 seconds worst case (15 + 10 + 90)
- **Frequency:** Every 5 cycles (~40-50 seconds per cycle)
- **Memory:** Stores ~2-4KB per analysis in RAG
- **Fallback:** Graceful degradation if any stage fails

## Future Enhancements

- Image-based retrieval from RAG (similar visual scenes)
- Landmark recognition and mapping
- Path history visualization
- Spatial graph construction
- Multi-frame temporal analysis
