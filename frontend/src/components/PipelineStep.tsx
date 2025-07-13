import React from 'react';
import './PipelineStep.css';

interface PipelineStepProps {
  name: string;
  icon: string;
  action: string;
  isActive: boolean;
}

const PipelineStep: React.FC<PipelineStepProps> = ({
  name,
  icon,
  action,
  isActive
}) => {
  const handleAction = () => {
    console.log(`${action} ${name}...`);
    // TODO: Implement action logic
  };

  return (
    <div className={`pipeline-step ${isActive ? 'active' : ''}`}>
      <div className="step-icon">{icon}</div>
      <div className="step-content">
        <h3 className="step-name">{name}</h3>
        <button
          className={`step-action ${isActive ? 'active' : ''}`}
          onClick={handleAction}
        >
          {action}
        </button>
      </div>
    </div>
  );
};

export default PipelineStep; 