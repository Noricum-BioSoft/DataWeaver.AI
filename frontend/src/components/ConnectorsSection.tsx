import React, { useState, useEffect } from 'react';
import { connectorApi } from '../services/api';
import { Connector, ConnectorType, ConnectorStatus, ConnectorCreate } from '../types';
import ConnectorCard from './ConnectorCard';
import ConnectorSetupModal from './ConnectorSetupModal';
import './ConnectorsSection.css';

const ConnectorsSection: React.FC = () => {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSetupModal, setShowSetupModal] = useState(false);
  const [selectedConnectorType, setSelectedConnectorType] = useState<ConnectorType | null>(null);

  // Load connectors on component mount
  useEffect(() => {
    loadConnectors();
  }, []);

  const loadConnectors = async () => {
    try {
      setLoading(true);
      const data = await connectorApi.getConnectors();
      setConnectors(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load connectors:', err);
      setError('Failed to load connectors. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConnector = async (connectorData: ConnectorCreate) => {
    try {
      const newConnector = await connectorApi.createConnector(connectorData);
      setConnectors(prev => [...prev, newConnector]);
      setShowSetupModal(false);
      setSelectedConnectorType(null);
    } catch (err) {
      console.error('Failed to create connector:', err);
      throw err;
    }
  };

  const handleTestConnection = async (connectorId: number) => {
    try {
      const result = await connectorApi.testConnection(connectorId);
      if (result.success) {
        // Update connector status to connected
        setConnectors(prev => prev.map(conn => 
          conn.id === connectorId 
            ? { ...conn, status: ConnectorStatus.CONNECTED }
            : conn
        ));
      }
      return result;
    } catch (err) {
      console.error('Failed to test connection:', err);
      throw err;
    }
  };

  const handleSyncData = async (connectorId: number) => {
    try {
      const result = await connectorApi.syncDataSources(connectorId);
      if (result.success) {
        // Update connector status
        setConnectors(prev => prev.map(conn => 
          conn.id === connectorId 
            ? { ...conn, status: ConnectorStatus.CONNECTED }
            : conn
        ));
      }
      return result;
    } catch (err) {
      console.error('Failed to sync data:', err);
      throw err;
    }
  };

  const handleDeleteConnector = async (connectorId: number) => {
    try {
      await connectorApi.deleteConnector(connectorId);
      setConnectors(prev => prev.filter(conn => conn.id !== connectorId));
    } catch (err) {
      console.error('Failed to delete connector:', err);
      throw err;
    }
  };

  const openSetupModal = (connectorType: ConnectorType) => {
    setSelectedConnectorType(connectorType);
    setShowSetupModal(true);
  };

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

  const getLastSynced = (connector: Connector): string => {
    // For now, return a placeholder. In a real implementation,
    // this would come from the connector's sync logs
    return 'Never';
  };

  if (loading) {
    return (
      <div className="section">
        <div className="section-header">
          <h2>🔹 Connectors</h2>
        </div>
        <div className="section-content">
          <div className="loading">Loading connectors...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="section">
      <div className="section-header">
        <h2>🔹 Connectors</h2>
        <div className="connector-actions">
          <button 
            className="btn btn-primary"
            onClick={() => openSetupModal(ConnectorType.GOOGLE_WORKSPACE)}
          >
            + Add Google Drive
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => openSetupModal(ConnectorType.EMAIL)}
          >
            + Add Email
          </button>
        </div>
      </div>
      
      <div className="section-content">
        {error && (
          <div className="error-message">
            {error}
            <button onClick={loadConnectors}>Retry</button>
          </div>
        )}
        
        <div className="connectors-grid">
          {connectors.map(connector => (
            <ConnectorCard
              key={connector.id}
              connector={connector}
              icon={getConnectorIcon(connector.connector_type)}
              name={getConnectorDisplayName(connector.connector_type)}
              status={connector.status}
              lastSynced={getLastSynced(connector)}
              isConnected={connector.status === ConnectorStatus.CONNECTED}
              onTestConnection={() => handleTestConnection(connector.id)}
              onSyncData={() => handleSyncData(connector.id)}
              onDelete={() => handleDeleteConnector(connector.id)}
            />
          ))}
        </div>
        
        {connectors.length === 0 && (
          <div className="empty-state">
            <p>No connectors configured yet.</p>
            <p>Add your first connector to start integrating data sources.</p>
          </div>
        )}
        
        <div className="integration-note">
          <p>💡 <strong>Supported Connectors:</strong> Google Drive, Email, Slack, Microsoft 365, LIMS, and more. Each connector supports secure authentication and data synchronization.</p>
        </div>
      </div>

      {showSetupModal && selectedConnectorType && (
        <ConnectorSetupModal
          connectorType={selectedConnectorType}
          onClose={() => {
            setShowSetupModal(false);
            setSelectedConnectorType(null);
          }}
          onSubmit={handleCreateConnector}
        />
      )}
    </div>
  );
};

export default ConnectorsSection; 