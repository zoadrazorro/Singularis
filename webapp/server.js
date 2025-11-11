/**
 * WebSocket server for real-time learning progress monitoring
 */

const express = require('express');
const cors = require('cors');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 5000;
const WS_PORT = 5001;

// Path to learning progress file
const LEARNING_PROGRESS_PATH = path.join(__dirname, '..', 'learning_progress.json');

// Store current progress
let currentProgress = {
  currentChunk: 0,
  totalChunks: 240,
  chunksCompleted: 0,
  avgTime: 0,
  avgCoherentia: 0,
  ethicalRate: 0,
  recentChunks: [],
  coherentiaHistory: [],
  timeHistory: [],
  isRunning: false,
  lastUpdate: null,
};

// Parse learning progress from JSON file
function parseProgress() {
  try {
    if (!fs.existsSync(LEARNING_PROGRESS_PATH)) {
      return { ...currentProgress, isRunning: false };
    }

    const data = JSON.parse(fs.readFileSync(LEARNING_PROGRESS_PATH, 'utf-8'));
    
    const chunks = data.chunks || [];
    const totalChunks = data.total_chunks || 240;
    const chunksCompleted = data.chunks_completed || chunks.length;
    const avgTime = data.avg_time || 0;
    const avgCoherentia = data.avg_coherentia || 0;
    const ethicalRate = data.ethical_rate || 0;
    
    // Get recent chunks (last 10)
    const recentChunks = chunks.slice(-10);
    
    // Build history for charts
    const coherentiaHistory = chunks.map(c => ({ chunk: c.chunk, value: c.coherentia }));
    const timeHistory = chunks.map(c => ({ chunk: c.chunk, value: c.time }));
    
    return {
      currentChunk: chunksCompleted,
      totalChunks,
      chunksCompleted,
      avgTime,
      avgCoherentia,
      ethicalRate,
      recentChunks,
      coherentiaHistory,
      timeHistory,
      isRunning: chunksCompleted < totalChunks,
      lastUpdate: data.last_update || new Date().toISOString(),
    };
  } catch (error) {
    console.error('Error parsing progress:', error);
    return { ...currentProgress, isRunning: false };
  }
}

// REST API endpoints
app.get('/api/progress', (req, res) => {
  const progress = parseProgress();
  res.json(progress);
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start HTTP server
app.listen(PORT, () => {
  console.log(`HTTP server running on http://localhost:${PORT}`);
});

// WebSocket server for real-time updates
const wss = new WebSocket.Server({ 
  port: WS_PORT,
  perMessageDeflate: false,
  clientTracking: true
});

wss.on('connection', (ws) => {
  console.log('Client connected');
  
  // Send initial data
  try {
    const initialData = parseProgress();
    ws.send(JSON.stringify(initialData));
  } catch (error) {
    console.error('Error sending initial data:', error);
  }
  
  // Set up interval to send updates
  const interval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      try {
        const progress = parseProgress();
        ws.send(JSON.stringify(progress));
      } catch (error) {
        console.error('Error sending update:', error);
      }
    }
  }, 2000); // Update every 2 seconds
  
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
  
  ws.on('close', () => {
    console.log('Client disconnected');
    clearInterval(interval);
  });
  
  // Send ping to keep connection alive
  const pingInterval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.ping();
    }
  }, 30000);
  
  ws.on('close', () => {
    clearInterval(pingInterval);
  });
});

console.log(`WebSocket server running on ws://localhost:${WS_PORT}`);
console.log('Monitoring:', LEARNING_PROGRESS_PATH);
