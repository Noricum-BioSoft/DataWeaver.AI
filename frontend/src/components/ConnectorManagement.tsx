import React, { useState, useEffect } from 'react';
import { connectorApi } from '../services/api';
import { Connector, ConnectorType, ConnectorStatus, ConnectorCreate, ConnectorUpdate } from '../types';
import ConnectorSetupModal from './ConnectorSetupModal';
import ConnectorTestModal from './ConnectorTestModal';
import ConnectorDetailsModal from './ConnectorDetailsModal';
import './ConnectorManagement.css';

interface ConnectorManagementProps {
  onConnectorUpdate?: (connector: Connector) => void;
}

const ConnectorManagement: React.FC<ConnectorManagementProps> = ({ onConnectorUpdate }) => {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSetupModal, setShowSetupModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedConnector, setSelectedConnector] = useState<Connector | null>(null);
  const [selectedConnectorType, setSelectedConnectorType] = useState<ConnectorType | null>(null);
  const [filterStatus, setFilterStatus] = useState<ConnectorStatus | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');

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
      
      if (onConnectorUpdate) {
        onConnectorUpdate(newConnector);
      }
    } catch (err) {
      console.error('Failed to create connector:', err);
      throw err;
    }
  };

  const handleUpdateConnector = async (connectorId: number, updates: ConnectorUpdate) => {
    try {
      const updatedConnector = await connectorApi.updateConnector(connectorId, updates);
      setConnectors(prev => prev.map(conn => 
        conn.id === connectorId ? updatedConnector : conn
      ));
      
      if (onConnectorUpdate) {
        onConnectorUpdate(updatedConnector);
      }
    } catch (err) {
      console.error('Failed to update connector:', err);
      throw err;
    }
  };

  const handleDeleteConnector = async (connectorId: number) => {
    if (!window.confirm('Are you sure you want to delete this connector? This action cannot be undone.')) {
      return;
    }

    try {
      await connectorApi.deleteConnector(connectorId);
      setConnectors(prev => prev.filter(conn => conn.id !== connectorId));
    } catch (err) {
      console.error('Failed to delete connector:', err);
      throw err;
    }
  };

  const handleTestConnection = async (connectorId: number) => {
    try {
      const result = await connectorApi.testConnection(connectorId);
      return result;
    } catch (err) {
      console.error('Failed to test connection:', err);
      throw err;
    }
  };

  const handleSyncData = async (connectorId: number) => {
    try {
      const result = await connectorApi.syncDataSources(connectorId);
      return result;
    } catch (err) {
      console.error('Failed to sync data:', err);
      throw err;
    }
  };

  const openSetupModal = (connectorType: ConnectorType) => {
    setSelectedConnectorType(connectorType);
    setShowSetupModal(true);
  };

  const openTestModal = (connector: Connector) => {
    setSelectedConnector(connector);
    setShowTestModal(true);
  };

  const openDetailsModal = (connector: Connector) => {
    setSelectedConnector(connector);
    setShowDetailsModal(true);
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

  const getStatusColor = (status: ConnectorStatus): string => {
    switch (status) {
      case ConnectorStatus.CONNECTED:
        return 'success';
      case ConnectorStatus.CONNECTING:
      case ConnectorStatus.SYNCING:
        return 'warning';
      case ConnectorStatus.ERROR:
        return 'error';
      default:
        return 'neutral';
    }
  };

  const filteredConnectors = connectors.filter(connector => {
    const matchesStatus = filterStatus === 'all' || connector.status === filterStatus;
    const matchesSearch = connector.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         connector.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         connector.connector_type.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  if (loading) {
    return (
      <div className="connector-management">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading connectors...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="connector-management">
      {/* Header */}
      <div className="connector-header">
        <div className="header-content">
          <h1>🔌 Connector Management</h1>
          <p>Configure and manage your data source connectors</p>
        </div>
        <div className="header-actions">
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
          <button 
            className="btn btn-secondary"
            onClick={loadConnectors}
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="connector-filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search connectors..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="status-filter">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as ConnectorStatus | 'all')}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value={ConnectorStatus.CONNECTED}>Connected</option>
            <option value={ConnectorStatus.CONNECTING}>Connecting</option>
            <option value={ConnectorStatus.DISCONNECTED}>Disconnected</option>
            <option value={ConnectorStatus.ERROR}>Error</option>
            <option value={ConnectorStatus.SYNCING}>Syncing</option>
          </select>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          {error}
          <button onClick={loadConnectors}>Retry</button>
        </div>
      )}

      {/* Connectors Grid */}
      <div className="connectors-container">
        {filteredConnectors.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔌</div>
            <h3>No connectors found</h3>
            <p>
              {searchTerm || filterStatus !== 'all' 
                ? 'Try adjusting your search or filter criteria.'
                : 'Get started by adding your first connector to integrate with external data sources.'
              }
            </p>
            <div className="empty-actions">
              <button 
                className="btn btn-primary"
                onClick={() => openSetupModal(ConnectorType.GOOGLE_WORKSPACE)}
              >
                Add Google Drive Connector
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => openSetupModal(ConnectorType.EMAIL)}
              >
                Add Email Connector
              </button>
            </div>
          </div>
        ) : (
          <div className="connectors-grid">
            {filteredConnectors.map(connector => (
              <div key={connector.id} className="connector-card">
                <div className="connector-card-header">
                  <div className="connector-icon">
                    {getConnectorIcon(connector.connector_type)}
                  </div>
                  <div className="connector-info">
                    <h3 className="connector-name">{connector.name}</h3>
                    <p className="connector-type">{getConnectorDisplayName(connector.connector_type)}</p>
                    {connector.description && (
                      <p className="connector-description">{connector.description}</p>
                    )}
                  </div>
                  <div className={`status-badge status-${getStatusColor(connector.status)}`}>
                    {connector.status}
                  </div>
                </div>

                <div className="connector-card-body">
                  <div className="connector-meta">
                    <span className="meta-item">
                      <strong>Auth:</strong> {connector.auth_type}
                    </span>
                    <span className="meta-item">
                      <strong>Created:</strong> {new Date(connector.created_at).toLocaleDateString()}
                    </span>
                    {connector.updated_at && (
                      <span className="meta-item">
                        <strong>Updated:</strong> {new Date(connector.updated_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>

                <div className="connector-card-actions">
                  <button
                    className="btn btn-sm btn-secondary"
                    onClick={() => openDetailsModal(connector)}
                    title="View Details"
                  >
                    Details
                  </button>
                  <button
                    className="btn btn-sm btn-primary"
                    onClick={() => openTestModal(connector)}
                    title="Test Connection"
                  >
                    Test
                  </button>
                  <button
                    className="btn btn-sm btn-success"
                    onClick={() => handleSyncData(connector.id)}
                    title="Sync Data"
                    disabled={connector.status !== ConnectorStatus.CONNECTED}
                  >
                    Sync
                  </button>
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={() => handleDeleteConnector(connector.id)}
                    title="Delete Connector"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
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

      {showTestModal && selectedConnector && (
        <ConnectorTestModal
          connector={selectedConnector}
          onClose={() => {
            setShowTestModal(false);
            setSelectedConnector(null);
          }}
          onTest={handleTestConnection}
          onSync={handleSyncData}
          onRefresh={loadConnectors}
        />
      )}

      {showDetailsModal && selectedConnector && (
        <ConnectorDetailsModal
          connector={selectedConnector}
          onClose={() => {
            setShowDetailsModal(false);
            setSelectedConnector(null);
          }}
          onUpdate={handleUpdateConnector}
          onDelete={handleDeleteConnector}
        />
      )}
    </div>
  );
};

export default ConnectorManagement;
