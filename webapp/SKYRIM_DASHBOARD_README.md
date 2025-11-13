# Skyrim AGI Real-Time Dashboard

Comprehensive real-time monitoring dashboard for tracking the Skyrim AGI's in-game status, consciousness metrics, performance, and decision-making across all subsystems.

## 🎮 Features

### Dual Mode Dashboard
- **Learning Monitor Mode**: Track philosophical text learning progress with Spinoza's ETHICA
- **Skyrim AGI Mode**: Real-time monitoring of autonomous gameplay AI

### Skyrim AGI Dashboard Panels

#### 📊 Overview Tab
- **Current Status**: Health, scene type, combat status
- **Action Display**: Current and recent actions with sources
- **Consciousness Metrics**: Real-time coherence (𝒞) and phi (Φ) values
- **LLM System Status**: Cloud/local LLM activity and call counts
- **Performance Metrics**: Planning, execution, and FPS
- **Diversity Metrics**: Action variety and exploration patterns

#### 🧠 Consciousness Tab
- Real-time coherence and phi measurements
- Node activation visualization
- Consciousness trend analysis
- Historical consciousness graphs

#### ⚡ Performance Tab
- Planning time metrics
- Execution time tracking
- Vision processing duration
- FPS monitoring
- Performance history charts
- System health indicators

#### 🎬 Action Tab
- Current action display with source attribution
- Recent action timeline
- Action distribution visualization
- Diversity score and metrics
- Action source breakdown (MoE, Hybrid, RL, etc.)

#### 👁️ Vision Tab
- Current scene detection (outdoor/indoor/combat/dialogue)
- Object detection list
- Enemy and NPC detection alerts
- Character vitals (Health, Magicka, Stamina)
- Combat/Menu state indicators
- Location tracking

#### 🤖 LLM Tab
- Active LLM architecture mode (Hybrid/MoE/Parallel)
- Cloud vs Local LLM distribution
- Total API call count
- Active model list with icons
- Action source attribution (LLM vs RL vs Heuristic)

#### 🌍 World Model Tab
- Current strategy display
- Active goals list
- World beliefs and knowledge
- Causal model insights

#### 📊 Stats Tab
- Session cycle count
- Uptime tracking
- Success rate metrics
- Action type distribution
- Total actions executed

#### 📈 Timeline Tab
- Consciousness evolution over time
- Performance history graphs
- Event timeline with cycle markers
- Action history with timestamps

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd webapp
npm install
```

### 2. Start the Backend Server

```bash
npm run server
```

This starts:
- HTTP API server on `http://localhost:5000`
- WebSocket server on `ws://localhost:5001`

The server monitors two JSON files:
- `learning_progress.json` - For learning monitor mode
- `skyrim_agi_state.json` - For Skyrim AGI mode

### 3. Start the React Dashboard

In a new terminal:

```bash
npm start
```

This opens the dashboard at `http://localhost:3000`

### Or Run Both Together

```bash
npm run dev
```

### 4. Run Skyrim AGI

In the main project directory:

```bash
python run_skyrim_agi.py
```

The AGI will automatically stream its state to `skyrim_agi_state.json` which the dashboard monitors in real-time.

## 🔄 Dashboard Modes

### Switching Modes

Click the "🎮 Switch to Skyrim AGI" or "📚 Switch to Learning" button in the header to toggle between:

- **Learning Monitor**: Tracks philosophical text learning with metrics like coherentia and ethical rate
- **Skyrim AGI Dashboard**: Real-time gameplay monitoring with full subsystem visibility

The dashboard automatically reconnects to the appropriate WebSocket endpoint when switching modes.

## 📡 Data Flow

```
┌─────────────────────┐
│   Skyrim AGI        │
│   (Python)          │
└──────────┬──────────┘
           │ Writes JSON every cycle
           ↓
┌─────────────────────┐
│ skyrim_agi_state    │
│      .json          │
└──────────┬──────────┘
           │ File watch
           ↓
┌─────────────────────┐
│  Node.js Server     │ (Port 5001)
│  WebSocket          │
└──────────┬──────────┘
           │ Real-time stream (1s updates)
           ↓
┌─────────────────────┐
│  React Dashboard    │ (Port 3000)
│  Multi-panel UI     │
└─────────────────────┘
```

## 📊 State Data Structure

The `skyrim_agi_state.json` file contains:

