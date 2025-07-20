import React, { useState } from 'react';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  const [command, setCommand] = useState('');

  const handleCommandSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Command submitted:', command);
    // Command processing will be implemented in future versions
    setCommand('');
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">Data Management</h1>
      </div>
      
      <div className="sidebar-content">
        <form onSubmit={handleCommandSubmit} className="command-form">
          <div className="command-input-container">
            <input
              type="text"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              placeholder="Ask me anything about your data..."
              className="command-input"
            />
            <button type="submit" className="command-submit">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
              </svg>
            </button>
          </div>
        </form>
        
        <div className="sidebar-help">
          <h3>Quick Commands</h3>
          <ul className="command-suggestions">
            <li>"Connect to Google Drive"</li>
            <li>"Show recent datasets"</li>
            <li>"Create new pipeline"</li>
            <li>"Analyze data trends"</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Sidebar; 