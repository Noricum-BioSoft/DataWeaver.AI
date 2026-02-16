import React, { useState } from 'react';
import { Connector, ConnectorStatus } from '../types';
import './ConnectorCard.css';

interface ConnectorCardProps {
  connector: Connector;
  icon: string;
  name: string;
  status: ConnectorStatus;
  lastSynced?: string;
  isConnected: boolean;
  onTestConnection?: () => Promise<any>;
  onSyncData?: () => Promise<any>;
  onDelete?: () => Promise<void>;
}

const ConnectorCard: React.FC<ConnectorCardProps> = ({
  connector,
  icon,
  name,
  status,
  lastSynced,
  isConnected,
  onTestConnection,
  onSyncData,
  onDelete
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const handleAction = async (action: () => Promise<any>, actionName: string) => {
    if (!action) return;
    
    try {
      setIsLoading(true);
      setActionMessage(`${actionName}...`);
      await action();
      setActionMessage(`${actionName} successful!`);
      setTimeout(() => setActionMessage(null), 2000);
    } catch (error) {
      console.error(`${actionName} failed:`, error);
      setActionMessage(`${actionName} failed. Please try again.`);
      setTimeout(() => setActionMessage(null), 3000);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestConnection = () => onTestConnection && handleAction(onTestConnection, 'Testing connection');
  const handleSyncData = () => onSyncData && handleAction(onSyncData, 'Syncing data');
  const handleDelete = () => onDelete && handleAction(onDelete, 'Deleting connector');

  const getStatusColor = (status: ConnectorStatus): string => {
    switch (status) {
      case ConnectorStatus.CONNECTED:
        return 'connected';
      case ConnectorStatus.CONNECTING:
      case ConnectorStatus.SYNCING:
        return 'connecting';
      case ConnectorStatus.ERROR:
        return 'error';
      default:
        return 'disconnected';
    }
  };

  return (
    <div className="connector-card">
      <div className="connector-header">
        <div className="connector-icon">{icon}</div>
        <div className="connector-info">
          <h3 className="connector-name">{name}</h3>
          <div className="connector-status">
            <span 
              className={`status-indicator ${getStatusColor(status)}`} 
              title={isConnected ? 'Connected and ready for data transfer' : 'Not connected - click to authenticate'}
            ></span>
            <span className="status-text" title={`Current status: ${status}`}>
              {status}
            </span>
          </div>
        </div>
      </div>
      
      <div className="connector-details">
        {lastSynced && <p className="last-synced">Last synced: {lastSynced}</p>}
        {actionMessage && (
          <div className={`action-message ${actionMessage.includes('failed') ? 'error' : 'success'}`}>
            {actionMessage}
          </div>
        )}
        
        <div className="connector-actions">
          {onTestConnection && (
            <button
              className="action-button test-button"
              onClick={handleTestConnection}
              disabled={isLoading}
              title="Test connection"
            >
              {isLoading ? 'Testing...' : 'Test'}
            </button>
          )}
          
          {onSyncData && isConnected && (
            <button
              className="action-button sync-button"
              onClick={handleSyncData}
              disabled={isLoading}
              title="Sync data sources"
            >
              {isLoading ? 'Syncing...' : 'Sync'}
            </button>
          )}
          
          {onDelete && (
            <button
              className="action-button delete-button"
              onClick={handleDelete}
              disabled={isLoading}
              title="Delete connector"
            >
              {isLoading ? 'Deleting...' : 'Delete'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConnectorCard; 