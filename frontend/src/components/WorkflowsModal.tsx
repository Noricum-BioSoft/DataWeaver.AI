import React from 'react';
import './WorkflowsModal.css';

interface WorkflowsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const WorkflowsModal: React.FC<WorkflowsModalProps> = ({ isOpen, onClose }) => {
  const workflows = [
    {
      id: 1,
      name: 'Protein Analysis Pipeline',
      status: 'Running',
      progress: 75,
      steps: 5,
      completedSteps: 3,
      created: '2 hours ago'
    },
    {
      id: 2,
      name: 'Data Merge Workflow',
      status: 'Completed',
      progress: 100,
      steps: 3,
      completedSteps: 3,
      created: '1 day ago'
    },
    {
      id: 3,
      name: 'Sequence Processing',
      status: 'Pending',
      progress: 0,
      steps: 4,
      completedSteps: 0,
      created: '3 hours ago'
    }
  ];

  if (!isOpen) return null;

  return (
    <div className="workflows-modal-overlay" onClick={onClose}>
      <div className="workflows-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>⚙️ Workflows</h2>
          <div className="simulation-badge" title="This data is simulated for demonstration purposes. Real workflow management needs to be implemented for production use.">🧪 Simulation Data</div>
          <button className="modal-close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div className="modal-content">
          <div className="workflows-list">
            {workflows.map(workflow => (
              <div key={workflow.id} className="workflow-item" title={`${workflow.name} - ${workflow.status} workflow with ${workflow.completedSteps}/${workflow.steps} steps completed. Created ${workflow.created}`}>
                <div className="workflow-header">
                  <h3 className="workflow-name">{workflow.name}</h3>
                  <span className={`status-badge ${workflow.status.toLowerCase()}`} title={`Workflow status: ${workflow.status} - ${workflow.status === 'Running' ? 'Currently executing' : workflow.status === 'Completed' ? 'Successfully finished' : 'Waiting to start'}`}>
                    {workflow.status}
                  </span>
                </div>
                
                <div className="workflow-progress">
                                              <div className="progress-bar" title={`Progress: ${workflow.progress}% complete (${workflow.completedSteps} of ${workflow.steps} steps finished)`}>
                              <div
                                className="progress-fill"
                                style={{ width: `${workflow.progress}%` }}
                              ></div>
                            </div>
                  <span className="progress-text">{workflow.progress}%</span>
                </div>
                
                <div className="workflow-details">
                  <span className="workflow-steps">
                    {workflow.completedSteps}/{workflow.steps} steps completed
                  </span>
                  <span className="workflow-created">Created {workflow.created}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="integration-note" title="Click to learn more about implementing real workflow management">
            <p>💡 <strong>Production Integration Required:</strong> This demo shows simulated data. For production use, implement custom integrations with your actual workflow management systems and APIs.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowsModal;
