# Skyrim AGI Enhancements Summary

## Overview
Comprehensive enhancements to the Skyrim AGI system including terrain-aware planning, strategic planning, menu learning, and memory-augmented generation.

## 1. Terrain-Aware Planning (Non-Narrative)

### Philosophy
- Focus on **environmental reasoning** rather than story/quest knowledge
- Learn terrain features through experience
- Adapt to spatial context (indoor/outdoor/combat/vertical)

### Key Features
- **Terrain Classification**: Automatically classifies scenes into terrain types
  - Indoor spaces (confined, look for exits)
  - Outdoor spaces (open, prioritize forward movement)
  - Danger zones (combat areas, use cover)
  - Vertical features (cliffs, stairs, elevation)
  
- **Terrain Knowledge System**: Learns and tracks:
  - Safe zones (no combat encounters)
  - Danger zones (frequent combat)
  - Indoor/outdoor features
  - Obstacles and navigation paths

- **Terrain Recommendations**: Provides context-specific advice
  - Indoor: "Look for exits", "Interact with objects"
  - Outdoor: "Prioritize forward movement", "Scan horizon"
  - Combat: "Use terrain for cover", "Identify retreat paths"

### LLM Context
Enhanced LLM prompts with:
- Terrain-focused constraints
- No narrative/quest assumptions
- Pure spatial navigation reasoning
- Environmental affordances

## 2. Strategic Planner Neuron

### Philosophy
- **Memory-based planning**: Learn from past experiences
- **Multi-step reasoning**: Plan sequences of actions
- **Pattern recognition**: Identify successful action patterns

### Architecture
```
StrategicPlannerNeuron
├── Episodic Memory (recent experiences)
├── Learned Patterns (successful sequences)
├── Active Plan (current multi-step plan)
└── Success Tracking (plan effectiveness)
```

### Key Features
- **Experience Recording**: Stores context, action, outcome, success
- **Pattern Learning**: Extracts 2-3 action sequences that led to success
- **Plan Generation**: Creates multi-step plans based on learned patterns
- **Adaptive Replanning**: Abandons plans when context changes significantly

### Example
```
Pattern Learned: explore → navigate → explore
Confidence: 0.85
Context: outdoor_spaces, health=100
```

## 3. Menu Interaction Learner

### Philosophy
- **Learn through interaction**: Build mental model of menu structure
- **Optimize navigation**: Find efficient paths through menus
- **Track success rates**: Learn which actions work in which menus

### Architecture
```
MenuLearner
├── Menu History (visited menus)
├── Transition Graph (menu → action → menu)
├── Action Success Rates (menu → action → rate)
└── Menu Structures (learned layouts)
```

### Key Features
- **Menu State Tracking**: Records entering/exiting menus
- **Action Recording**: Tracks success/failure of menu actions
- **Transition Learning**: Builds graph of menu navigation
- **Path Finding**: Finds optimal routes between menus
- **Action Recommendation**: Suggests best actions based on learned success rates

### Example
```
inventory --[exit (85%)]--> exploration
inventory --[equip (70%)]--> inventory
map --[fast_travel (60%)]--> loading
```

## 4. Memory RAG (Retrieval-Augmented Generation)

### Philosophy
- **Learn from experience**: Past successes guide future decisions
- **Context-aware retrieval**: Find similar situations
- **Augment reasoning**: Enhance LLM with relevant memories

### Architecture
```
MemoryRAG
├── Perceptual Memories (what was seen)
│   ├── Visual embeddings
│   ├── Scene types
│   └── Locations
├── Cognitive Memories (decisions made)
│   ├── Situations
│   ├── Actions taken
│   ├── Outcomes
│   └── Success/failure
└── Retrieval System
    ├── Similarity search
    └── Context augmentation
```

### Key Features

#### Perceptual Memory
- Stores visual embeddings from CLIP
- Records scene type and location
- Tracks context (health, combat, layer)
- Retrieves similar visual experiences

#### Cognitive Memory
- Stores situation → action → outcome
- Records success/failure
- Includes reasoning for decisions
- Retrieves similar decision contexts

