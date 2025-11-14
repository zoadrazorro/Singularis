# Vision System Configuration Summary

**Date**: November 14, 2025  
**Status**: ✅ GPT Vision (GPT-4o) Active

---

## Current Configuration

### Primary Vision: GPT-4o Vision
- **Model**: `gpt-4o` with vision capabilities
- **Experts**: 2 parallel experts
- **Purpose**: Primary visual perception and understanding
- **Quality**: Superior object recognition, scene understanding, OCR
- **Speed**: 1-2 seconds per request
- **Cost**: ~$0.01 per image (1024x1024)

### Video Analysis: Gemini 2.5 Flash
- **Model**: `gemini-2.5-flash-native-audio`
- **Experts**: 1 expert
- **Purpose**: Real-time video interpretation with spoken commentary
- **Features**: Native audio generation, streaming architecture
- **Modes**: Tactical, Spatial, Narrative, Strategic, Comprehensive

### Voice: Gemini 2.5 Pro TTS
- **Model**: `gemini-2.5-pro-preview-tts`
- **Voice**: NOVA (best quality)
- **Purpose**: Text-to-speech for system thoughts and decisions
- **Priority**: Medium+ priority messages

---

## API Responsibilities

### OpenAI (OPENAI_API_KEY)
- ✅ GPT-5 - Central orchestrator
- ✅ GPT-4o Vision - Primary visual perception (2 experts)

### Google (GEMINI_API_KEY)
- ✅ Gemini 2.5 Flash - Video interpretation (1 expert)
- ✅ Gemini 2.5 Pro TTS - Voice system

### Anthropic (ANTHROPIC_API_KEY)
- ✅ Claude 3.5 Haiku/Sonnet - Reasoning (2 experts)

---

## Vision Processing Flow

```
Game Screen
     ↓
Screenshot Capture
     ↓
┌─────────────────────┐
│  GPT-4o Vision      │ ← Primary (2 experts in parallel)
│  (gpt-4o)           │
└─────────────────────┘
     ↓
Visual Understanding
  • Objects detected
  • Scene analyzed
  • UI elements read
  • Text extracted (OCR)
  • Spatial relationships
     ↓
GPT-5 Orchestrator
     ↓
Action Decision
```

---

## Video Processing Flow (Parallel)

```
Game Screen
     ↓
Video Stream
     ↓
┌─────────────────────────────┐
│  Gemini 2.5 Flash           │
│  (Native Audio)             │
└─────────────────────────────┘
     ↓
Video Analysis + Commentary
  • Tactical analysis
  • Spatial awareness
  • Narrative context
  • Strategic planning
     ↓
Spoken Audio Output
     ↓
Audio Playback (pygame)
```

---

## Expert Pool Configuration

### Default Mode
```python
num_gpt_vision_experts: 2    # GPT-4o Vision
num_gemini_experts: 1        # Video + Voice
num_claude_experts: 2        # Reasoning
```

### Fast Mode
```python
# Vision disabled for speed
enable_video_interpreter: False
```

### Conservative Mode
```python
num_gpt_vision_experts: 1    # Reduced
num_gemini_experts: 1        # Video + Voice
num_claude_experts: 1        # Reduced
```

---

## Why GPT-4o Vision?

### Advantages
1. **Superior Quality**
   - Better object recognition
   - Advanced scene understanding
   - Excellent OCR capabilities
   - UI element detection

2. **Better Reasoning**
   - Can reason about visual content
   - Strategic decision making
   - Context understanding
   - Threat assessment

3. **Unified API**
   - Same API as GPT-5
   - Single rate limit pool
   - Consistent error handling
   - Easier management

4. **Faster Response**
   - 1-2s vs 2-3s (Gemini)
   - Lower latency
   - Better for real-time gameplay

### Trade-offs
- **Cost**: 4x more expensive than Gemini Vision
- **Rate Limits**: Shares pool with GPT-5
- **Dependency**: Single point of failure (OpenAI)

---

## Cost Analysis

### Per Hour (Default Mode)
- **GPT-5**: ~$1.00 (orchestration)
- **GPT-4o Vision**: ~$0.80 (2 experts, ~80 images/hour)
- **Gemini**: ~$0.40 (video + voice)
- **Claude**: ~$0.60 (reasoning)
- **Total**: ~$2.80/hour

### Per Hour (Conservative Mode)
- **GPT-5**: ~$0.50
- **GPT-4o Vision**: ~$0.40 (1 expert)
- **Gemini**: ~$0.30
- **Claude**: ~$0.30
- **Total**: ~$1.50/hour

---

## Rate Limits

### OpenAI
- **GPT-5**: 10,000 TPM (tokens per minute)
- **GPT-4o Vision**: 30 RPM (requests per minute)
- **Combined**: Shared rate limit pool

### Google Gemini
- **Gemini 2.5 Flash**: 30 RPM (free tier)
- **Gemini 2.5 Pro TTS**: 30 RPM (free tier)

### Anthropic Claude
- **Claude 3.5**: 100 RPM (tier 1)

---

## Fallback Chain

### Vision Fallback
1. **GPT-4o Vision** (primary, 2 experts)
2. **Claude Vision** (if available)
3. **Local Qwen3-VL** (if enabled)

### Video Fallback
1. **Gemini 2.5 Flash** (primary)
2. **Disabled** (no fallback)

### Voice Fallback
1. **Gemini 2.5 Pro TTS** (primary)
2. **OpenAI TTS** (if Gemini fails)
3. **Disabled** (silent mode)

---

## Monitoring

### What to Watch
```
[VISION] GPT-4o processing frame...
[VISION] Detected: 3 enemies, health bar at 60%
[VIDEO] Gemini analyzing tactical situation...
[VOICE] Speaking: "Enemy approaching from left"
```

### Performance Metrics
- Vision latency: 1-2s
- Video latency: 2-3s
- Voice latency: 1-2s
- Total perception: ~3-5s

---

## Configuration File

Location: `run_beta_v2.4_cloud.py`

Key settings:
```python
# Line ~169-172
config.use_gemini_vision = False
config.use_gpt_vision = True
config.use_claude_reasoning = True
config.use_gpt5_orchestrator = True

# Line ~193-195
config.num_gpt_vision_experts = 2
config.num_gemini_experts = 1
config.num_claude_experts = 2
```

---

## Testing

### Test Vision System
```bash
python run_beta_v2.4_cloud.py --duration 300 --verbose
```

Watch for:
- `[VISION]` - GPT-4o vision processing
- `[VIDEO]` - Gemini video analysis
- `[VOICE]` - Gemini TTS output

### Test Without Vision (Fast Mode)
```bash
python run_beta_v2.4_cloud.py --duration 300 --fast
```

---

## Troubleshooting

### "GPT-4o Vision not available"
- Check OPENAI_API_KEY is set
- Verify API key has GPT-4o access
- Check rate limits (30 RPM)

### "Vision too slow"
- Use conservative mode (1 expert)
- Increase cycle interval
- Use fast mode (disable vision)

### "Too expensive"
- Use conservative mode
- Reduce num_gpt_vision_experts to 1
- Consider switching back to Gemini Vision

---

## Status: ACTIVE ✅

Current vision configuration:
- ✅ **GPT-4o Vision** - Primary (2 experts)
- ✅ **Gemini 2.5 Flash** - Video (1 expert)
- ✅ **Gemini 2.5 Pro TTS** - Voice
- ✅ **Claude 3.5** - Reasoning (2 experts)

**Quality**: Superior  
**Speed**: Fast (1-2s)  
**Cost**: ~$2.80/hour (default mode)
