# Dream Analysis System 🌙

Automated Jungian/Freudian dream analysis with Fitbit wake detection and Meta Glasses Messenger bot integration.

---

## Overview

The Dream Analysis System automatically prompts you to record your dreams each morning when you wake up, then provides deep psychological analysis using both Jungian and Freudian frameworks.

### Key Features

✨ **Automatic Wake Detection** - Fitbit monitors sleep and detects when you wake up  
📱 **Messenger Bot Prompts** - Sends personalized prompts via Meta Glasses  
🎤 **Voice Dictation** - Dictate dreams naturally via voice  
🧠 **Dual Analysis** - Jungian archetypal + Freudian psychoanalytic interpretation  
📊 **Pattern Tracking** - Identifies recurring symbols, themes, and patterns  
💡 **Actionable Insights** - Personalized psychological recommendations  

---

## Quick Start

### 1. Install Dependencies

```bash
pip install requests aiohttp asyncio
```

### 2. Set Up Integrations

**Fitbit:**
- Create developer app at [dev.fitbit.com](https://dev.fitbit.com)
- Get OAuth access token with `sleep` scope

**Messenger:**
- Ensure meta-glasses-api extension is running
- Create Messenger group chat named "Dream Journal"
- Start monitoring in extension

### 3. Run System

```python
from dream_system_integration import DreamAnalysisSystem
import asyncio

system = DreamAnalysisSystem(
    fitbit_token="YOUR_TOKEN",
    fitbit_user_id="YOUR_USER_ID",
    messenger_chat_name="Dream Journal"
)

# Start monitoring (runs continuously)
asyncio.run(system.start())
```

That's it! The system will now automatically prompt you each morning.

---

## How It Works

### Daily Workflow

```
1. 😴 You sleep (Fitbit tracking)
2. ☀️ You wake up (Fitbit detects)
3. 📱 Prompt sent to Messenger
4. 🎤 You dictate your dream
5. 🔮 System analyzes dream
6. 📊 Analysis sent back to you
7. 📈 Patterns tracked over time
```

### Example Interaction

**Morning Prompt:**
> Good morning! ☀️  
> You had excellent sleep (quality: 85/100)!  
> Did you have any dreams?

**You dictate:**
> "I was in a dark forest with a snake following me. I felt anxious. Then I found a bridge over water and crossed it. An old man smiled at me and I felt peaceful."

**Analysis received:**
> 🔮 **Dream Analysis Complete**
> 
> **Jungian:** Forest = unconscious mind. Snake = transformation (Shadow archetype). Bridge = transition. Old man = Wise Old Man archetype offering guidance.
> 
> **Freudian:** Anxiety suggests repressed content. Snake may represent transformation or fear. Water symbolizes the unconscious.
> 
> **Synthesis:** Journey from fear to acceptance. Processing anxiety about change while seeking wisdom.
> 
> **Recommendations:**
> • Explore what changes you're resisting
> • Practice shadow integration
> • Seek guidance from mentors

---

## Components

### 1. Dream Analyst (`dream_analyst.py`)

Core analysis engine with:
- Jungian archetypal interpretation
- Freudian psychoanalytic interpretation
- Symbol dictionary (expandable)
- Emotional tone detection
- Theme extraction
- Pattern recognition

**Key Classes:**
- `DreamAnalyst` - Main analysis engine
- `DreamRecord` - Stores dream data
- `DreamAnalysis` - Analysis results
- `DreamSymbol` - Symbol interpretation

### 2. Fitbit Integration (`fitbit_integration.py`)

Sleep tracking and wake detection:
- OAuth 2.0 authentication
- Sleep data retrieval
- Wake-up detection
- Sleep quality scoring
- REM sleep tracking

**Key Classes:**
- `FitbitIntegration` - Main API wrapper
- `SleepData` - Sleep session data

### 3. Messenger Bot (`messenger_dream_bot.py`)

Communication via Meta Glasses:
- Personalized prompts
- Voice transcription handling
- Analysis delivery
- Weekly summaries
- Template system

**Key Classes:**
- `MessengerDreamBot` - Bot interface
- `MetaGlassesAPIBridge` - Extension bridge

### 4. Integration System (`dream_system_integration.py`)

Complete automated workflow:
- Connects all components
- Manages callbacks
- Handles state
- Provides analytics

**Key Class:**
- `DreamAnalysisSystem` - Complete system

---

## Analysis Frameworks

### Jungian Analysis

**Focus:** Collective unconscious, archetypes, individuation

**Key Concepts:**
- **Archetypes:** Universal symbols (Self, Shadow, Anima/Animus, Wise Old Man, etc.)
- **Collective Unconscious:** Shared human psychological inheritance
- **Individuation:** Process of becoming psychologically whole
- **Compensation:** Dreams balance one-sided conscious attitudes

**Example Interpretation:**
> "The snake represents your Shadow - repressed aspects seeking integration. The old man is the Wise Old Man archetype offering guidance on your individuation journey."

### Freudian Analysis

**Focus:** Personal unconscious, wish fulfillment, repression

**Key Concepts:**
- **Manifest Content:** Surface story of dream
- **Latent Content:** Hidden unconscious meaning
- **Dream Work:** Mechanisms that disguise wishes (displacement, condensation, symbolization)
- **Wish Fulfillment:** Dreams satisfy unconscious desires

**Example Interpretation:**
> "Anxiety in the dream suggests repressed content. The snake may represent sexual energy or transformation. Water symbolizes the unconscious and birth."

### Combined Synthesis

The system integrates both frameworks:
- Personal unconscious (Freud) + Collective unconscious (Jung)
- Individual wishes + Universal patterns
- Psychological development + Archetypal guidance

---

## Symbol Dictionary

### Jungian Symbols

| Symbol | Meaning | Archetype |
|--------|---------|-----------|
| Water | Unconscious mind | Self |
| Snake | Transformation, healing | Shadow |
| Mountain | Spiritual ascent | Self |
| Forest | Unknown, unconscious | Shadow |
| Bridge | Transition, connection | Self |
| Old Man | Wisdom, guidance | Wise Old Man |
| Mother | Nurturing, origin | Great Mother |
| Fire | Transformation, passion | Self |

### Freudian Symbols

| Symbol | Meaning |
|--------|---------|
| Snake | Phallic symbol, sexual energy |
| Water | Birth, womb, unconscious |
| House | The self, body |
| Stairs | Sexual intercourse |
| Flying | Sexual desire, freedom |
| Falling | Loss of control, anxiety |
| Teeth | Castration anxiety, aging |

*Note: Symbols can be added and customized*

---

## Pattern Recognition

The system tracks patterns across dreams:

### Recurring Symbols
Identifies symbols that appear multiple times and their psychological significance.

### Recurring Themes
Tracks themes like pursuit, transformation, falling, flying, death, birth.

### Emotional Patterns
Monitors emotional tone trends (anxious, fearful, joyful, peaceful).

### Sleep Correlation
Analyzes how sleep quality affects dream characteristics.

---

## Analytics

### Dream Statistics

```python
report = system.dream_analyst.get_dream_report(days=30)
```

Returns:
- Total dreams recorded
- Most common themes
- Most common symbols
- Emotional distribution
- Dream type breakdown
- Pattern-based recommendations

### Sleep-Dream Correlation

```python
correlation = system.get_dream_statistics(30)['correlation']
```

Analyzes:
- High quality sleep dreams vs low quality
- REM sleep impact on dream recall
- Sleep duration effects

### Weekly Summaries

Automatically sent every week with:
- Dreams recorded
- Top themes and symbols
- Recurring patterns
- Key insights

---

## Customization

### Personal Symbol Associations

```python
analyst.personal_symbol_associations['car'] = "Freedom and independence"
```

### Custom Jungian Symbols

```python
analyst.jungian_symbols['dragon'] = {
    'jungian': 'Primal power, transformation',
    'archetype': JungianArchetype.SHADOW
}
```

### Prompt Templates

```python
templates = messenger.get_prompt_templates()
templates['morning_prompt'] = "Your custom prompt..."
```

### Analysis Framework

```python
# Choose framework
analysis = analyst.analyze_dream(
    dream_id="dream_123",
    framework=AnalysisFramework.JUNGIAN  # or FREUDIAN or COMBINED
)
```

---

## Files

| File | Purpose |
|------|---------|
| `dream_analyst.py` | Core analysis engine |
| `fitbit_integration.py` | Fitbit API wrapper |
| `messenger_dream_bot.py` | Messenger bot interface |
| `dream_system_integration.py` | Complete system integration |
| `demo_dream_system.py` | Full workflow demo |
| `DREAM_SYSTEM_SETUP.md` | Detailed setup guide |

---

## Requirements

- Python 3.8+
- Fitbit account with developer app
- Meta Glasses or Messenger app
- meta-glasses-api browser extension
- Dependencies: `requests`, `aiohttp`, `asyncio`

---

## Privacy

- All dreams stored locally
- No cloud storage by default
- Fitbit OAuth tokens are revocable
- Messenger uses end-to-end encryption
- Use environment variables for credentials

---

## Tips for Better Dream Recall

1. **Set intention before sleep:** "I will remember my dreams"
2. **Don't move when waking:** Stay still to preserve memory
3. **Record immediately:** Use voice dictation right away
4. **Keep consistent sleep schedule:** Improves recall
5. **Avoid alcohol:** Reduces REM sleep
6. **Practice regularly:** Recall improves over time

---

## Expected Results

**Week 1-2:** Learning to remember, 2-3 dreams/week  
**Week 3-4:** Improved recall, 4-5 dreams/week  
**Month 2-3:** Strong recall, 5-7 dreams/week, patterns emerging  
**Month 3+:** Excellent recall, rich symbolism, deep insights, potential lucid dreaming

---

## Support

See `DREAM_SYSTEM_SETUP.md` for:
- Detailed setup instructions
- Troubleshooting guide
- Configuration options
- Advanced features

---

## Demo

Run the complete demo:

```bash
python demo_dream_system.py
```

This demonstrates the full workflow from wake detection to analysis delivery.

---

**Sweet dreams and happy analyzing! 🌙✨**

*Part of the Sophia Personal AI Life Assistant suite*
