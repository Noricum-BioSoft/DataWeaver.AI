import React from 'react';
import { Connector, ConnectorType, ConnectorStatus } from '../types';
import ConnectorCard from './ConnectorCard';
import './ConnectorsModal.css';

interface ConnectorsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ConnectorsModal: React.FC<ConnectorsModalProps> = ({ isOpen, onClose }) => {
  // Mock connectors for demonstration
  const connectors: Connector[] = [
    {
      id: 1,
      name: 'Google Drive Connector',
      description: 'Access to Google Drive files and folders',
      connector_type: ConnectorType.GOOGLE_WORKSPACE,
      auth_type: 'OAUTH2' as any,
      status: ConnectorStatus.CONNECTED,
      config: {
        client_id: 'mock-client-id',
        scopes: ['https://www.googleapis.com/auth/drive.readonly']
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 2,
      name: 'Email Connector',
      description: 'Email integration for data extraction',
      connector_type: ConnectorType.EMAIL,
      auth_type: 'USERNAME_PASSWORD' as any,
      status: ConnectorStatus.CONNECTED,
      config: {
        server: 'smtp.gmail.com',
        port: 587,
        use_ssl: true
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 3,
      name: 'Slack Connector',
      description: 'Slack workspace integration',
      connector_type: ConnectorType.SLACK,
      auth_type: 'TOKEN' as any,
      status: ConnectorStatus.CONNECTED,
      config: {
        bot_token: 'mock-bot-token'
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ];

  const getConnectorIcon = (connectorType: ConnectorType): string => {
    switch (connectorType) {
      case ConnectorType.GOOGLE_WORKSPACE:
        return '📁';
      case ConnectorType.EMAIL:
        return '📧';
      case ConnectorType.SLACK:
        return '💬';
      case ConnectorType.MICROSOFT_365:
        return '📄';
      case ConnectorType.LIMS:
        return '🧪';
      default:
        return '🔌';
    }
  };

  const getConnectorDisplayName = (connectorType: ConnectorType): string => {
    switch (connectorType) {
      case ConnectorType.GOOGLE_WORKSPACE:
        return 'Google Drive';
      case ConnectorType.EMAIL:
        return 'Email';
      case ConnectorType.SLACK:
        return 'Slack';
      case ConnectorType.MICROSOFT_365:
        return 'Microsoft 365';
      case ConnectorType.LIMS:
        return 'LIMS';
      default:
        return connectorType;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="connectors-modal-overlay" onClick={onClose}>
      <div className="connectors-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🔹 Connectors</h2>
          <div className="simulation-badge" title="This data is simulated for demonstration purposes. Real integrations need to be implemented for production use.">🧪 Simulation Data</div>
          <button className="modal-close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div className="modal-content">
          <div className="connectors-grid">
            {connectors.map(connector => (
              <div key={connector.id} title={`${getConnectorDisplayName(connector.connector_type)}: ${connector.status} - ${connector.status === ConnectorStatus.CONNECTED ? 'Connected and ready for data transfer' : 'Not connected - requires authentication'}`}>
                <ConnectorCard
                  connector={connector}
                  icon={getConnectorIcon(connector.connector_type)}
                  name={getConnectorDisplayName(connector.connector_type)}
                  status={connector.status}
                  lastSynced="Never"
                  isConnected={connector.status === ConnectorStatus.CONNECTED}
                />
              </div>
            ))}
          </div>
          <div className="integration-note" title="Click to learn more about implementing real integrations">
            <p>💡 <strong>Production Integration Required:</strong> This demo shows simulated data. For production use, implement custom integrations with your actual data sources and APIs.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConnectorsModal;
