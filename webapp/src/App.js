import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import SkyrimDashboard from './components/SkyrimDashboard';

function App() {
  const [progress, setProgress] = useState(null);
  const [connected, setConnected] = useState(false);
  const [ws, setWs] = useState(null);
  const [mode, setMode] = useState('learning'); // 'learning' or 'skyrim'

  useEffect(() => {
    let reconnectTimeout;
    
    const connectWebSocket = () => {
      // Connect to WebSocket with mode parameter
      // Use current hostname to support both local and network access
      const hostname = window.location.hostname;
      const wsUrl = mode === 'skyrim' 
        ? `ws://${hostname}:5001?mode=skyrim`
        : `ws://${hostname}:5001`;
      
      console.log('Connecting to WebSocket:', wsUrl);
      const websocket = new WebSocket(wsUrl);
      
      websocket.onopen = () => {
        console.log('WebSocket connected');
        setConnected(true);
      };
      
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setProgress(data);
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      };
      
      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnected(false);
      };
      
      websocket.onclose = () => {
        console.log('WebSocket disconnected');
        setConnected(false);
        // Attempt to reconnect after 3 seconds
        reconnectTimeout = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connectWebSocket();
        }, 3000);
      };
      
      setWs(websocket);
      
      return websocket;
    };
    
    const websocket = connectWebSocket();
    
    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (websocket) {
        websocket.close();
      }
    };
  }, [mode]); // Re-connect when mode changes

  const toggleMode = () => {
    setMode(mode === 'learning' ? 'skyrim' : 'learning');
    setProgress(null); // Clear data when switching
    if (ws) {
      ws.close(); // Close existing connection
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🧠 Singularis {mode === 'skyrim' ? 'AGI Dashboard' : 'Learning Monitor'}</h1>
        <div className="header-controls">
          <button className="mode-toggle" onClick={toggleMode}>
            {mode === 'learning' ? '🎮 Switch to Skyrim AGI' : '📚 Switch to Learning'}
          </button>
          <div className="connection-status">
            <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`}></span>
            <span>{connected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
      </header>
      
      {progress ? (
        mode === 'skyrim' ? (
          <SkyrimDashboard data={progress} connected={connected} />
        ) : (
          <Dashboard progress={progress} />
        )
      ) : (
        <div className="loading">
          <div className="spinner"></div>
          <p>Connecting to {mode === 'skyrim' ? 'Skyrim AGI' : 'learning process'}...</p>
        </div>
      )}
      
      <footer className="App-footer">
        <p>From ETHICA: "The more the mind understands, the greater its power."</p>
      </footer>
    </div>
  );
}

export default App;
