import React from 'react';
import PipelineStep from './PipelineStep';
import './PipelineSection.css';

const PipelineSection: React.FC = () => {
  const pipelineSteps = [
    {
      id: 1,
      name: 'API Request',
      icon: '📡',
      action: 'Connect',
      isActive: true
    },
    {
      id: 2,
      name: 'Transformation',
      icon: '⚙️',
      action: 'Run',
      isActive: false
    },
    {
      id: 3,
      name: 'API Response',
      icon: '📊',
      action: 'Connect',
      isActive: false
    }
  ];

  const handleAddPipeline = () => {
    console.log('Adding new pipeline...');
    // Add pipeline logic will be implemented in future versions
  };

  return (
    <div className="section">
      <div className="section-header">
        <h2>🔄 Data Processing Pipelines</h2>
      </div>
      <div className="section-content">
        <div className="pipeline-container">
          <div className="pipeline-steps">
            {pipelineSteps.map((step, index) => (
              <React.Fragment key={step.id}>
                <PipelineStep
                  name={step.name}
                  icon={step.icon}
                  action={step.action}
                  isActive={step.isActive}
                />
                {index < pipelineSteps.length - 1 && (
                  <div className="pipeline-arrow">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
          <button className="add-pipeline-button" onClick={handleAddPipeline}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            Add Pipeline
          </button>
        </div>
      </div>
    </div>
  );
};

export default PipelineSection; 