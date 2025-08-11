import React from 'react';
import './ConnectorCard.css';

interface ConnectorCardProps {
  name: string;
  icon: string;
  status: string;
  lastSynced?: string;
  isConnected: boolean;
}

const ConnectorCard: React.FC<ConnectorCardProps> = ({
  name,
  icon,
  status,
  lastSynced,
  isConnected
}) => {
  const handleConnect = () => {
    console.log(`Connecting to ${name}...`);
    // TODO: Implement connector integration
  };

  return (
    <div className="connector-card">
      <div className="connector-header">
        <div className="connector-icon">{icon}</div>
        <div className="connector-info">
          <h3 className="connector-name">{name}</h3>
                  <div className="connector-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`} title={isConnected ? 'Connected and ready for data transfer' : 'Not connected - click to authenticate'}></span>
          <span className="status-text" title={`Current status: ${status}`}>{status}</span>
        </div>
        </div>
      </div>
      
      <div className="connector-details">
        {lastSynced && <p className="last-synced">Last synced: {lastSynced}</p>}
        <button
          className={`connect-button ${isConnected ? 'connected' : ''}`}
          onClick={handleConnect}
          title={isConnected ? 'Already connected - click to disconnect' : 'Click to connect and authenticate'}
        >
          {isConnected ? 'Connected' : 'Connect'}
        </button>
      </div>
    </div>
  );
};

export default ConnectorCard; 