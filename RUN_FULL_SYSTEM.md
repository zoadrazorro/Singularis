# 🚀 Run Singularis FULL SYSTEM

**Updated**: November 14, 2025  
**Status**: ✅ ALL APIs + ALL Systems Enabled

---

## Quick Start

### 1. Set Environment Variables

```bash
# Required (must have)
export OPENAI_API_KEY='sk-...'        # GPT-5
export GEMINI_API_KEY='AI...'         # Gemini 2.5
export ANTHROPIC_API_KEY='sk-ant-...' # Claude 3.5

# Optional (recommended for full features)
export PERPLEXITY_API_KEY='pplx-...'      # Research
export OPENROUTER_API_KEY='sk-or-...'     # MetaCognition
export HYPERBOLIC_API_KEY='...'           # Qwen3-235B
export GITHUB_TOKEN='ghp_...'             # OpenRouter fallback
```

### 2. Run the System

```bash
# Default: 30 minutes, balanced profile, all systems
python run_beta_v2.4_cloud.py --duration 1800

# Full hour with verbose logging
python run_beta_v2.4_cloud.py --duration 3600 --verbose

# Fast test (5 minutes, no voice/video)
python run_beta_v2.4_cloud.py --duration 300 --fast
```

---

## What's Enabled

### ✅ ALL Cloud APIs (7 sources)
- **GPT-5** - Central orchestrator
- **Gemini 2.5 Flash** - Vision + Video + Voice
- **Claude 3.5 Haiku/Sonnet** - Reasoning
- **Perplexity AI** - Research advisor
- **OpenRouter** - MetaCognition (GPT-4o/DeepSeek)
- **Hyperbolic** - Qwen3-235B
- **DeepSeek** - Alternative reasoning

### ✅ ALL Systems (15+ subsystems)
- **Voice System** - Gemini TTS (NOVA voice)
- **Video Interpreter** - Real-time gameplay analysis
- **GPT-5 Orchestrator** - Meta-cognitive coordination
- **Double Helix** - 15 analytical + intuitive systems
- **Main Brain** - Session tracking & memory
- **Research Advisor** - Perplexity queries
- **MetaCognition Advisor** - Meta-level planning
- **Continuum** - Predictive consciousness
- **HaackLang** - Polyrhythmic execution (10 Hz)
- **SCCE** - Temporal cognitive dynamics

---

## Profiles

Choose cognitive personality with `--profile`:

| Profile | Behavior | Best For |
|---------|----------|----------|
| **balanced** | Moderate regulation (default) | General gameplay |
| **anxious** | Emotions linger, cautious | Survival horror |
| **stoic** | Fast recovery, calm | Boss fights |
| **curious** | Low stress, exploratory | Discovery |
| **aggressive** | Fast reactions, impulsive | Combat |
| **cautious** | Slow to act, risk averse | Dangerous areas |

Example:
```bash
python run_beta_v2.4_cloud.py --duration 3600 --profile stoic
```

---

## Performance Modes

### 🏎️ Fast Mode
```bash
python run_beta_v2.4_cloud.py --duration 1800 --fast
```
- 1s cycle interval
- Voice disabled
- Video disabled
- **Use for**: Quick tests, debugging

### 🐢 Conservative Mode
```bash
python run_beta_v2.4_cloud.py --duration 3600 --conservative
```
- 5s cycle interval
- 1 expert per API (instead of 2)
- SCCE every 5 cycles
- **Use for**: Cost reduction, overnight runs

---

## Expected Output

### Startup Banner
```
================================================================================
                                                                  
   🧠 SINGULARIS BETA v2.4 - FULL SYSTEM 🚀
   "One Being, Striving for Coherence"
   ALL APIs + ALL Systems + HaackLang + SCCE
                                                                  
================================================================================

    ✅ ALL Cloud APIs Enabled:
       • GPT-5 (Central Orchestrator)
       • Gemini 2.5 Flash (Vision + Video)
       • Claude 3.5 Haiku/Sonnet (Reasoning)
       • Perplexity AI (Research Advisor)
       • OpenRouter (MetaCognition)
       • Hyperbolic (Qwen3-235B)
    
    ✅ ALL Systems Active:
       • Voice System (Gemini TTS)
       • Video Interpreter (Real-time)
       • Research Advisor
       • MetaCognition Advisor
       • Double Helix (15 subsystems)
       • Main Brain (Session tracking)
       • Continuum (Predictive)
```

