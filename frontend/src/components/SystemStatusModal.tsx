import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { connectorApi } from '../services/api';
import './SystemStatusModal.css';

interface Connector {
  id: number;
  name: string;
  connector_type: string;
  status: string;
  auth_type: string;
  last_sync?: string;
  next_sync?: string;
  config: any;
}

interface SystemStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStatusChange?: (status: 'operational' | 'warning' | 'error') => void;
  onConnectorCountChange?: (count: { total: number; connected: number; disconnected: number }) => void;
}

const SystemStatusModal: React.FC<SystemStatusModalProps> = ({ isOpen, onClose, onStatusChange, onConnectorCountChange }) => {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [backendStatus, setBackendStatus] = useState<'operational' | 'warning' | 'error'>('operational');
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  useEffect(() => {
    if (isOpen) {
      loadSystemStatus();
    }
  }, [isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadSystemStatus = async () => {
    setLoading(true);
    try {
      // Load connectors
      const connectorsResponse = await connectorApi.getConnectors();
      setConnectors(connectorsResponse);

      // Test backend health
      try {
        const response = await fetch('/api/health');
        if (response.ok) {
          setBackendStatus('operational');
        } else {
          setBackendStatus('error');
        }
      } catch (error) {
        setBackendStatus('error');
      }

      // Update parent component status
      if (onStatusChange) {
        const overallStatus = backendStatus === 'operational' && connectors.length > 0 
          ? (connectors.some(c => c.status === 'connected') ? 'operational' : 'warning')
          : backendStatus;
        onStatusChange(overallStatus);
      }

      // Update connector count
      if (onConnectorCountChange) {
        const connected = connectors.filter(c => c.status === 'connected').length;
        const disconnected = connectors.filter(c => c.status === 'disconnected').length;
        onConnectorCountChange({
          total: connectors.length,
          connected,
          disconnected
        });
      }

      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error loading system status:', error);
      setBackendStatus('error');
    } finally {
      setLoading(false);
    }
  };



  const getOverallStatus = () => {
    // Check if backend is operational
    if (backendStatus !== 'operational') {
      return 'unhealthy';
    }
    
    // Check if there are any disconnected connectors
    const hasDisconnectedConnectors = connectors.some(c => c.status === 'disconnected');
    if (hasDisconnectedConnectors) {
      return 'unhealthy';
    }
    
    return 'healthy';
  };



  if (!isOpen) return null;

  return (
    <div className="system-status-modal-overlay" onClick={onClose}>
      <div className="system-status-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="header-content">
            <h2>System Status</h2>
            <div className="overall-status">
              <span className={`status-badge ${getOverallStatus() === 'healthy' ? 'healthy' : 'unhealthy'}`}>
                {getOverallStatus() === 'healthy' ? 'Healthy' : 'Unhealthy'}
              </span>
            </div>
          </div>
          <button className="close-button" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-content">
          {loading ? (
            <div className="loading">Loading system status...</div>
          ) : (
            <>
              {/* Status Table */}
              <table className="status-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {/* Backend Row */}
                  <tr>
                    <td>Backend</td>
                    <td>Backend</td>
                    <td>
                      <span className={`status-badge ${backendStatus === 'operational' ? 'healthy' : 'unhealthy'}`}>
                        {backendStatus === 'operational' ? 'Healthy' : 'Unhealthy'}
                      </span>
                    </td>
                  </tr>
                  
                  {/* Connector Rows */}
                  {connectors.map((connector) => (
                    <tr key={connector.id}>
                      <td>{connector.name}</td>
                      <td>{connector.connector_type}</td>
                      <td>
                        <span className={`status-badge ${connector.status === 'connected' ? 'healthy' : 'unhealthy'}`}>
                          {connector.status === 'connected' ? 'Connected' : 'Disconnected'}
                        </span>
                      </td>
                    </tr>
                  ))}
                  
                  {connectors.length === 0 && (
                    <tr>
                      <td colSpan={3} className="empty-cell">No connectors configured</td>
                    </tr>
                  )}
                </tbody>
              </table>

              {/* Summary and Refresh */}
              <div className="summary-info">
                <span>Total: {connectors.length + 1} | Connected: {connectors.filter(c => c.status === 'connected').length + (backendStatus === 'operational' ? 1 : 0)} | Last Updated: {lastUpdated.toLocaleTimeString()}</span>
              </div>
              <div className="refresh-section">
                <button className="refresh-button" onClick={loadSystemStatus}>
                  Refresh Status
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SystemStatusModal;