```json
{
  "session_id": "skyrim_agi_20251113_031200_07217037",
  "cycle": 25,
  "uptime": 734.5,
  "last_update": "2025-11-13T03:24:14Z",
  
  "current_action": "explore",
  "last_action": "attack",
  "action_source": "hybrid",
  
  "perception": {
    "scene_type": "outdoor_wilderness",
    "objects_detected": ["tree", "rock", "path"],
    "enemies_nearby": false,
    "npcs_nearby": true
  },
  
  "game_state": {
    "health": 85,
    "magicka": 100,
    "stamina": 90,
    "in_combat": false,
    "in_menu": false,
    "location": "Whiterun Plains"
  },
  
  "consciousness": {
    "coherence": 0.42,
    "phi": 0.38,
    "nodes_active": 22,
    "trend": "stable",
    "history": [...]
  },
  
  "llm_status": {
    "mode": "hybrid",
    "cloud_active": 2,
    "local_active": 0,
    "total_calls": 150,
    "active_models": ["Gemini 2.0 Flash", "Claude Sonnet 4.5"]
  },
  
  "performance": {
    "fps": 60,
    "planning_time": 0.45,
    "execution_time": 0.12,
    "vision_time": 0.08,
    "history": [...]
  },
  
  "diversity": {
    "score": 0.65,
    "unique_actions": 8,
    "variety_rate": 0.72,
    "action_distribution": {
      "explore": 10,
      "attack": 5,
      "move_forward": 8
    }
  },
  
  "stats": {
    "success_rate": 0.92,
    "llm_actions": 18,
    "rl_actions": 5,
    "heuristic_actions": 2
  }
}
```

## 🎨 UI Features

### Real-Time Updates
- WebSocket connection with 1-second update frequency
- Automatic reconnection on disconnect
- Live connection status indicator

### Responsive Design
- Grid-based layout adapts to screen size
- Mobile-friendly panel layouts
- Optimized for 1080p and 4K displays

### Visual Feedback
- Animated pulse effects for active states
- Color-coded status indicators
- Gradient backgrounds for emphasis
- Smooth transitions and animations

### Performance Optimized
- Efficient React component updates
- Chart data limiting to prevent memory bloat
- Lazy rendering for inactive tabs

## 🛠️ Customization

### Update Frequency

Edit `server.js` to change update frequency:

```javascript
// Skyrim updates every 1s (line ~115)
}, isSkyrimMode ? 1000 : 2000);
```

### Panel Configuration

Modify `SkyrimDashboard.js` to add/remove tabs:

```javascript
const tabs = [
  { id: 'overview', label: '📊 Overview', icon: '📊' },
  { id: 'consciousness', label: '🧠 Consciousness', icon: '🧠' },
  // Add your custom tab here
];
```

### Styling

All panel styles are in separate CSS files:
- `SkyrimDashboard.css` - Main dashboard layout
- `PerformancePanel.css` - Performance metrics
- `ActionPanel.css` - Action visualization
- `VisionPanel.css` - Vision and perception
- `LLMPanel.css` - LLM system status
- And more...

## 📈 Monitoring Best Practices

1. **Pre-Session**: Start the dashboard before launching Skyrim AGI
2. **During Session**: Keep Overview tab visible for quick status checks
3. **Analysis**: Use Timeline tab to review consciousness trends
4. **Performance**: Monitor Performance tab for bottlenecks
5. **Debugging**: Check LLM tab for model selection issues

## 🐛 Troubleshooting

### Dashboard shows "Waiting for AGI data"
- Ensure Skyrim AGI is running: `python run_skyrim_agi.py`
- Check that `skyrim_agi_state.json` exists in project root
- Verify WebSocket server is running on port 5001

### Connection keeps dropping
- Check firewall settings for ports 5000 and 5001
- Ensure no other apps are using these ports
- Restart both server and dashboard

### Data not updating
- Verify Skyrim AGI dashboard streamer is enabled
- Check console for WebSocket errors
- Confirm `skyrim_agi_state.json` is being written to

### Performance issues
- Reduce chart history size in panel components
- Check browser memory usage (F12 → Performance)
- Consider disabling Timeline panel for long sessions

## 📝 Development

### Adding New Panels

1. Create panel component in `src/components/panels/`
2. Create corresponding CSS file
3. Import in `SkyrimDashboard.js`
4. Add tab to `tabs` array
5. Add case to tab switcher

### Extending State Data

1. Update `dashboard_streamer.py` to collect new data
2. Modify `skyrim_agi.py` to call `_update_dashboard_state()`
3. Update panel components to display new data

## 🔗 Related Documentation

- [SKYRIM_AGI_ARCHITECTURE.md](../SKYRIM_AGI_ARCHITECTURE.md) - System architecture
- [SKYRIM_AGI_ENHANCEMENTS.md](../SKYRIM_AGI_ENHANCEMENTS.md) - Feature details
- [SYSTEM_ARCHITECTURE_COMPLETE.md](../SYSTEM_ARCHITECTURE_COMPLETE.md) - Complete system overview

## 📄 License

Part of the Singularis AGI project. See LICENSE in project root.

---

**Built with**: React, Recharts, WebSockets, Node.js, Express

**Purpose**: Real-time monitoring and analysis of autonomous AGI gameplay in Skyrim

**Status**: ✅ Fully operational with 8 comprehensive monitoring panels
