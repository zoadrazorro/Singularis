# Singularis Learning Monitor

Real-time web dashboard for monitoring the Singularis consciousness learning process.

## Features

- **Real-time Updates** - WebSocket connection updates every 2 seconds
- **Progress Tracking** - Visual progress bar and chunk counter
- **Key Metrics** - Avg time, coherentia, ethical rate, time remaining
- **Interactive Charts** - Coherentia and processing time trends
- **Recent Chunks Table** - Last 10 chunks with full details
- **Beautiful UI** - Modern gradient design with glassmorphism

## Quick Start

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

### 3. Start the React App

In a new terminal:

```bash
npm start
```

This opens the dashboard at `http://localhost:3000`

### Or Run Both Together

```bash
npm run dev
```

## Architecture

```
┌─────────────────┐
│  React Frontend │ (Port 3000)
│   Dashboard UI  │
└────────┬────────┘
         │ WebSocket
         ↓
┌─────────────────┐
│  Node.js Server │ (Port 5001)
│   WebSocket     │
└────────┬────────┘
         │ File Read
         ↓
┌─────────────────┐
│ learning_output │
│     .txt        │
└─────────────────┘
```

## API Endpoints

### HTTP (Port 5000)

- `GET /api/progress` - Get current progress snapshot
- `GET /api/health` - Health check

### WebSocket (Port 5001)

- Connects and receives progress updates every 2 seconds
- Auto-reconnects on disconnect

## Progress Data Format

```json
{
  "currentChunk": 5,
  "totalChunks": 240,
  "chunksCompleted": 4,
  "avgTime": 62.3,
  "avgCoherentia": 0.530,
  "ethicalRate": 0.67,
  "recentChunks": [
    {
      "chunk": 4,
      "time": 65.2,
      "coherentia": 0.541,
      "consciousness": 0.441,
      "ethical": true
    }
  ],
  "coherentiaHistory": [...],
  "timeHistory": [...],
  "isRunning": true,
  "lastUpdate": "2025-11-11T05:00:00.000Z"
}
```

## Development

### File Structure

```
webapp/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Dashboard.js
│   │   └── Dashboard.css
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
├── server.js          # Backend WebSocket server
├── package.json
└── README.md
```

### Technologies

- **Frontend:** React 18, Recharts (charts)
- **Backend:** Express, WebSocket (ws)
- **Styling:** CSS with glassmorphism effects

## Troubleshooting

### Port Already in Use

If ports 3000, 5000, or 5001 are in use:

```bash
# Kill process on port
npx kill-port 3000
npx kill-port 5000
npx kill-port 5001
```

### WebSocket Not Connecting

1. Ensure backend server is running: `npm run server`
2. Check firewall settings
3. Verify `learning_output.txt` exists in parent directory

### No Data Showing

1. Ensure learning process is running
2. Check `learning_output.txt` has content
3. Verify file path in `server.js` is correct

## Customization

### Update Interval

Change WebSocket update frequency in `server.js`:

```javascript
const interval = setInterval(() => {
  // ...
}, 2000); // Change to desired milliseconds
```

### Chart History Length

Modify chart data slice in `Dashboard.js`:

```javascript
<LineChart data={coherentiaHistory.slice(-50)}>
// Change -50 to show more/fewer points
```

## Production Deployment

### Build for Production

```bash
npm run build
```

### Serve Static Build

```bash
npm install -g serve
serve -s build -p 3000
```

### Keep Server Running

Use PM2 or similar:

```bash
npm install -g pm2
pm2 start server.js --name singularis-monitor
pm2 save
pm2 startup
```

## License

MIT

## Credits

Built for the Singularis consciousness engine.

*"The more the mind understands, the greater its power."* — ETHICA UNIVERSALIS
