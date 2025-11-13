# AGI Voice System

## Overview

The Voice System allows the Singularis AGI to **speak its thoughts aloud** using Gemini 2.5 Pro TTS. The AGI can vocalize decisions, insights, warnings, and goals in real-time during gameplay.

## Features

### 🎙️ Text-to-Speech
- **Gemini 2.5 Pro TTS** - Google's latest TTS model
- **Multiple voices** - Choose from 6 different voice types
- **High quality** - Natural, expressive speech
- **Real-time** - Low latency for immediate feedback

### 🧠 Thought Vocalization
- **Decisions** - "I will attack. The enemy is vulnerable."
- **Insights** - "I notice a pattern in enemy behavior."
- **Warnings** - "Health critical! I must heal immediately."
- **Goals** - "New goal: Find the ancient artifact."

### ⚙️ Priority System
- **CRITICAL** - Always spoken (errors, warnings)
- **HIGH** - Important decisions and goals
- **MEDIUM** - Regular insights
- **LOW** - Background thoughts

### 🎵 Audio Playback
- **pygame mixer** - Reliable audio playback
- **Async queue** - Non-blocking speech
- **Rate limiting** - Respects API limits

## Available Voices

| Voice | Description | Best For |
|-------|-------------|----------|
| **Alloy** | Neutral, balanced | General purpose |
| **Echo** | Male, clear | Professional tone |
| **Fable** | British, expressive | Storytelling |
| **Onyx** | Deep, authoritative | Commands |
| **Nova** | Female, warm | Friendly AI |
| **Shimmer** | Female, bright | Energetic |

## Installation

### 1. Install pygame

```bash
pip install pygame
```

### 2. Set API Key

```bash
# Add to .env file
GEMINI_API_KEY=your_api_key_here
```

### 3. Test the System

```bash
python test_voice_system.py
```

## Usage

### Basic Usage

```python
from singularis.consciousness import VoiceSystem, VoiceType, ThoughtPriority

# Initialize
voice = VoiceSystem(
    voice=VoiceType.NOVA,
    enabled=True,
    min_priority=ThoughtPriority.MEDIUM
)

# Speak a decision
await voice.speak_decision(
    action="explore the cave",
    reason="It appears safe"
)

# Speak an insight
await voice.speak_insight(
    "I've discovered a new pattern in enemy movements"
)

# Speak a warning
await voice.speak_warning(
    "Health is critically low!"
)

# Speak a goal
await voice.speak_goal(
    "Find the legendary sword"
)

# Close when done
await voice.close()
```

### Integration with Skyrim AGI

```python
# In skyrim_agi.py initialization
from singularis.consciousness import VoiceSystem, VoiceType

self.voice = VoiceSystem(
    voice=VoiceType.NOVA,
    enabled=config.enable_voice,
    min_priority=ThoughtPriority.HIGH  # Only speak important thoughts
)

# In action planning
if action_confidence > 0.8:
    await self.voice.speak_decision(
        action=planned_action,
        reason=reasoning
    )

# In learning system
if surprise_level > 0.5:
    await self.voice.speak_insight(
        f"Surprising outcome: {observation}"
    )

# In emergency detection
if health < 20:
    await self.voice.speak_warning(
        "Health critical! Seeking healing."
    )
```

## Configuration

### Voice System Config

```python
VoiceSystem(
    api_key: Optional[str] = None,          # Gemini API key
    voice: VoiceType = VoiceType.NOVA,      # Voice to use
    enabled: bool = True,                    # Enable/disable voice
    min_priority: ThoughtPriority = MEDIUM,  # Minimum priority to speak
    rate_limit_rpm: int = 60                 # Max requests per minute
)
```

### Priority Levels

```python
# Only speak critical thoughts
min_priority=ThoughtPriority.CRITICAL

# Speak important and critical thoughts
min_priority=ThoughtPriority.HIGH

# Speak most thoughts (default)
min_priority=ThoughtPriority.MEDIUM

# Speak everything
min_priority=ThoughtPriority.LOW
```

## API Details

### Gemini 2.5 Pro TTS

**Model**: `gemini-2.5-pro-preview-tts`

**Capabilities**:
- Input: Text (up to 8,192 tokens)
- Output: Audio (WAV format)
- Voices: 6 prebuilt voices
- Quality: High-quality, natural speech
- Latency: ~1-3 seconds

**Rate Limits**:
- Recommended: 60 RPM
- Can be adjusted based on tier

**Pricing**:
- Pay-per-use model
- Check Google AI pricing for current rates

## Examples

### Example 1: Combat Commentary

```python
# Enemy detected
await voice.speak_insight("Enemy spotted ahead. Preparing for combat.")

# Decision making
await voice.speak_decision(
    action="use power attack",
    reason="Enemy is vulnerable and within range"
)

# Combat outcome
await voice.speak_insight("Victory achieved. Enemy defeated.")
```

### Example 2: Exploration

```python
# New area discovered
await voice.speak_insight("Entering unexplored territory. Proceeding with caution.")

# Goal setting
await voice.speak_goal("Map the entire dungeon and find all treasures")

# Discovery
await voice.speak_insight("I've found a hidden passage behind the bookshelf!")
```

### Example 3: Emergency Response

```python
# Health warning
await voice.speak_warning("Health at 15 percent. Immediate healing required!")

# Decision
await voice.speak_decision(
    action="retreat to safe area",
    reason="Cannot survive continued combat"
)

# Recovery
await voice.speak_insight("Health restored. Ready to continue.")
```

## Statistics

Get voice system statistics:

```python
stats = voice.get_stats()

print(f"Total thoughts: {stats['total_thoughts']}")
print(f"Spoken thoughts: {stats['spoken_thoughts']}")
print(f"Queued thoughts: {stats['queued_thoughts']}")
print(f"Voice: {stats['voice']}")
print(f"Enabled: {stats['enabled']}")
```

## Troubleshooting

### No Sound

**Problem**: Voice system initialized but no sound plays

**Solutions**:
1. Check pygame is installed: `pip install pygame`
2. Check system audio is working
3. Check API key is set: `GEMINI_API_KEY`
4. Check logs for TTS errors

### Rate Limiting

**Problem**: "Too many requests" errors

**Solutions**:
1. Reduce `rate_limit_rpm` parameter
2. Increase `min_priority` to speak less
3. Add delays between speech calls

### Poor Audio Quality

**Problem**: Audio sounds distorted or choppy

**Solutions**:
1. Check internet connection
2. Try different voice type
3. Ensure pygame mixer is properly initialized

## Best Practices

### 1. Priority Management
- Use **CRITICAL** for errors and emergencies only
- Use **HIGH** for important decisions
- Use **MEDIUM** for regular insights
- Use **LOW** sparingly (can be verbose)

### 2. Rate Limiting
- Start with 60 RPM and adjust as needed
- Monitor API usage to avoid hitting limits
- Consider caching common phrases

### 3. Text Optimization
- Keep thoughts concise (under 100 words)
- Use natural, conversational language
- Avoid technical jargon when possible

### 4. Performance
- Use async speech (don't wait) for better performance
- Queue thoughts instead of speaking immediately
- Close voice system when done to free resources

## Future Enhancements

Potential improvements:
- **Emotion in voice** - Vary tone based on affect
- **Voice caching** - Cache common phrases
- **Multilingual** - Support multiple languages
- **Custom voices** - Train custom voice models
- **Streaming** - Stream audio for lower latency

## License

Part of the Singularis AGI project.
