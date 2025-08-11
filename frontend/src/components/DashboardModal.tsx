import React from 'react';
import './DashboardModal.css';

interface DashboardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const DashboardModal: React.FC<DashboardModalProps> = ({ isOpen, onClose }) => {
  const metrics = [
    {
      id: 1,
      name: 'Active Workflows',
      value: '12',
      change: '+2',
      trend: 'up'
    },
    {
      id: 2,
      name: 'Total Files',
      value: '1,247',
      change: '+15',
      trend: 'up'
    },
    {
      id: 3,
      name: 'Connected Sources',
      value: '8',
      change: 'All healthy',
      trend: 'neutral'
    },
    {
      id: 4,
      name: 'Processing Speed',
      value: '2.3s',
      change: '-0.5s',
      trend: 'up'
    }
  ];

  if (!isOpen) return null;

  return (
    <div className="dashboard-modal-overlay" onClick={onClose}>
      <div className="dashboard-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>📊 Dashboard</h2>
          <div className="simulation-badge">🧪 Simulation Data</div>
          <button className="modal-close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div className="modal-content">
          <div className="metrics-grid">
            {metrics.map(metric => (
              <div key={metric.id} className="metric-card">
                <h3 className="metric-name">{metric.name}</h3>
                <p className="metric-value">{metric.value}</p>
                <span className={`metric-change ${metric.trend}`}>
                  {metric.change}
                </span>
              </div>
            ))}
          </div>
          <div className="integration-note">
            <p>💡 <strong>Production Integration Required:</strong> This demo shows simulated data. For production use, implement custom integrations with your actual monitoring and analytics systems.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardModal;
