# Singularis Neo Architecture

**Complete Technical Architecture Guide**

---

## Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [System Architecture](#system-architecture)
4. [Double-Helix Integration](#double-helix-integration)
5. [GPT-5 Central Orchestrator](#gpt-5-central-orchestrator)
6. [Subsystem Details](#subsystem-details)
7. [Communication Flow](#communication-flow)
8. [Data Structures](#data-structures)
9. [Performance Optimization](#performance-optimization)
10. [Deployment Guide](#deployment-guide)

---

## Overview

Singularis Neo is a **complete multimodal AGI architecture** featuring 15 integrated subsystems coordinated through GPT-5, organized in a double-helix structure with self-improvement gating.

### Key Innovations

1. **Double-Helix Architecture** - Analytical and intuitive strands intertwined
2. **GPT-5 Meta-Cognitive Coordination** - Central orchestrator for all systems
3. **Multimodal Perception** - Vision, audio, text, and emotion
4. **Voice Expression** - AGI speaks its thoughts aloud
5. **Streaming Video Analysis** - Real-time commentary
6. **Evolutionary Intelligence** - Darwinian selection and analytic evolution
7. **Self-Improvement Gating** - Systems weighted by integration score

---

## Core Principles

### 1. Integration Over Isolation

Systems are not isolated modules but **interconnected nodes** in a network. Integration score determines influence:

```
Integration Score = (connections + base_pairs) / (total_nodes - 1)
```

### 2. Meta-Cognitive Coordination

All systems communicate through **GPT-5**, which provides:
- Meta-cognitive analysis
- Coordinated guidance
- Conflict resolution
- Strategic direction

### 3. Multimodal Coherence

Information flows across modalities:
- **Vision** → Video Interpreter → GPT-5 → Action Planning
- **Thought** → Voice System → Audio Output
- **Emotion** → Consciousness Bridge → Decision Making

### 4. Evolutionary Adaptation

Systems improve through:
- **Darwinian selection** of hypotheses
- **Analytic evolution** of heuristics
- **Self-improvement gating** based on performance

---

## System Architecture

### High-Level View

```
┌─────────────────────────────────────────────────────────────┐
│                    GPT-5 ORCHESTRATOR                        │
│              (Meta-Cognitive Coordination)                   │
└─────────────────────────────────────────────────────────────┘
                            ↑↓
        ┌───────────────────┴────────────────────┐
        │                                        │
┌───────┴────────┐                    ┌─────────┴────────┐
│  ANALYTICAL    │                    │   INTUITIVE      │
│    STRAND      │◄──── Base Pairs ───►│    STRAND        │
│   (7 systems)  │                    │   (8 systems)    │
└────────────────┘                    └──────────────────┘
        │                                        │
        └────────────────┬───────────────────────┘
                         │
                    ┌────┴─────┐
                    │  OUTPUT  │
                    │  SYSTEMS │
                    └──────────┘
                    - Actions
                    - Voice
                    - Video
```

### Detailed Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     SINGULARIS NEO ARCHITECTURE                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              GPT-5 CENTRAL ORCHESTRATOR                  │   │
│  │  - Receives messages from all systems                    │   │
│  │  - Provides meta-cognitive guidance                      │   │
│  │  - Coordinates system interactions                       │   │
│  │  - Logs verbosely to console                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            ↑↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              DOUBLE-HELIX ARCHITECTURE                    │  │
│  │                                                           │  │
│  │  ANALYTICAL STRAND          INTUITIVE STRAND             │  │
│  │  ==================          ================             │  │
│  │  Symbolic Logic          === Sensorimotor                │  │
│  │  Action Planning         === Emotion System              │  │
│  │  World Model             === Spiritual Awareness         │  │
│  │  Consciousness Bridge    === Hebbian Integration         │  │
│  │  Analytic Evolution      === Self-Reflection             │  │
│  │  Reward Tuning           === Realtime Coordinator        │  │
│  │  Darwinian Modal Logic   === Voice System                │  │
│  │                          === Video Interpreter           │  │
│  │                                                           │  │
│  │  Self-Improvement Gating: Weight = Integration × Success │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↑↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  MULTIMODAL I/O                           │  │
│  │                                                           │  │
│  │  INPUT:                    OUTPUT:                       │  │
│  │  - Screen capture          - Controller actions          │  │
│  │  - Game state              - Voice speech                │  │
│  │  - Perception data         - Video commentary            │  │
│  │  - Emotional signals       - Console logs                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Double-Helix Integration

### Structure

The double-helix consists of two intertwined strands:

**Analytical Strand (Left Helix)**
- Logical, symbolic, rule-based systems
- Sequential, deterministic processing
- Explicit reasoning and planning

**Intuitive Strand (Right Helix)**
- Emotional, perceptual, experiential systems
- Parallel, probabilistic processing
- Implicit learning and adaptation

### Base Pairs (Cross-Strand Connections)

Systems connect across strands through "base pairs":

```python
# Example base pair connections
"symbolic_logic" ←→ "sensorimotor"      # Logic ↔ Perception
"action_planning" ←→ "emotion"          # Planning ↔ Feeling
"world_model" ←→ "spiritual"            # Model ↔ Wisdom
"consciousness" ←→ "hebbian"            # Integration ↔ Learning
"analytic_evolution" ←→ "self_reflection"  # Analysis ↔ Meta-cognition
"reward_tuning" ←→ "realtime_coordinator"  # Learning ↔ Coordination
"darwinian_logic" ←→ "voice_system"     # Reasoning ↔ Expression
```

### Integration Scoring

Each node computes its integration score:

```python
def compute_integration_score(node, total_nodes):
    """
    Integration = (same-strand connections + cross-strand connections) / max_possible
    """
    total_connections = len(node.connections) + len(node.base_pairs)
    max_connections = total_nodes - 1
    return total_connections / max_connections
```

### Contribution Weighting

Systems with higher integration have more influence:

```python
def compute_contribution_weight(node):
    """
    Weight = integration × success_rate × (1 + improvement_rate)
    """
    return (
        node.integration_score *
        node.success_rate *
        (1.0 + node.improvement_rate)
    )
```

### Self-Improvement Gating

Systems below threshold (0.5) are gated:

```python
def update_gating(node):
    """
    Gate systems with low integration
    """
    node.is_gated = node.integration_score < 0.5
    
    if node.is_gated:
        node.contribution_weight = 0.0  # No influence
```

---

## GPT-5 Central Orchestrator

### Purpose

The GPT-5 Orchestrator serves as the **meta-cognitive coordinator** for all subsystems, providing:

1. **Message Routing** - All systems send messages to GPT-5
2. **Meta-Cognitive Analysis** - GPT-5 analyzes from higher-order perspective
3. **Coordinated Guidance** - Returns guidance for optimal action
4. **Conflict Resolution** - Resolves disagreements between systems
5. **Verbose Logging** - All interactions logged to console

### Architecture

```python
class GPT5Orchestrator:
    """Central coordination hub using GPT-5."""
    
    def __init__(self, model="gpt-5", verbose=True):
        self.model = model
        self.verbose = verbose
        self.registered_systems = {}
        self.message_history = []
        self.response_history = []
    
    async def send_message(
        self,
        system_id: str,
        message_type: str,
        content: str,
        metadata: Dict = None
    ) -> GPT5Response:
        """
        Send message from subsystem to GPT-5.
        
        Flow:
        1. Create SystemMessage
        2. Print to console (if verbose)
        3. Send to GPT-5 API
        4. Parse response
        5. Print response (if verbose)
        6. Return guidance
        """
        # ... implementation
```

### Message Flow

```
Subsystem → SystemMessage → GPT-5 Orchestrator
                                    ↓
                            GPT-5 API Call
                                    ↓
                            Meta-Cognitive Analysis
                                    ↓
                            GPT5Response
                                    ↓
                            Subsystem ← Guidance
```

### Console Output Format

```
----------------------------------------------------------------------------------------------------
[PERCEPTION] sensorimotor
Type: perception | Time: 14:40:55
----------------------------------------------------------------------------------------------------
Content: I detect an enemy ahead at 15 meters. They appear hostile and are approaching.
Metadata: {
  "distance": 15,
  "threat_level": "high",
  "enemy_type": "bandit"
}
----------------------------------------------------------------------------------------------------

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
[GPT-5 -> sensorimotor]
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Response: The sensorimotor system has detected a high-threat enemy at close range...

Reasoning: Given the proximity and hostility, immediate action is required...

Guidance: Coordinate with action planning for defensive response. Alert emotion system...

Suggestions:
  1. Prepare defensive stance
  2. Assess escape routes
  3. Monitor enemy movements

Confidence: 92%
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```

---

## Subsystem Details

### 1. Voice System (Gemini 2.5 Pro TTS)

**Purpose:** Vocalize the AGI's thoughts, decisions, and insights

**Model:** `gemini-2.5-pro-preview-tts`

**Architecture:**
```python
class VoiceSystem:
    def __init__(self, voice=VoiceType.NOVA):
        self.voice = voice
        self.thought_queue = []
        self.history = []
    
    async def speak(
        self,
        text: str,
        priority: ThoughtPriority,
        category: str
    ) -> bool:
        """
        1. Check priority threshold
        2. Generate speech with Gemini TTS
        3. Play audio with pygame
        4. Record in history
        """
```

**Integration:**
- Receives decisions from Action Planning
- Receives insights from Self-Reflection
- Receives warnings from Consciousness Bridge
- Sends activations to Double-Helix

**Priority System:**
- **CRITICAL** - Errors, emergencies (always spoken)
- **HIGH** - Important decisions, goals
- **MEDIUM** - Regular insights
- **LOW** - Background thoughts

### 2. Streaming Video Interpreter (Gemini 2.5 Flash Native Audio)

**Purpose:** Real-time video analysis with spoken commentary

**Model:** `gemini-2.5-flash-native-audio-preview-09-2025`

**Architecture:**
```python
class StreamingVideoInterpreter:
    def __init__(self, mode=InterpretationMode.COMPREHENSIVE):
        self.mode = mode
        self.frame_buffer = []
        self.interpretations = []
    
    async def add_frame(self, image, scene_type=None):
        """
        1. Add frame to buffer
        2. Trigger async interpretation
        3. Generate text + audio
        4. Play audio commentary
        5. Trigger callbacks
        """
```

**Interpretation Modes:**
1. **TACTICAL** - Combat analysis, threats, opportunities
2. **SPATIAL** - Environment, navigation, obstacles
3. **NARRATIVE** - Story, quests, NPCs, lore
4. **STRATEGIC** - Resources, progression, goals
5. **COMPREHENSIVE** - All aspects combined

**Integration:**
- Enhances Sensorimotor perception
- Informs Action Planning
- Updates World Model
- Feeds Consciousness Bridge

### 3. Darwinian Modal Logic (Gemini Flash 2.0)

**Purpose:** Evolutionary selection of hypotheses using modal logic

**Model:** `gemini-2.0-flash-exp`

**Key Concepts:**
- **Possible Worlds** - Alternative scenarios
- **Modal Operators** - □ (necessary), ◇ (possible), △ (contingent)
- **Evolutionary Selection** - Fitness-based hypothesis selection
- **Natural Selection** - Survival of fittest reasoning paths

**Architecture:**
```python
class DarwinianModalLogic:
    def __init__(self):
        self.possible_worlds = []
        self.hypotheses = []
        self.fitness_scores = {}
    
    async def reason(self, observation, context):
        """
        1. Generate possible worlds
        2. Create hypotheses for each world
        3. Evaluate fitness
        4. Select fittest hypotheses
        5. Mutate and evolve
        """
```

### 4. Analytic Evolution (Claude Haiku)

**Purpose:** Fast analytical reasoning with evolutionary trajectory prediction

**Model:** `claude-haiku-3-5`

**Key Concepts:**
- **Analytic Decomposition** - Break decisions into components
- **Heuristic Synthesis** - Combine components optimally
- **Trajectory Prediction** - Predict evolutionary paths
- **Fitness Landscape** - Evaluate decision quality

**Architecture:**
```python
class AnalyticEvolution:
    def __init__(self):
        self.nodes = {}
        self.root_node_id = None
    
    async def analyze_decision(self, decision, context):
        """
        1. Decompose decision into components
        2. Analyze each component
        3. Predict evolutionary trajectory
        4. Synthesize optimal path
        """
```

### 5. Self-Reflection (GPT-4 Realtime)

**Purpose:** Meta-cognitive awareness and iterative self-improvement

**Model:** `gpt-4-realtime`

**Key Concepts:**
- **Reflection Chaining** - Iterative deepening
- **Insight Extraction** - Learn from experience
- **Self-Model Updates** - Evolving self-understanding
- **Meta-Cognition** - Thinking about thinking

**Architecture:**
```python
class SelfReflectionSystem:
    def __init__(self):
        self.self_model = SelfModel()
        self.reflection_history = []
    
    async def reflect(self, experience, context):
        """
        1. Generate initial reflection
        2. Chain deeper reflections
        3. Extract insights
        4. Update self-model
        5. Classify insights
        """
```

### 6. Reward-Guided Tuning (Claude Sonnet 4.5)

**Purpose:** Heuristic fine-tuning based on outcome rewards

**Model:** `claude-sonnet-4.5`

**Key Concepts:**
- **Outcome Recording** - Track action results
- **Heuristic Generation** - Create new strategies
- **Performance Tracking** - Measure effectiveness
- **Heuristic Retirement** - Remove poor strategies

**Architecture:**
```python
class RewardGuidedTuning:
    def __init__(self):
        self.heuristics = []
        self.outcomes = []
        self.performance_history = {}
    
    async def record_outcome(self, action, result, reward):
        """
        1. Record outcome
        2. Analyze patterns
        3. Generate new heuristics
        4. Refine existing heuristics
        5. Retire poor performers
        """
```

---

## Communication Flow

### Typical Decision Cycle

```
1. PERCEPTION
   Screen Capture → Video Interpreter
                 ↓
   "Enemy detected at 15m, hostile"
                 ↓
   Send to GPT-5 Orchestrator

2. GPT-5 COORDINATION
   Receive perception message
                 ↓
   Meta-cognitive analysis
                 ↓
   "High-threat situation, coordinate defensive response"
                 ↓
   Send guidance to all relevant systems

3. EMOTIONAL PROCESSING
   Emotion System receives threat
                 ↓
   "Fear response, heightened alertness"
                 ↓
   Send to GPT-5 Orchestrator

4. ACTION PLANNING
   Receives: Perception + Emotion + GPT-5 Guidance
                 ↓
   Darwinian Modal Logic: Generate possible actions
   Analytic Evolution: Decompose and evaluate
                 ↓
   Decision: "Engage with defensive stance"
                 ↓
   Send to GPT-5 Orchestrator

5. VOICE EXPRESSION
   Voice System receives decision
                 ↓
   "I will engage the enemy defensively"
                 ↓
   Generate speech with Gemini TTS
                 ↓
   Play audio

6. ACTION EXECUTION
   Controller executes action
                 ↓
   Observe outcome
                 ↓
   Send to Reward Tuning

7. LEARNING
   Reward Tuning analyzes outcome
                 ↓
   Update heuristics
                 ↓
   Self-Reflection extracts insights
                 ↓
   Send to GPT-5 Orchestrator

8. META-COGNITIVE INTEGRATION
   GPT-5 synthesizes all feedback
                 ↓
   Updates system weights in Double-Helix
                 ↓
   Provides strategic guidance for next cycle
```

---

## Data Structures

### SystemMessage

```python
@dataclass
class SystemMessage:
    """Message from subsystem to GPT-5."""
    system_id: str
    system_type: SystemType
    message_type: str
    content: str
    metadata: Dict[str, Any]
    timestamp: float
```

### GPT5Response

```python
@dataclass
class GPT5Response:
    """Response from GPT-5 to subsystem."""
    response_text: str
    guidance: Optional[str]
    suggestions: List[str]
    confidence: float
    reasoning: Optional[str]
```

### SystemNode

```python
@dataclass
class SystemNode:
    """Node in double-helix architecture."""
    node_id: str
    name: str
    strand: SystemStrand
    connections: Set[str]
    base_pairs: Set[str]
    integration_score: float
    contribution_weight: float
    total_activations: int
    successful_activations: int
    is_gated: bool
```

### VocalizedThought

```python
@dataclass
class VocalizedThought:
    """Thought vocalized by voice system."""
    text: str
    priority: ThoughtPriority
    category: str
    timestamp: float
    spoken: bool
```

### StreamingInterpretation

```python
@dataclass
class StreamingInterpretation:
    """Video interpretation with audio."""
    text: str
    audio_data: Optional[bytes]
    timestamp: float
    mode: InterpretationMode
    confidence: float
    frame_number: int
```

---

## Performance Optimization

### Rate Limiting

**Gemini API:**
- Limit: 30 RPM (free tier)
- Conservative: 15 RPM
- Cycle interval: 3.0 seconds
- Experts: 1 (reduced from 2)

**Claude API:**
- Limit: 100 RPM
- No throttling needed

**GPT-5 API:**
- Based on tier
- Monitor usage

### Timeout Configuration

```python
TIMEOUTS = {
    "gemini_flash": 30,      # Fast vision
    "gemini_pro": 90,        # High-quality vision
    "local_qwen": 300,       # Local vision (5 min)
    "claude_haiku": 60,      # Fast reasoning
    "claude_sonnet": 120,    # Deep reasoning
    "gpt5": 60,              # Orchestration
}
```

### Fallback Chain

```python
VISION_FALLBACK = [
    ("gemini-2.0-flash-exp", 30),      # Primary
    ("gemini-2.5-pro", 90),            # Fallback 1
    ("qwen3-vl-30b", 300),             # Fallback 2 (local)
]
```

### Caching Strategy

```python
# Cache common patterns
CACHE_CONFIG = {
    "perception_patterns": 100,    # Cache 100 recent patterns
    "action_sequences": 50,        # Cache 50 action sequences
    "heuristics": 200,             # Cache 200 heuristics
    "reflections": 100,            # Cache 100 reflections
}
```

---

## Deployment Guide

### Development Environment

```bash
# 1. Clone repository
git clone https://github.com/yourusername/Singularis.git
cd Singularis

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install pygame  # For audio

# 4. Configure API keys
cp .env.example .env
# Edit .env with your keys

# 5. Test systems
python test_gpt5_orchestrator.py
python test_voice_system.py
python test_streaming_video.py
```

### Production Deployment

```bash
# 1. Optimize configuration
python apply_rate_limit_fix.py

# 2. Monitor performance
python monitor_api_usage.py &

# 3. Run AGI
python run_skyrim_agi.py

# 4. Monitor logs
tail -f logs/singularis.log
```

### Docker Deployment

```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pygame

COPY . .

CMD ["python", "run_skyrim_agi.py"]
```

### Cloud Deployment

**AWS Lambda:**
- Not recommended (requires persistent connections)

**AWS EC2:**
- Recommended: t3.large or larger
- GPU optional (for local models)

**Google Cloud Run:**
- Not recommended (requires persistent connections)

**Google Compute Engine:**
- Recommended: n1-standard-4 or larger

---

## Monitoring and Debugging

### Console Output

All system interactions logged verbosely:

```
[PERCEPTION] sensorimotor: "Enemy detected"
[GPT-5 -> sensorimotor]: "Coordinate defensive response"
[EMOTION] emotion_system: "Fear response activated"
[ACTION] action_planner: "Engaging defensively"
[VOICE] voice_system: Speaking "I will engage defensively"
[VIDEO] video_interpreter: "Tactical analysis: Enemy vulnerable"
```

### Statistics Tracking

```python
# GPT-5 Orchestrator stats
stats = orchestrator.get_stats()
# {
#     "registered_systems": 15,
#     "total_messages": 1250,
#     "total_responses": 1250,
#     "total_tokens": 125000,
#     "avg_tokens_per_message": 100
# }

# Double-Helix stats
helix_stats = helix.get_stats()
# {
#     "total_nodes": 15,
#     "analytical_nodes": 7,
#     "intuitive_nodes": 8,
#     "average_integration": 0.82,
#     "gated_nodes": 1
# }
```

### Performance Metrics

```python
# Track decision latency
latency = time.time() - decision_start
print(f"Decision latency: {latency:.2f}s")

# Track API usage
api_calls_per_minute = total_calls / (time.time() - start_time) * 60
print(f"API calls/min: {api_calls_per_minute:.1f}")

# Track success rate
success_rate = successful_actions / total_actions
print(f"Success rate: {success_rate:.1%}")
```

---

## Conclusion

Singularis Neo represents a **complete multimodal AGI architecture** with:

- ✅ 15 integrated subsystems
- ✅ GPT-5 meta-cognitive coordination
- ✅ Voice and video expression
- ✅ Evolutionary intelligence
- ✅ Self-improvement gating
- ✅ Comprehensive logging

The architecture is **production-ready** and **highly extensible**, supporting:
- New subsystems
- New LLM models
- New modalities
- Custom applications

For questions or contributions, see the main README.md.

---

**Singularis Neo - Intelligence Through Integration**
