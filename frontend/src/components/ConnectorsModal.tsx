import React from 'react';
import ConnectorCard from './ConnectorCard';
import './ConnectorsModal.css';

interface ConnectorsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ConnectorsModal: React.FC<ConnectorsModalProps> = ({ isOpen, onClose }) => {
  const connectors = [
    {
      id: 1,
      name: 'Google Drive',
      icon: '📁',
      status: 'Connected',
      isConnected: true
    },
    {
      id: 2,
      name: 'Amazon S3',
      icon: '☁️',
      status: 'Connected',
      isConnected: true
    },
    {
      id: 3,
      name: 'FTP',
      icon: '📡',
      status: 'Connected',
      isConnected: true
    }
  ];

  if (!isOpen) return null;

  return (
    <div className="connectors-modal-overlay" onClick={onClose}>
      <div className="connectors-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🔹 Connectors</h2>
          <div className="simulation-badge">🧪 Simulation Data</div>
          <button className="modal-close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div className="modal-content">
          <div className="connectors-grid">
            {connectors.map(connector => (
              <ConnectorCard
                key={connector.id}
                name={connector.name}
                icon={connector.icon}
                status={connector.status}
                isConnected={connector.isConnected}
              />
            ))}
          </div>
          <div className="integration-note">
            <p>💡 <strong>Production Integration Required:</strong> This demo shows simulated data. For production use, implement custom integrations with your actual data sources and APIs.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConnectorsModal;
