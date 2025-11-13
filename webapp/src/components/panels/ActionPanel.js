import React from 'react';
import './ActionPanel.css';

/**
 * Action history and planning panel
 */
function ActionPanel({ data }) {
  const currentAction = data.current_action || 'idle';
  const recentActions = data.recent_actions || [];
  const actionSource = data.action_source || 'unknown';
  const diversity = data.diversity || {};
  
  // Get action distribution
  const actionDist = diversity.action_distribution || {};
  const totalActions = diversity.total_actions || 0;
  
  return (
    <div className="action-panel">
      <h2>🎬 Action System</h2>
      
      <div className="current-action-display">
        <div className="action-header">Current Action</div>
        <div className="action-name-large">{formatAction(currentAction)}</div>
        <div className="action-meta">
          <span className="meta-label">Source:</span>
          <span className={`meta-value source-${actionSource.toLowerCase()}`}>
            {formatSource(actionSource)}
          </span>
        </div>
      </div>
      
      <div className="action-sections">
        <div className="recent-actions-section">
          <h3>Recent Actions</h3>
          <div className="action-timeline">
            {recentActions.slice(-10).reverse().map((action, idx) => (
              <div key={idx} className="timeline-item">
                <div className="timeline-dot"></div>
                <div className="timeline-content">
                  <span className="timeline-action">{formatAction(action.name)}</span>
                  <span className="timeline-source">{formatSource(action.source)}</span>
                  <span className="timeline-time">{formatTime(action.timestamp)}</span>
                </div>
              </div>
            ))}
            {recentActions.length === 0 && (
              <div className="no-data">No actions yet</div>
            )}
          </div>
        </div>
        
        <div className="action-distribution-section">
          <h3>Action Distribution</h3>
          <div className="distribution-bars">
            {Object.entries(actionDist).map(([action, count]) => {
              const percentage = totalActions > 0 ? (count / totalActions) * 100 : 0;
              return (
                <div key={action} className="dist-bar-item">
                  <div className="dist-label">
                    <span className="dist-action">{formatAction(action)}</span>
                    <span className="dist-count">{count}</span>
                  </div>
                  <div className="dist-bar">
                    <div 
                      className="dist-fill"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className="dist-percent">{percentage.toFixed(1)}%</div>
                </div>
              );
            })}
            {Object.keys(actionDist).length === 0 && (
              <div className="no-data">No distribution data</div>
            )}
          </div>
        </div>
      </div>
      
      <div className="diversity-metrics">
        <h3>Diversity Metrics</h3>
        <div className="diversity-grid">
          <div className="diversity-card">
            <div className="diversity-value">{(diversity.score * 100 || 0).toFixed(1)}%</div>
            <div className="diversity-label">Diversity Score</div>
          </div>
          <div className="diversity-card">
            <div className="diversity-value">{diversity.unique_actions || 0}</div>
            <div className="diversity-label">Unique Actions</div>
          </div>
          <div className="diversity-card">
            <div className="diversity-value">{(diversity.variety_rate * 100 || 0).toFixed(1)}%</div>
            <div className="diversity-label">Variety Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function formatAction(action) {
  return action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatSource(source) {
  if (source === 'moe') return 'MoE';
  if (source === 'hybrid') return 'Hybrid';
  if (source === 'phi4') return 'Phi-4';
  if (source === 'local_moe') return 'Local MoE';
  return source.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatTime(timestamp) {
  if (!timestamp) return '';
  const date = new Date(timestamp * 1000);
  return date.toLocaleTimeString();
}

export default ActionPanel;
