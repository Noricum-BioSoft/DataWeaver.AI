import React, { useState } from 'react';
import { Connector, ConnectorUpdate } from '../types';
import './ConnectorDetailsModal.css';

interface ConnectorDetailsModalProps {
  connector: Connector;
  onClose: () => void;
  onUpdate: (connectorId: number, updates: ConnectorUpdate) => Promise<void>;
  onDelete: (connectorId: number) => Promise<void>;
}

const ConnectorDetailsModal: React.FC<ConnectorDetailsModalProps> = ({
  connector,
  onClose,
  onUpdate,
  onDelete
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [formData, setFormData] = useState({
    name: connector.name,
    description: connector.description || '',
    config: connector.config
  });
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setError(null);
      
      const updates: ConnectorUpdate = {
        name: formData.name,
        description: formData.description || undefined,
        config: formData.config
      };
      
      await onUpdate(connector.id, updates);
      setIsEditing(false);
    } catch (err) {
      console.error('Update failed:', err);
      setError('Failed to update connector. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this connector? This action cannot be undone.')) {
      return;
    }

    try {
      setIsDeleting(true);
      setError(null);
      
      await onDelete(connector.id);
      onClose();
    } catch (err) {
      console.error('Delete failed:', err);
      setError('Failed to delete connector. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
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

  const renderConfigDetails = () => {
    if (!connector.config || Object.keys(connector.config).length === 0) {
      return <p className="no-config">No configuration details available.</p>;
    }

    return (
      <div className="config-details">
        {Object.entries(connector.config).map(([key, value]) => (
          <div key={key} className="config-item">
            <strong>{key}:</strong>
            <span className="config-value">
              {typeof value === 'string' && (key.includes('password') || key.includes('secret') || key.includes('token'))
                ? '••••••••'
                : typeof value === 'object'
                ? JSON.stringify(value, null, 2)
                : String(value)
              }
            </span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content details-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="header-content">
            <div className="connector-info">
              <span className="connector-icon">{getConnectorIcon(connector.connector_type)}</span>
              <div>
                <h3>{isEditing ? 'Edit Connector' : connector.name}</h3>
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
          {isEditing ? (
            /* Edit Form */
            <div className="edit-form">
              <div className="form-group">
                <label htmlFor="name">Connector Name *</label>
                <input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="form-textarea"
                  rows={3}
                  placeholder="Optional description for this connector"
                />
              </div>

              <div className="form-group">
                <label>Configuration</label>
                <div className="config-note">
                  <p>⚠️ Configuration changes should be made carefully. Some changes may require re-authentication.</p>
                </div>
                <textarea
                  value={JSON.stringify(formData.config, null, 2)}
                  onChange={(e) => {
                    try {
                      const parsed = JSON.parse(e.target.value);
                      handleInputChange('config', parsed);
                    } catch (err) {
                      // Allow invalid JSON during typing
                    }
                  }}
                  className="form-textarea config-json"
                  rows={8}
                  placeholder="Configuration JSON"
                />
              </div>
            </div>
          ) : (
            /* View Details */
            <div className="details-view">
              <div className="detail-section">
                <h4>📋 Basic Information</h4>
                <div className="detail-grid">
                  <div className="detail-item">
                    <strong>Name:</strong> {connector.name}
                  </div>
                  <div className="detail-item">
                    <strong>Type:</strong> {connector.connector_type}
                  </div>
                  <div className="detail-item">
                    <strong>Authentication:</strong> {connector.auth_type}
                  </div>
                  <div className="detail-item">
                    <strong>Status:</strong> 
                    <span className={`status-text status-${getStatusColor(connector.status)}`}>
                      {connector.status}
                    </span>
                  </div>
                  {connector.description && (
                    <div className="detail-item full-width">
                      <strong>Description:</strong> {connector.description}
                    </div>
                  )}
                </div>
              </div>

              <div className="detail-section">
                <h4>📅 Timestamps</h4>
                <div className="detail-grid">
                  <div className="detail-item">
                    <strong>Created:</strong> {new Date(connector.created_at).toLocaleString()}
                  </div>
                  {connector.updated_at && (
                    <div className="detail-item">
                      <strong>Last Updated:</strong> {new Date(connector.updated_at).toLocaleString()}
                    </div>
                  )}
                </div>
              </div>

              <div className="detail-section">
                <h4>⚙️ Configuration</h4>
                {renderConfigDetails()}
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}
        </div>

        <div className="modal-actions">
          {isEditing ? (
            <>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setIsEditing(false)}
                disabled={isSaving}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleSave}
                disabled={isSaving || !formData.name.trim()}
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                className="btn btn-danger"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting...' : 'Delete Connector'}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setIsEditing(true)}
              >
                Edit
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={onClose}
              >
                Close
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConnectorDetailsModal;