#### RAG Integration
- **Automatic Storage**: Every perception and action stored
- **Similarity Retrieval**: Cosine similarity on embeddings
- **Context Augmentation**: Adds relevant memories to LLM prompts
- **Success Filtering**: Can retrieve only successful decisions

### Example RAG Augmentation
```
RELEVANT PAST PERCEPTIONS:
1. Similar scene (0.92 match): exploration at Whiterun
2. Similar scene (0.87 match): outdoor at Riverwood

RELEVANT PAST DECISIONS (successful):
1. Similar situation (0.85 match): Action 'explore' → health=100, progress made
   Reasoning: Motivation: curiosity, Layer: Exploration
2. Similar situation (0.78 match): Action 'navigate' → scene=outdoor
   Reasoning: Motivation: autonomy, Layer: Exploration
```

## 5. Forward-Biased Exploration

### Key Changes
- **70% forward movement** (was 25% random)
- **15% left/right strafe** (was 25% each)
- **0% backward** (only for evasive maneuvers)
- **Longer commitments**: 1.5-2.5s per direction (was 1.2-2.0s)
- **Camera scanning**: 60% chance to scan for targets

### Scanning Patterns
1. **Horizontal Sweep**: Left 30° → Right 60° → Center
2. **Vertical Check**: Up 20° → Down 40° → Center
3. **Quick Glance**: 45° left/right → Center

## 6. Stuckness Detection Improvements

### Sensitivity Adjustments
- **Window size**: 5 → 8 frames
- **Similarity threshold**: 0.995 → 0.9985 (99.85%)
- **Consecutive frames**: 4 → 7 required
- **Menu skip**: No detection in inventory/menu scenes
- **Startup delay**: Wait 5+ cycles before checking

## Integration Flow

```
┌─────────────────────────────────────────────────────────┐
│                    PERCEPTION                           │
│  1. Capture screen                                      │
│  2. Generate visual embedding                           │
│  3. Store in RAG (perceptual memory)                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              STRATEGIC PLANNING                         │
│  1. Check if replanning needed                          │
│  2. Generate plan from learned patterns                 │
│  3. Execute plan step OR                                │
│  4. Fall back to LLM/heuristic planning                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│               LLM PLANNING (with RAG)                   │
│  1. Build terrain-aware context                         │
│  2. Retrieve similar perceptions (RAG)                  │
│  3. Retrieve similar decisions (RAG)                    │
│  4. Augment LLM context with memories                   │
│  5. Get LLM response                                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              ACTION EXECUTION                           │
│  1. Check if in menu → use menu learner                 │
│  2. Execute action                                      │
│  3. Record outcome                                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                  LEARNING                               │
│  1. Evaluate action success                             │
│  2. Store in strategic planner                          │
│  3. Store in RAG (cognitive memory)                     │
│  4. Update terrain knowledge                            │
│  5. Update menu learner (if applicable)                 │
└─────────────────────────────────────────────────────────┘
```

## Statistics Tracking

The system now tracks:
- **Strategic Planner**: Patterns learned, plans executed, success rate
- **Menu Learner**: Menus explored, actions taken, transitions learned
- **Memory RAG**: Perceptual memories, cognitive memories, total memories
- **Terrain Knowledge**: Safe zones, danger zones, terrain features

## Example Output

```
Strategic Planner:
  Patterns learned: 12
  Experiences: 87
  Plans executed: 15
  Success rate: 73.3%

Menu Learning:
  Menus explored: 4
  Menu actions: 23
  Transitions learned: 8

Memory RAG:
  Perceptual memories: 156
  Cognitive memories: 87
  Total memories: 243
```

## Benefits

1. **Smarter Planning**: Learns from experience, plans ahead
2. **Better Navigation**: Terrain-aware, forward-biased movement
3. **Menu Mastery**: Learns menu structures, optimizes navigation
4. **Memory-Enhanced**: Past experiences inform future decisions
5. **Adaptive**: Replans when context changes
6. **Non-Narrative**: Focuses on environment, not story

## Future Enhancements

Potential additions:
- Visual object detection for target tracking
- Pathfinding with learned terrain knowledge
- Long-term memory consolidation
- Cross-session memory persistence
- Hierarchical planning (goals → subgoals → actions)
