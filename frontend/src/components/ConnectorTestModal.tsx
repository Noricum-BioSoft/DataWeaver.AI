import React, { useState } from 'react';
import { Connector, ConnectorTestResult, SyncResult } from '../types';
import './ConnectorTestModal.css';

interface ConnectorTestModalProps {
  connector: Connector;
  onClose: () => void;
  onTest: (connectorId: number) => Promise<ConnectorTestResult>;
  onSync: (connectorId: number) => Promise<SyncResult>;
  onRefresh?: () => void;
}

const ConnectorTestModal: React.FC<ConnectorTestModalProps> = ({
  connector,
  onClose,
  onTest,
  onSync,
  onRefresh
}) => {
  const [isTesting, setIsTesting] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [testResult, setTestResult] = useState<ConnectorTestResult | null>(null);
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTestConnection = async () => {
    try {
      setIsTesting(true);
      setError(null);
      setTestResult(null);
      
      const result = await onTest(connector.id);
      setTestResult(result);
    } catch (err) {
      console.error('Test failed:', err);
      setError('Connection test failed. Please check your configuration.');
    } finally {
      setIsTesting(false);
    }
  };

  const handleSyncData = async () => {
    try {
      setIsSyncing(true);
      setError(null);
      setSyncResult(null);
      
      const result = await onSync(connector.id);
      setSyncResult(result);
    } catch (err) {
      console.error('Sync failed:', err);
      setError('Data sync failed. Please try again.');
    } finally {
      setIsSyncing(false);
    }
  };

  const getConnectorIcon = (connectorType: string): string => {
    switch (connectorType) {
      case 'GOOGLE_WORKSPACE':
        return '📁';
      case 'EMAIL':
        return '📧';
      case 'SLACK':
        return '💬';
      case 'MICROSOFT_365':
        return '📄';
      case 'LIMS':
        return '🧪';
      default:
        return '🔌';
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'connected':
        return 'success';
      case 'connecting':
      case 'syncing':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'neutral';
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content test-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="header-content">
            <div className="connector-info">
              <span className="connector-icon">{getConnectorIcon(connector.connector_type)}</span>
              <div>
                <h3>{connector.name}</h3>
                <p className="connector-type">{connector.connector_type}</p>
              </div>
            </div>
            <div className={`status-badge status-${getStatusColor(connector.status)}`}>
              {connector.status}
            </div>
          </div>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body">
          {/* Connection Test Section */}
          <div className="test-section">
            <h4>🔍 Connection Test</h4>
            <p>Test the connection to verify authentication and connectivity.</p>
            
            <div className="test-buttons">
              <button
                className={`btn btn-primary ${isTesting ? 'loading' : ''}`}
                onClick={handleTestConnection}
                disabled={isTesting}
              >
                {isTesting ? 'Testing...' : 'Test Connection'}
              </button>
              
              {onRefresh && (
                <button
                  className="btn btn-secondary"
                  onClick={onRefresh}
                  disabled={isTesting}
                >
                  🔄 Refresh Status
                </button>
              )}
            </div>

            {testResult && (
              <div className={`result-box ${testResult.success ? 'success' : 'error'}`}>
                <div className="result-header">
                  <span className="result-icon">
                    {testResult.success ? '✅' : '❌'}
                  </span>
                  <span className="result-title">
                    {testResult.success ? 'Connection Successful' : 'Connection Failed'}
                  </span>
                </div>
                <p className="result-message">{testResult.message}</p>
                {testResult.details && (
                  <div className="result-details">
                    <pre>{JSON.stringify(testResult.details, null, 2)}</pre>
                  </div>
                )}
                
                {/* OAuth2 Authorization Button */}
                {!testResult.success && 
                 testResult.details?.error === 'No valid credentials' && 
                 testResult.details?.next_step === 'Complete OAuth2 authorization flow' && (
                  <div className="oauth2-section">
                    <div className="oauth2-info">
                      <span className="oauth2-icon">🔐</span>
                      <div>
                        <h5>OAuth2 Authorization Required</h5>
                        <p>This connector needs to be authorized to access your Google Drive.</p>
                      </div>
                    </div>
                    <button
                      className="btn btn-primary oauth2-button"
                      onClick={() => {
                        const authUrl = `http://localhost:8000/api/auth/google/authorize/${connector.id}`;
                        const popup = window.open(authUrl, '_blank', 'width=600,height=700');
                        
                        // Check if popup was closed or redirected
                        const checkAuth = setInterval(() => {
                          if (popup?.closed) {
                            clearInterval(checkAuth);
                            // Refresh the connector status after a short delay
                            setTimeout(() => {
                              if (onRefresh) {
                                onRefresh();
                              }
                            }, 1000);
                          } else if (popup) {
                            // Check if the popup has been redirected to the main page
                            try {
                              if (popup.location.href.includes('localhost:3000') && 
                                  (popup.location.href.includes('success=true') || 
                                   popup.location.href.includes('error='))) {
                                // OAuth2 flow completed, close popup
                                popup.close();
                                clearInterval(checkAuth);
                                // Refresh the connector status
                                setTimeout(() => {
                                  if (onRefresh) {
                                    onRefresh();
                                  }
                                }, 1000);
                              }
                            } catch (e) {
                              // Cross-origin error, popup is still on Google's domain
                              // Continue checking
                            }
                          }
                        }, 500);
                      }}
                    >
                      🔐 Authorize Google Drive Access
                    </button>
                    <p className="oauth2-note">
                      <small>
                        This will open Google's authorization page in a new window. 
                        After authorization, you'll be redirected back and can test the connection again.
                      </small>
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Data Sync Section */}
          <div className="test-section">
            <h4>🔄 Data Synchronization</h4>
            <p>Sync data from the connected source to update your local data.</p>
            
            <button
              className={`btn btn-success ${isSyncing ? 'loading' : ''}`}
              onClick={handleSyncData}
              disabled={isSyncing || connector.status !== 'connected'}
            >
              {isSyncing ? 'Syncing...' : 'Sync Data'}
            </button>

            {syncResult && (
              <div className={`result-box ${syncResult.success ? 'success' : 'error'}`}>
                <div className="result-header">
                  <span className="result-icon">
                    {syncResult.success ? '✅' : '❌'}
                  </span>
                  <span className="result-title">
                    {syncResult.success ? 'Sync Successful' : 'Sync Failed'}
                  </span>
                </div>
                <p className="result-message">{syncResult.message}</p>
                {syncResult.records_processed && (
                  <div className="sync-stats">
                    <span className="stat-item">
                      <strong>Records Processed:</strong> {syncResult.records_processed}
                    </span>
                    {syncResult.sync_log_id && (
                      <span className="stat-item">
                        <strong>Sync Log ID:</strong> {syncResult.sync_log_id}
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Configuration Details */}
          <div className="test-section">
            <h4>⚙️ Configuration Details</h4>
            <div className="config-details">
              <div className="config-item">
                <strong>Authentication Type:</strong> {connector.auth_type}
              </div>
              <div className="config-item">
                <strong>Created:</strong> {new Date(connector.created_at).toLocaleString()}
              </div>
              {connector.updated_at && (
                <div className="config-item">
                  <strong>Last Updated:</strong> {new Date(connector.updated_at).toLocaleString()}
                </div>
              )}
              {connector.description && (
                <div className="config-item">
                  <strong>Description:</strong> {connector.description}
                </div>
              )}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}
        </div>

        <div className="modal-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClose}
            disabled={isTesting || isSyncing}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConnectorTestModal;
