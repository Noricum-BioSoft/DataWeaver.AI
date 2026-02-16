import React, { useState } from 'react';
import { ConnectorType, AuthenticationType, ConnectorCreate } from '../types';
import './ConnectorSetupModal.css';

interface ConnectorSetupModalProps {
  connectorType: ConnectorType;
  onClose: () => void;
  onSubmit: (connectorData: ConnectorCreate) => Promise<void>;
}

const ConnectorSetupModal: React.FC<ConnectorSetupModalProps> = ({
  connectorType,
  onClose,
  onSubmit
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    auth_type: AuthenticationType.OAUTH2,
    config: {} as Record<string, any>
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getConnectorDisplayName = (): string => {
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



  const getAuthTypeOptions = (): { value: AuthenticationType; label: string }[] => {
    switch (connectorType) {
      case ConnectorType.GOOGLE_WORKSPACE:
        return [
          { value: AuthenticationType.OAUTH2, label: 'OAuth 2.0' },
          { value: AuthenticationType.API_KEY, label: 'API Key' }
        ];
      case ConnectorType.EMAIL:
        return [
          { value: AuthenticationType.USERNAME_PASSWORD, label: 'Username & Password' },
          { value: AuthenticationType.OAUTH2, label: 'OAuth 2.0' }
        ];
      default:
        return [
          { value: AuthenticationType.OAUTH2, label: 'OAuth 2.0' },
          { value: AuthenticationType.API_KEY, label: 'API Key' },
          { value: AuthenticationType.USERNAME_PASSWORD, label: 'Username & Password' },
          { value: AuthenticationType.TOKEN, label: 'Token' }
        ];
    }
  };

  const handleInputChange = (field: string, value: any) => {
    if (field.startsWith('config.')) {
      const configField = field.replace('config.', '');
      setFormData(prev => ({
        ...prev,
        config: {
          ...prev.config,
          [configField]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('Connector name is required');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      
      const connectorData: ConnectorCreate = {
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        connector_type: connectorType,
        auth_type: formData.auth_type,
        config: formData.config
      };

      await onSubmit(connectorData);
    } catch (err) {
      console.error('Failed to create connector:', err);
      setError('Failed to create connector. Please check your configuration and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderConfigFields = () => {
    switch (connectorType) {
      case ConnectorType.GOOGLE_WORKSPACE:
        return (
          <div className="config-section">
            <h4>Google Workspace Configuration</h4>
            <div className="form-group">
              <label htmlFor="client_id">Client ID *</label>
              <input
                type="text"
                id="client_id"
                value={formData.config.client_id || ''}
                onChange={(e) => handleInputChange('config.client_id', e.target.value)}
                placeholder="Enter your Google OAuth Client ID"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="client_secret">Client Secret *</label>
              <input
                type="password"
                id="client_secret"
                value={formData.config.client_secret || ''}
                onChange={(e) => handleInputChange('config.client_secret', e.target.value)}
                placeholder="Enter your Google OAuth Client Secret"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="redirect_uri">Redirect URI</label>
              <input
                type="text"
                id="redirect_uri"
                value={formData.config.redirect_uri || ''}
                onChange={(e) => handleInputChange('config.redirect_uri', e.target.value)}
                placeholder="http://localhost:3000/auth/callback"
              />
            </div>
            <div className="help-text">
              <p>💡 <strong>Setup Instructions:</strong></p>
              <ol>
                <li>Go to <a href="https://console.developers.google.com" target="_blank" rel="noopener noreferrer">Google Cloud Console</a></li>
                <li>Create a new project or select existing one</li>
                <li>Enable Google Drive API</li>
                <li>Create OAuth 2.0 credentials</li>
                <li>Add your redirect URI to authorized redirect URIs</li>
              </ol>
            </div>
          </div>
        );

      case ConnectorType.EMAIL:
        return (
          <div className="config-section">
            <h4>Email Configuration</h4>
            <div className="form-group">
              <label htmlFor="server">Mail Server *</label>
              <input
                type="text"
                id="server"
                value={formData.config.server || ''}
                onChange={(e) => handleInputChange('config.server', e.target.value)}
                placeholder="e.g., smtp.gmail.com, outlook.office365.com"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="port">Port *</label>
              <input
                type="number"
                id="port"
                value={formData.config.port || 587}
                onChange={(e) => handleInputChange('config.port', parseInt(e.target.value))}
                placeholder="587"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="username">Username/Email *</label>
              <input
                type="email"
                id="username"
                value={formData.config.username || ''}
                onChange={(e) => handleInputChange('config.username', e.target.value)}
                placeholder="your-email@domain.com"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                value={formData.config.password || ''}
                onChange={(e) => handleInputChange('config.password', e.target.value)}
                placeholder="Enter your password or app password"
                required
              />
            </div>
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.config.use_ssl || false}
                  onChange={(e) => handleInputChange('config.use_ssl', e.target.checked)}
                />
                Use SSL/TLS
              </label>
            </div>
            <div className="form-group">
              <label htmlFor="folder">Folder</label>
              <input
                type="text"
                id="folder"
                value={formData.config.folder || 'INBOX'}
                onChange={(e) => handleInputChange('config.folder', e.target.value)}
                placeholder="INBOX"
              />
            </div>
            <div className="help-text">
              <p>💡 <strong>Setup Instructions:</strong></p>
              <ul>
                <li>For Gmail: Use app password instead of regular password</li>
                <li>For Outlook: Enable 2FA and use app password</li>
                <li>Port 587 is recommended for most providers</li>
                <li>Enable SSL/TLS for secure connections</li>
              </ul>
            </div>
          </div>
        );

      default:
        return (
          <div className="config-section">
            <h4>Configuration</h4>
            <p>Configuration fields will be available based on the selected authentication type.</p>
          </div>
        );
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Setup {getConnectorDisplayName()} Connector</h3>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="connector-form">
          <div className="form-section">
            <h4>Basic Information</h4>
            <div className="form-group">
              <label htmlFor="name">Connector Name *</label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder={`My ${getConnectorDisplayName()} Connector`}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Optional description for this connector"
                rows={3}
              />
            </div>
          </div>

          <div className="form-section">
            <h4>Authentication</h4>
            <div className="form-group">
              <label htmlFor="auth_type">Authentication Type *</label>
              <select
                id="auth_type"
                value={formData.auth_type}
                onChange={(e) => handleInputChange('auth_type', e.target.value as AuthenticationType)}
                required
              >
                {getAuthTypeOptions().map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {renderConfigFields()}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="modal-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Create Connector'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ConnectorSetupModal;
