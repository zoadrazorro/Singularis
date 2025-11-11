import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';

function App() {
  const [progress, setProgress] = useState(null);
  const [connected, setConnected] = useState(false);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    let reconnectTimeout;
    
    const connectWebSocket = () => {
      // Connect to WebSocket
      const websocket = new WebSocket('ws://localhost:5001');
      
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
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🧠 Singularis Learning Monitor</h1>
        <div className="connection-status">
          <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`}></span>
          <span>{connected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </header>
      
      {progress ? (
        <Dashboard progress={progress} />
      ) : (
        <div className="loading">
          <div className="spinner"></div>
          <p>Connecting to learning process...</p>
        </div>
      )}
      
      <footer className="App-footer">
        <p>From ETHICA: "The more the mind understands, the greater its power."</p>
      </footer>
    </div>
  );
}

export default App;
