## Dream Analysis System - Complete Setup Guide

Automated dream recording and Jungian/Freudian analysis system that integrates with Fitbit and Meta Glasses Messenger bot.

---

## 🌙 System Overview

**Workflow:**
1. **Fitbit** detects when you wake up
2. **Messenger bot** sends prompt via Meta Glasses
3. You **dictate your dream** via voice
4. System **analyzes** using Jungian + Freudian frameworks
5. Sends **interpretation** back to you
6. Tracks **patterns** over time

---

## 📋 Prerequisites

### 1. Fitbit Setup

**Required:**
- Fitbit device (any model with sleep tracking)
- Fitbit account

**Steps:**
1. Create Fitbit developer app at [dev.fitbit.com](https://dev.fitbit.com)
2. Get OAuth 2.0 credentials (Client ID, Client Secret)
3. Authorize app with `sleep` scope
4. Obtain access token

**Quick OAuth Flow:**
```python
from fitbit_integration import get_fitbit_auth_url, exchange_code_for_token

# Step 1: Get authorization URL
auth_url = get_fitbit_auth_url(
    client_id="YOUR_CLIENT_ID",
    redirect_uri="http://localhost:8080/callback"
)
print(f"Visit: {auth_url}")

# Step 2: After user authorizes, exchange code for token
tokens = exchange_code_for_token(
    code="AUTHORIZATION_CODE",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="http://localhost:8080/callback"
)

# Save these:
ACCESS_TOKEN = tokens['access_token']
USER_ID = tokens['user_id']
```

### 2. Meta Glasses / Messenger Setup

**Required:**
- Meta Ray-Ban Smart Glasses OR standalone Messenger app
- Alternative Facebook account for bot
- meta-glasses-api browser extension

**Steps:**
1. **Install meta-glasses-api extension:**
   ```bash
   cd integrations/meta-glasses-api
   bun install
   bun run dev:chrome  # or brave, firefox
   ```

2. **Create Messenger group chat:**
   - Create group with 2 other accounts
   - Remove one account (minimum for group)
   - Rename chat to "Dream Journal"
   - Add group photo (optional)
   - Set nickname for bot account

3. **Sync with Meta Glasses:**
   - Open Meta View app
   - Go to Communications → Messenger
   - Disconnect and reconnect Messenger
   - This syncs the new "Dream Journal" chat

4. **Start monitoring:**
   - Sign into alt Facebook account
   - Go to messenger.com or facebook.com/messages
   - Open "Dream Journal" chat
   - Start monitoring in extension

### 3. Python Dependencies

```bash
pip install requests aiohttp asyncio
```

---

## 🚀 Quick Start

### Option 1: Automated System (Recommended)

```python
from dream_system_integration import DreamAnalysisSystem
import asyncio

# Initialize with your credentials
system = DreamAnalysisSystem(
    fitbit_token="YOUR_FITBIT_ACCESS_TOKEN",
    fitbit_user_id="YOUR_FITBIT_USER_ID",
    messenger_chat_name="Dream Journal"
)

# Start monitoring (runs continuously)
asyncio.run(system.start())
```

That's it! The system will now:
- Monitor Fitbit for wake-ups
- Send prompts via Messenger
- Analyze dreams automatically
- Send interpretations back to you

### Option 2: Manual Components

```python
from dream_analyst import DreamAnalyst
from fitbit_integration import FitbitIntegration
from messenger_dream_bot import MessengerDreamBot

# Initialize components separately
analyst = DreamAnalyst()
fitbit = FitbitIntegration(ACCESS_TOKEN, USER_ID)
messenger = MessengerDreamBot("Dream Journal")

# Use individually as needed
```

---

## 📱 Daily Usage

### Morning Routine

1. **Wake up naturally** (Fitbit detects)
2. **Check Messenger** on phone or glasses
3. **See prompt:** "Good morning! Did you have any dreams?"
4. **Dictate dream** via voice (or type)
5. **Receive analysis** within seconds

### Example Interaction

**Bot:** 
> Good morning! ☀️
> 
> 🌙 **Dream Journal Time** 🌙
> 
> You had excellent sleep (quality: 85/100)! You got 95 minutes of REM sleep - great for dreaming!
> 
> **Did you have any dreams?**
> 
> If yes, please dictate your dream now...

**You (via voice):**
> "I was in a dark forest and there was a snake following me. I felt really anxious. Then I found a bridge over water and when I crossed it I felt peaceful. There was an old man on the other side who smiled at me."

**Bot:**
> 🌟 Thank you! I'm analyzing your dream now...
> 
> 🔮 **Dream Analysis Complete** 🔮
> 
> **🌟 Jungian Interpretation**
> Forest represents the unconscious mind. Snake symbolizes transformation and healing (Shadow archetype). Bridge represents transition between states. Old man is the Wise Old Man archetype offering guidance.
> 
> **🧠 Freudian Interpretation**
> Anxiety suggests repressed content. Snake may represent sexual energy or fear. Water symbolizes the unconscious. The dream uses displacement to transfer anxiety onto symbols.
> 
> **💡 Integrated Insights**
> Both frameworks reveal a journey from fear to acceptance. You're processing anxiety about change while seeking wisdom and guidance.
> 
> **📋 Recommendations:**
> • Explore what changes you're resisting in waking life
> • Practice shadow integration work
> • Seek guidance from mentors or trusted advisors
> 
> Confidence: 85%
> 
> Sweet dreams tonight! 🌙✨

---

## 📊 Analytics & Reports

### Daily Stats
```python
# Get today's sleep and dream data
sleep = system.fitbit.get_latest_sleep()
dreams = system.dream_analyst.dreams

print(f"Sleep quality: {sleep.sleep_quality}/100")
print(f"Dreams recorded: {len(dreams)}")
```

### Weekly Summary
```python
# Automatically sent every Sunday
await system.send_weekly_summary()

# Or get manually
stats = system.get_dream_statistics(days=7)
```

### Pattern Analysis
```python
# Analyze recurring patterns
report = system.dream_analyst.get_dream_report(days=30)

print(f"Most common themes: {report['most_common_themes']}")
print(f"Most common symbols: {report['most_common_symbols']}")
print(f"Recommendations: {report['recommendations']}")
```

### Sleep-Dream Correlation
```python
# See how sleep quality affects dreams
correlation = system.get_dream_statistics(30)['correlation']

print(f"High quality sleep dreams: {correlation['high_quality_sleep']}")
print(f"Low quality sleep dreams: {correlation['low_quality_sleep']}")
```

---

## 🔧 Configuration

### Customize Prompts

```python
# Modify prompt templates
messenger.get_prompt_templates()['morning_prompt'] = "Your custom prompt..."
```

### Adjust Wake Detection

```python
# Change monitoring frequency (default: 5 minutes)
await fitbit.start_monitoring(check_interval_minutes=10)
```

### Symbol Dictionaries

```python
# Add personal symbol associations
analyst.personal_symbol_associations['car'] = "Freedom and independence"

# Add custom Jungian symbols
analyst.jungian_symbols['dragon'] = {
    'jungian': 'Primal power, transformation',
    'archetype': JungianArchetype.SHADOW
}
```

### Analysis Framework

```python
# Choose analysis framework
analysis = analyst.analyze_dream(
    dream_id="dream_123",
    framework=AnalysisFramework.JUNGIAN  # or FREUDIAN or COMBINED
)
```

---

## 🎯 Advanced Features

### Recurring Dream Detection

System automatically detects recurring dreams and prompts deeper exploration:

```python
# Check for patterns
patterns = analyst.analyze_dream_patterns(days=90)

for pattern in patterns:
    print(f"{pattern.element} appears {pattern.occurrences} times")
    print(f"Significance: {pattern.psychological_significance}")
```

### Lucid Dream Training

When lucid dreams are detected, system provides encouragement and tips:

```python
if dream.dream_type == DreamType.LUCID:
    # Special response with lucid dreaming tips
    messenger.send_message(
        messenger.get_prompt_templates()['lucid_dream_congratulations']
    )
```

### Nightmare Support

System detects nightmares and offers coping strategies:

```python
if dream.dream_type == DreamType.TRAUMATIC:
    # Send support message
    messenger.send_message(
        messenger.get_prompt_templates()['nightmare_support']
    )
```

---

## 🔒 Privacy & Security

### Data Storage
- All dream data stored locally
- No cloud storage by default
- Fitbit data accessed via OAuth (revocable)
- Messenger uses end-to-end encryption

### Recommendations
1. Use alternative Facebook account for bot
2. Keep Fitbit tokens secure (use environment variables)
3. Regularly review and delete old dreams
4. Don't share sensitive dream content

### Environment Variables
```bash
# .env file
FITBIT_ACCESS_TOKEN=your_token_here
FITBIT_USER_ID=your_user_id
FITBIT_CLIENT_ID=your_client_id
FITBIT_CLIENT_SECRET=your_client_secret
MESSENGER_CHAT_NAME=Dream Journal
```

---

## 🐛 Troubleshooting

### Fitbit Not Detecting Wake-Up

**Problem:** No prompt received after waking up

**Solutions:**
1. Check Fitbit sync (open Fitbit app)
2. Verify OAuth token is valid
3. Check monitoring is running: `system.fitbit.monitoring == True`
4. Reduce check interval: `check_interval_minutes=2`

### Messenger Not Receiving Messages

**Problem:** Prompt not appearing in Messenger

**Solutions:**
1. Verify meta-glasses-api extension is running
2. Check chat name matches exactly: "Dream Journal"
3. Ensure monitoring is active in extension
4. Check browser console for errors

### Poor Dream Analysis

**Problem:** Analysis seems inaccurate or generic

**Solutions:**
1. Provide more detail in dream description
2. Include emotions, symbols, and settings
3. Add personal symbol associations
4. Record dreams immediately upon waking (better recall)

### Low Confidence Scores

**Problem:** Analysis confidence < 50%

**Causes:**
- Brief dream description
- Few symbols identified
- Vague emotional tone
- Generic themes

**Solutions:**
- Describe dreams in more detail
- Mention specific objects, people, places
- Express how you felt during dream
- Note any unusual or vivid elements

---

## 📚 Understanding Your Analysis

### Jungian Framework

**Key Concepts:**
- **Archetypes:** Universal symbols from collective unconscious
- **Shadow:** Repressed aspects of personality
- **Individuation:** Process of becoming whole
- **Compensation:** Dreams balance conscious attitudes

**Common Archetypes:**
- Self: Wholeness, integration
- Shadow: Hidden aspects, fears
- Anima/Animus: Feminine/masculine within
- Wise Old Man: Guidance, wisdom
- Great Mother: Nurturing, origin

### Freudian Framework

**Key Concepts:**
- **Manifest Content:** Surface story of dream
- **Latent Content:** Hidden meaning
- **Wish Fulfillment:** Unconscious desires
- **Dream Work:** How mind disguises wishes

**Defense Mechanisms:**
- Displacement: Emotion transferred to substitute
- Condensation: Multiple ideas compressed
- Symbolization: Abstract made concrete
- Repression: Unacceptable thoughts hidden

### Synthesis

The system combines both frameworks to provide:
- Personal unconscious insights (Freud)
- Collective unconscious patterns (Jung)
- Actionable recommendations
- Pattern recognition over time

---

## 🎓 Tips for Better Dream Recall

1. **Set Intention:** Before sleep, say "I will remember my dreams"
2. **Don't Move:** Stay still when waking up
3. **Record Immediately:** Use voice dictation right away
4. **Keep Journal:** Even fragments are valuable
5. **Consistent Sleep:** Regular schedule improves recall
6. **Avoid Alcohol:** Reduces REM sleep and dream recall
7. **Practice:** Recall improves with consistent journaling

---

## 📈 Expected Results

### Week 1-2
- Learning to remember dreams
- 2-3 dreams recorded per week
- Basic symbol identification
- Getting comfortable with system

### Week 3-4
- Improved dream recall
- 4-5 dreams per week
- Recognizing personal symbols
- Noticing emotional patterns

### Month 2-3
- Strong dream recall
- 5-7 dreams per week
- Recurring patterns identified
- Deeper self-understanding

### Month 3+
- Excellent recall (even multiple dreams per night)
- Rich symbolic vocabulary
- Clear psychological patterns
- Potential lucid dreaming
- Significant personal insights

---

## 🤝 Support

For issues or questions:
1. Check troubleshooting section above
2. Review meta-glasses-api documentation
3. Verify Fitbit API status
4. Check Python dependencies

---

## 📄 License

Part of the Singularis project.

---

**Sweet dreams and happy analyzing! 🌙✨**
