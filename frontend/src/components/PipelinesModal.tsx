import React from 'react';
import './PipelinesModal.css';

interface PipelinesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const PipelinesModal: React.FC<PipelinesModalProps> = ({ isOpen, onClose }) => {
  const pipelines = [
    {
      id: 1,
      name: 'Data Processing Pipeline',
      status: 'Active',
      throughput: '1.2 GB/s',
      nodes: 3,
      lastRun: '5 minutes ago'
    },
    {
      id: 2,
      name: 'ETL Pipeline',
      status: 'Idle',
      throughput: '0.8 GB/s',
      nodes: 2,
      lastRun: '2 hours ago'
    },
    {
      id: 3,
      name: 'Analytics Pipeline',
      status: 'Maintenance',
      throughput: '0.5 GB/s',
      nodes: 1,
      lastRun: '1 day ago'
    }
  ];

  if (!isOpen) return null;

  return (
    <div className="pipelines-modal-overlay" onClick={onClose}>
      <div className="pipelines-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🔗 Pipelines</h2>
          <button className="modal-close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div className="modal-content">
          <div className="pipelines-list">
            {pipelines.map(pipeline => (
              <div key={pipeline.id} className="pipeline-item">
                <div className="pipeline-info">
                  <h3 className="pipeline-name">{pipeline.name}</h3>
                  <p className="pipeline-details">
                    {pipeline.throughput} • {pipeline.nodes} nodes • Last run: {pipeline.lastRun}
                  </p>
                </div>
                <span className={`status-badge ${pipeline.status.toLowerCase()}`}>
                  {pipeline.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PipelinesModal;
