import React, { useState } from 'react';
import './WorkflowsModal.css';

interface WorkflowsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const WorkflowsModal: React.FC<WorkflowsModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'existing' | 'create' | 'templates'>('existing');
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

  const workflowTemplates = [
    {
      id: 1,
      name: '🧬 Bioinformatics Pipeline',
      description: 'Complete pipeline for protein sequence analysis and visualization',
      steps: 6,
      estimatedTime: '15-30 min',
      category: 'Biology'
    },
    {
      id: 2,
      name: '📊 Data Analysis Workflow',
      description: 'Standard workflow for data cleaning, analysis, and reporting',
      steps: 4,
      estimatedTime: '10-20 min',
      category: 'General'
    },
    {
      id: 3,
      name: '🔄 ETL Pipeline',
      description: 'Extract, Transform, Load pipeline for data integration',
      steps: 5,
      estimatedTime: '20-45 min',
      category: 'Data Engineering'
    },
    {
      id: 4,
      name: '📈 Business Intelligence',
      description: 'Workflow for creating dashboards and business reports',
      steps: 3,
      estimatedTime: '5-15 min',
      category: 'Business'
    }
  ];

  const handleCreateWorkflow = () => {
    console.log('Creating new workflow...');
    // TODO: Implement workflow creation
    setActiveTab('existing');
  };

  const handleUseTemplate = (templateId: number) => {
    console.log('Using template:', templateId);
    // TODO: Implement template usage
    setActiveTab('existing');
  };

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
          {/* Tab Navigation */}
          <div className="workflow-tabs">
            <button 
              className={`tab-button ${activeTab === 'existing' ? 'active' : ''}`}
              onClick={() => setActiveTab('existing')}
            >
              Existing Workflows ({workflows.length})
            </button>
            <button 
              className={`tab-button ${activeTab === 'create' ? 'active' : ''}`}
              onClick={() => setActiveTab('create')}
            >
              Create New
            </button>
            <button 
              className={`tab-button ${activeTab === 'templates' ? 'active' : ''}`}
              onClick={() => setActiveTab('templates')}
            >
              Templates
            </button>
          </div>

          {/* Existing Workflows Tab */}
          {activeTab === 'existing' && (
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
          )}

          {/* Create New Workflow Tab */}
          {activeTab === 'create' && (
            <div className="create-workflow-section">
              <div className="create-options">
                <div className="option-card" onClick={handleCreateWorkflow}>
                  <div className="option-icon">🎨</div>
                  <h3>Visual Workflow Builder</h3>
                  <p>Drag and drop interface to create custom workflows with predefined tasks</p>
                  <div className="option-features">
                    <span>• Visual designer</span>
                    <span>• Task library</span>
                    <span>• Conditional logic</span>
                  </div>
                </div>
                
                <div className="option-card" onClick={() => setActiveTab('templates')}>
                  <div className="option-icon">📝</div>
                  <h3>Natural Language</h3>
                  <p>Describe your workflow in plain English and let AI generate it for you</p>
                  <div className="option-features">
                    <span>• AI-powered</span>
                    <span>• Natural language</span>
                    <span>• Smart suggestions</span>
                  </div>
                </div>
                
                <div className="option-card" onClick={() => setActiveTab('templates')}>
                  <div className="option-icon">⚡</div>
                  <h3>Quick Start</h3>
                  <p>Choose from pre-built templates and customize them for your needs</p>
                  <div className="option-features">
                    <span>• Pre-built templates</span>
                    <span>• One-click setup</span>
                    <span>• Easy customization</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Templates Tab */}
          {activeTab === 'templates' && (
            <div className="templates-section">
              <div className="templates-grid">
                {workflowTemplates.map(template => (
                  <div key={template.id} className="template-card" onClick={() => handleUseTemplate(template.id)}>
                    <div className="template-header">
                      <h3 className="template-name">{template.name}</h3>
                      <span className="template-category">{template.category}</span>
                    </div>
                    <p className="template-description">{template.description}</p>
                    <div className="template-meta">
                      <span className="template-steps">{template.steps} steps</span>
                      <span className="template-time">{template.estimatedTime}</span>
                    </div>
                    <button className="use-template-btn">
                      Use Template
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="integration-note" title="Click to learn more about implementing real workflow management">
            <p>💡 <strong>Production Integration Required:</strong> This demo shows simulated data. For production use, implement custom integrations with your actual workflow management systems and APIs.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowsModal;