### Status Dashboard
```
☁️  [Cloud APIs]
   • GPT-5: ✅ (Orchestrator)
   • Gemini: ✅ (Vision + Video + Voice)
   • Claude: ✅ (Reasoning)
   • Perplexity: ✅
   • OpenRouter: ✅
   • Hyperbolic: ❌ (no API key)

🎯 [Systems]
   • Voice: ✅
   • Video: ✅
   • GPT-5 Orchestrator: ✅
   • Double Helix: ✅
   • Main Brain: ✅
   • Research Advisor: ✅
   • MetaCognition: ✅
   • Continuum: ✅
```

---

## Cost Estimates

### Per Hour
- **Conservative**: $0.50-1.00
- **Default**: $1.50-2.50
- **Verbose**: $2.50-4.00

### API Breakdown
- GPT-5: 40% (~$1.00/hour)
- Gemini: 25% (~$0.60/hour)
- Claude: 25% (~$0.60/hour)
- Perplexity: 5% (~$0.15/hour)
- OpenRouter: 5% (~$0.15/hour)

---

## Monitoring

### During Run
Watch for:
- `[SCCE]` - Cognitive dynamics (fear, trust, stress)
- `[HAACK]` - Polyrhythmic execution
- `Δ𝒞` - Coherence changes
- `ℓₒ, ℓₛ, ℓₚ` - Three Lumina balance

### After Run
Check:
- `sessions/` - Main Brain reports
- Console output - Final statistics
- HaackLang stats - Global beat count

---

## Troubleshooting

### "Missing API key"
Add the required environment variables to `.env` file:
```bash
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AI...
ANTHROPIC_API_KEY=sk-ant-...
```

### "429 Rate Limit Error"
Use conservative mode:
```bash
python run_beta_v2.4_cloud.py --duration 3600 --conservative
```

### "Unicode errors"
The UTF-8 fix is already included. If you still see errors:
```bash
set PYTHONIOENCODING=utf-8  # Windows
export PYTHONIOENCODING=utf-8  # Linux/Mac
```

---

## Advanced Options

### Custom Cycle Interval
```bash
python run_beta_v2.4_cloud.py --duration 3600 --cycle-interval 2.5
```

### Disable Specific Systems
```bash
# No voice
python run_beta_v2.4_cloud.py --duration 3600 --no-voice

# No video
python run_beta_v2.4_cloud.py --duration 3600 --no-video

# Both
python run_beta_v2.4_cloud.py --duration 3600 --no-voice --no-video
```

### Verbose Logging
```bash
python run_beta_v2.4_cloud.py --duration 3600 --verbose
```
Shows:
- HaackLang execution details
- GPT-5 orchestration messages
- Detailed subsystem communication

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    GPT-5 Orchestrator                     │
│            (Meta-Cognitive Coordination)                  │
└────────────────────┬─────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐            ┌────▼────┐
    │ Gemini  │            │ Claude  │
    │ (2x)    │            │ (2x)    │
    │Vision   │            │Reasoning│
    │Video    │            │Strategy │
    │Voice    │            │         │
    └────┬────┘            └────┬────┘
         │                      │
         └──────────┬───────────┘
                    │
         ┌──────────▼──────────┐
         │   Double Helix      │
         │   (15 Subsystems)   │
         │   Analytical +      │
         │   Intuitive         │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │   BeingState        │
         │   C_global → [0,1]  │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │   HaackLang         │
         │   (10 Hz Execution) │
         └─────────────────────┘
```

---

## Next Steps

1. **Test the system**:
   ```bash
   python run_beta_v2.4_cloud.py --duration 300 --verbose
   ```

2. **Monitor performance**:
   ```bash
   python monitor_api_usage.py
   ```

3. **Review session reports**:
   ```bash
   ls -l sessions/
   ```

4. **Try different profiles**:
   ```bash
   python run_beta_v2.4_cloud.py --duration 1800 --profile anxious
   python run_beta_v2.4_cloud.py --duration 1800 --profile stoic
   python run_beta_v2.4_cloud.py --duration 1800 --profile curious
   ```

---

## Status: READY TO RUN 🚀

The complete AGI architecture is operational with:
- ✅ 7 API sources
- ✅ 15+ integrated systems
- ✅ Voice + Video perception
- ✅ Research + MetaCognition
- ✅ HaackLang + SCCE
- ✅ Continuum predictive consciousness

**This is the most advanced Singularis system to date.**

Run it now:
```bash
python run_beta_v2.4_cloud.py --duration 3600 --profile balanced
```
