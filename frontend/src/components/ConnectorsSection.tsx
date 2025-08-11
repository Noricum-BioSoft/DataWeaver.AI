import React from 'react';
import ConnectorCard from './ConnectorCard';
import './ConnectorsSection.css';

const ConnectorsSection: React.FC = () => {
  const connectors = [
    {
      id: 1,
      name: 'Google Drive',
      icon: '📁',
      status: 'Connected',
      lastSynced: '2 hours ago',
      isConnected: true
    },
    {
      id: 2,
      name: 'Amazon S3',
      icon: '☁️',
      status: 'Connected',
      lastSynced: '1 day ago',
      isConnected: true
    },
    {
      id: 3,
      name: 'FTP',
      icon: '📡',
      status: 'Connected',
      lastSynced: '3 hours ago',
      isConnected: true
    }
  ];

  return (
    <div className="section">
      <div className="section-header">
        <h2>🔹 Connectors</h2>
        <div className="simulation-badge" title="This data is simulated for demonstration purposes. Real integrations need to be implemented for production use.">🧪 Simulation Data</div>
      </div>
      <div className="section-content">
        <div className="connectors-grid">
          {connectors.map(connector => (
            <ConnectorCard
              key={connector.id}
              name={connector.name}
              icon={connector.icon}
              status={connector.status}
              lastSynced={connector.lastSynced}
              isConnected={connector.isConnected}
            />
          ))}
        </div>
        <div className="integration-note" title="Click to learn more about implementing real integrations">
          <p>💡 <strong>Production Integration Required:</strong> This demo shows simulated data. For production use, implement custom integrations with your actual data sources and APIs.</p>
        </div>
      </div>
    </div>
  );
};

export default ConnectorsSection; 