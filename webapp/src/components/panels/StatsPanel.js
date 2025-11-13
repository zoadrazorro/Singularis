import React from 'react';
import './StatsPanel.css';

function StatsPanel({ data }) {
  const stats = data.stats || {};
  const cycle = data.cycle || 0;
  const uptime = data.uptime || 0;
  
  const successRate = stats.success_rate || 0;
  const llmActions = stats.llm_actions || 0;
  const rlActions = stats.rl_actions || 0;
  const heuristicActions = stats.heuristic_actions || 0;
  const totalActions = stats.total_actions || 0;
  
  return (
    <div className="stats-panel">
      <h2>📊 Session Statistics</h2>
      
      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-value">{cycle}</div>
          <div className="stat-label">Cycles</div>
        </div>
        
        <div className="stat-card primary">
          <div className="stat-value">{formatUptime(uptime)}</div>
          <div className="stat-label">Uptime</div>
        </div>
        
        <div className="stat-card success">
          <div className="stat-value">{(successRate * 100).toFixed(1)}%</div>
          <div className="stat-label">Success Rate</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{totalActions}</div>
          <div className="stat-label">Total Actions</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{llmActions}</div>
          <div className="stat-label">LLM Actions</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{rlActions}</div>
          <div className="stat-label">RL Actions</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{heuristicActions}</div>
          <div className="stat-label">Heuristic Actions</div>
        </div>
      </div>
    </div>
  );
}

function formatUptime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
}

export default StatsPanel;
