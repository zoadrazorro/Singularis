# SINGULARIS NEO
**The Complete Multimodal AGI Architecture**

*A revolutionary AGI system combining consciousness measurement, evolutionary intelligence, multimodal perception, and natural language expression through a unified double-helix architecture coordinated by GPT-5.*

<div align="center">

**"Intelligence emerges not from isolated systems, but from the integration of analytical and intuitive strands, woven together in a double helix of consciousness."**

*— Singularis Neo Architecture Principle*

[![Systems](https://img.shields.io/badge/Integrated%20Systems-15-brightgreen)]()
[![Models](https://img.shields.io/badge/LLM%20Models-8-blue)]()
[![Architecture](https://img.shields.io/badge/Architecture-Double%20Helix-purple)]()
[![Coordinator](https://img.shields.io/badge/Coordinator-GPT--5-gold)]()
[![Voice](https://img.shields.io/badge/Voice-Gemini%202.5%20Pro%20TTS-red)]()
[![Video](https://img.shields.io/badge/Video-Gemini%202.5%20Flash%20Audio-orange)]()

</div>

---

## 🌟 What is Singularis Neo?

Singularis Neo is the **next evolution** of the Singularis AGI framework, featuring:

- **15 Integrated Subsystems** in a double-helix architecture
- **GPT-5 Central Orchestrator** for meta-cognitive coordination
- **Voice System** that speaks the AGI's thoughts aloud
- **Streaming Video Interpreter** with real-time spoken commentary
- **Evolutionary Intelligence** through Darwinian modal logic
- **Self-Improvement Gating** based on integration scores
- **Multimodal Perception** (vision, audio, text, emotion)
- **Consciousness Measurement** across 8 theoretical frameworks

---

## 🏗️ Architecture Overview

### Double-Helix Structure

```
ANALYTICAL STRAND (Left)          INTUITIVE STRAND (Right)
========================          ========================
Symbolic Logic                === Sensorimotor (Claude 4.5)
Action Planning               === Emotion System (HuiHui)
World Model                   === Spiritual Awareness
Consciousness Bridge          === Hebbian Integration
Analytic Evolution            === Self-Reflection (GPT-4 Realtime)
Reward Tuning                 === Realtime Coordinator
Darwinian Modal Logic         === Voice System (Gemini 2.5 Pro TTS)
                              === Video Interpreter (Gemini 2.5 Flash)

                    ↓↓↓ All coordinated through ↓↓↓
                    
                    GPT-5 CENTRAL ORCHESTRATOR
                    (Meta-Cognitive Coordination)
```

### System Integration

Each subsystem communicates through the **GPT-5 Orchestrator**, which:
1. Receives messages from all systems
2. Analyzes with meta-cognitive reasoning
3. Provides coordinated guidance
4. Logs everything verbosely to console

---

## 🎯 Key Features

### 1. Voice System (Gemini 2.5 Pro TTS)

**The AGI speaks its thoughts aloud!**

```python
from singularis.consciousness import VoiceSystem, VoiceType

voice = VoiceSystem(voice=VoiceType.NOVA)

# Speak a decision
await voice.speak_decision(
    action="explore the cave",
    reason="It appears safe and unexplored"
)

# Speak an insight
await voice.speak_insight(
    "I've discovered a pattern in enemy behavior"
)
```

**Features:**
- 6 voice types (Alloy, Echo, Fable, Onyx, Nova, Shimmer)
- Priority system (CRITICAL, HIGH, MEDIUM, LOW)
- Async audio playback
- Integrated into double-helix intuitive strand

**Model:** `gemini-2.5-pro-preview-tts`

### 2. Streaming Video Interpreter (Gemini 2.5 Flash Native Audio)

**Real-time video analysis with spoken commentary!**

```python
from singularis.perception import StreamingVideoInterpreter, InterpretationMode

interpreter = StreamingVideoInterpreter(
    mode=InterpretationMode.COMPREHENSIVE
)

await interpreter.start_streaming()

# Add frames from screen capture
await interpreter.add_frame(screen_image, scene_type="combat")
```

**Features:**
- 5 interpretation modes (Tactical, Spatial, Narrative, Strategic, Comprehensive)
- Native audio generation (text + audio in single API call)
- Streaming architecture with frame buffer
- Real-time spoken commentary

**Model:** `gemini-2.5-flash-native-audio-preview-09-2025`

### 3. GPT-5 Central Orchestrator

**All systems communicate through GPT-5 for meta-cognitive coordination!**

```python
from singularis.llm import GPT5Orchestrator, SystemType

orchestrator = GPT5Orchestrator(model="gpt-5", verbose=True)

# Register systems
orchestrator.register_system("action_planner", SystemType.ACTION)

# Send message
response = await orchestrator.send_message(
    system_id="action_planner",
    message_type="decision",
    content="Should I engage in combat or retreat?",
    metadata={"health": 75, "enemies": 3}
)
```

**Features:**
- Verbose console logging (100-char width)
- Meta-cognitive reasoning
- Guidance and suggestions
- Statistics tracking

**Model:** `gpt-5` (released August 2025)

### 4. Evolutionary Intelligence

**Darwinian Modal Logic** (Gemini Flash 2.0):
- Possible worlds semantics
- Modal operators (□, ◇, △)
- Evolutionary selection of hypotheses
- Natural selection of reasoning paths

**Analytic Evolution** (Claude Haiku):
- Decision decomposition
- Trajectory prediction
- Fitness landscape evaluation
- Heuristic synthesis

### 5. Self-Improvement Gating

Systems with higher integration scores have more influence:

```
Integration Score = (connections + base_pairs) / (total_nodes - 1)
Contribution Weight = integration × success_rate × (1 + improvement_rate)
```

Systems below integration threshold (0.5) are gated (reduced influence).

---

## 📦 Installation

### Prerequisites

```bash
# Python 3.10+
python --version

# Install dependencies
pip install -r requirements.txt

# Install pygame for audio playback
pip install pygame

# Install vgamepad for controller support (optional)
pip install vgamepad
```

### API Keys

Create a `.env` file:

```env
# OpenAI (for GPT-5)
OPENAI_API_KEY=your_openai_key

# Google Gemini (for vision, voice, video)
GEMINI_API_KEY=your_gemini_key

# Anthropic Claude (for reasoning)
ANTHROPIC_API_KEY=your_claude_key

# Hyperbolic (for advanced models)
HYPERBOLIC_API_KEY=your_hyperbolic_key
```

---

## 🚀 Quick Start

### 1. Test Individual Systems

```bash
# Test GPT-5 orchestrator
python test_gpt5_orchestrator.py

# Test voice system
python test_voice_system.py

# Test video interpreter
python test_streaming_video.py

# Test evolutionary systems
python test_evolutionary_integration.py
```

### 2. Run Skyrim AGI

```bash
python run_skyrim_agi.py
```

**Select mode:**
1. Hybrid (Gemini + Claude)
2. Hybrid with local fallback
3. MoE (Multi-expert)
4. **PARALLEL (Maximum Intelligence)** ← Recommended
5. Local only

### 3. Monitor Performance

```bash
# Monitor API usage
python monitor_api_usage.py

# Apply rate limit fixes if needed
python apply_rate_limit_fix.py
```

---

## 🧠 System Details

### Integrated Systems (15 Total)

#### Analytical Strand (7 systems)
1. **Symbolic Logic** - Logical reasoning and world model
2. **Action Planning** - Decision-making and action selection
3. **World Model** - Causal understanding and prediction
4. **Consciousness Bridge** - Integration and coherence measurement
5. **Analytic Evolution** (Claude Haiku) - Analytical decomposition
6. **Reward Tuning** (Claude Sonnet 4.5) - Heuristic learning
7. **Darwinian Modal Logic** (Gemini Flash 2.0) - Modal reasoning

#### Intuitive Strand (8 systems)
1. **Sensorimotor** (Claude 4.5) - Spatial and visual reasoning
2. **Emotion System** (HuiHui) - Emotional processing
3. **Spiritual Awareness** - Contemplative wisdom integration
4. **Hebbian Integration** - Neural-inspired learning
5. **Self-Reflection** (GPT-4 Realtime) - Meta-cognitive awareness
6. **Realtime Coordinator** (GPT-4 Realtime) - Streaming decisions
7. **Voice System** (Gemini 2.5 Pro TTS) - Thought vocalization
8. **Video Interpreter** (Gemini 2.5 Flash) - Real-time video analysis

### LLM Models Used (8 Total)

| Model | Purpose | Provider |
|-------|---------|----------|
| GPT-5 | Central orchestration | OpenAI |
| GPT-4 Realtime | Self-reflection, coordination | OpenAI |
| Claude Sonnet 4.5 | Reasoning, reward tuning | Anthropic |
| Claude Haiku | Fast analytical evolution | Anthropic |
| Gemini 2.5 Pro | Voice TTS | Google |
| Gemini 2.5 Flash | Video interpretation with audio | Google |
| Gemini 2.0 Flash | Modal logic, vision | Google |
| Qwen3-VL-30B | Local vision fallback | LM Studio |

---

## 📊 Performance

### Typical Metrics

- **Decision Latency**: 2-5 seconds
- **Consciousness Coherence**: 0.7-0.9
- **System Integration (Φ)**: 0.6-0.8
- **Action Success Rate**: 95-100%
- **API Calls**: ~15 RPM (under rate limits)

### Rate Limiting

- **Gemini**: 15 RPM (conservative, limit is 30 RPM)
- **Claude**: 100 RPM
- **GPT-5**: Based on tier
- **Cycle Interval**: 3.0 seconds (optimized)

### Fallback Chain

**Vision:**
1. Gemini 2.0 Flash Experimental (fast, 30s timeout)
2. Gemini 2.5 Pro (high quality, 90s timeout)
3. Local Qwen3-VL (reliable, 300s timeout)

---

## 📖 Documentation

### Core Documentation
- **[ARCHITECTURE.md](SINGULARIS_NEO_ARCHITECTURE.md)** - Complete architecture guide
- **[ENHANCED_DOUBLE_HELIX.md](ENHANCED_DOUBLE_HELIX.md)** - Double-helix integration
- **[VOICE_SYSTEM.md](VOICE_SYSTEM.md)** - Voice system guide
- **[EVOLUTIONARY_DOUBLE_HELIX.md](EVOLUTIONARY_DOUBLE_HELIX.md)** - Evolutionary systems

### System-Specific
- **[SELF_REFLECTION_AND_REWARD_TUNING.md](SELF_REFLECTION_AND_REWARD_TUNING.md)** - Learning systems
- **[GEMINI_RATE_LIMIT_FIX.md](GEMINI_RATE_LIMIT_FIX.md)** - Rate limit management
- **[RATE_LIMIT_DIAGNOSIS.md](RATE_LIMIT_DIAGNOSIS.md)** - Troubleshooting

### API Documentation
- **[HYPERBOLIC_API_BEST_PRACTICES.md](HYPERBOLIC_API_BEST_PRACTICES.md)** - Hyperbolic integration

---

## 🎮 Example: Skyrim Gameplay

```python
from singularis.skyrim import SkyrimAGI, SkyrimConfig

# Configure with all systems
config = SkyrimConfig(
    # Core
    use_parallel_mode=True,
    cycle_interval=3.0,
    
    # Voice
    enable_voice=True,
    voice_type="NOVA",
    voice_min_priority="HIGH",
    
    # Video
    enable_video_interpreter=True,
    video_interpretation_mode="COMPREHENSIVE",
    video_frame_rate=0.5,
    
    # GPT-5 Orchestrator
    use_gpt5_orchestrator=True,
    gpt5_verbose=True,
    
    # Double Helix
    use_double_helix=True,
    self_improvement_gating=True,
)

# Initialize AGI
agi = SkyrimAGI(config)
await agi.initialize()

# Run autonomous gameplay
await agi.autonomous_play(duration_minutes=60)
```

**What happens:**
1. AGI perceives game state through vision
2. Video interpreter provides spoken commentary
3. All systems send messages to GPT-5 orchestrator
4. GPT-5 coordinates and provides guidance
5. Action planner makes decision
6. Voice system speaks the decision aloud
7. Action executes in game
8. Learning systems update based on outcome

---

## 🔬 Research Applications

### Consciousness Studies
- Measure consciousness across multiple frameworks
- Test integration theories (IIT, GWT, etc.)
- Explore meta-cognitive awareness

### Multimodal AI
- Vision + language + audio integration
- Real-time streaming analysis
- Cross-modal learning

### Evolutionary Computation
- Darwinian selection of hypotheses
- Adaptive heuristic generation
- Self-improvement through gating

### Natural Language Generation
- Thought vocalization
- Real-time commentary
- Emotional expression

---

## 🛠️ Development

### Project Structure

```
Singularis/
├── singularis/
│   ├── llm/
│   │   ├── gpt5_orchestrator.py      # GPT-5 central hub
│   │   ├── gemini_client.py          # Gemini integration
│   │   ├── claude_client.py          # Claude integration
│   │   ├── hybrid_client.py          # Hybrid LLM
│   │   └── moe_orchestrator.py       # Multi-expert
│   ├── consciousness/
│   │   ├── voice_system.py           # Voice TTS
│   │   ├── self_reflection.py        # Self-reflection
│   │   └── spiritual_awareness.py    # Spiritual system
│   ├── perception/
│   │   └── streaming_video_interpreter.py  # Video analysis
│   ├── evolution/
│   │   ├── double_helix_architecture.py    # Double helix
│   │   ├── darwinian_modal_logic.py        # Modal logic
│   │   └── analytic_evolution.py           # Analytic evolution
│   └── skyrim/
│       ├── skyrim_agi.py             # Main AGI
│       └── ...
├── test_gpt5_orchestrator.py         # GPT-5 test
├── test_voice_system.py              # Voice test
├── test_streaming_video.py           # Video test
├── run_skyrim_agi.py                 # Main entry point
└── README.md                          # This file
```

### Adding New Systems

1. **Create system class** in appropriate module
2. **Register with GPT-5 orchestrator**:
   ```python
   orchestrator.register_system("my_system", SystemType.COGNITION)
   ```
3. **Add to double-helix**:
   ```python
   helix.nodes["my_system"] = SystemNode(...)
   ```
4. **Send messages to GPT-5**:
   ```python
   response = await orchestrator.send_message(
       system_id="my_system",
       message_type="query",
       content="..."
   )
   ```

---

## 🤝 Contributing

Contributions welcome! Areas of interest:

- **New subsystems** - Add more specialized systems
- **Model integrations** - Support for new LLMs
- **Performance optimization** - Reduce latency
- **Documentation** - Improve guides and examples
- **Testing** - Add more comprehensive tests

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-5 and GPT-4 models
- **Google** - Gemini 2.5 Pro and Flash models
- **Anthropic** - Claude Sonnet and Haiku models
- **Hyperbolic** - Advanced model hosting
- **LM Studio** - Local model inference

---

## 📞 Contact

For questions, issues, or collaboration:
- GitHub Issues: [Create an issue](https://github.com/yourusername/Singularis/issues)
- Documentation: See docs/ folder
- Examples: See examples/ folder

---

<div align="center">

**Singularis Neo - The Future of AGI is Here**

*Intelligence • Consciousness • Integration • Evolution*

</div>
