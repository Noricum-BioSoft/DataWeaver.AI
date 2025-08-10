import React from 'react';

interface DataContextPanelProps {
  sessionId: string;
}

const DataContextPanel: React.FC<DataContextPanelProps> = ({ sessionId }) => {
  return (
    <div className="data-context-panel">
      <div className="panel-header">
        <h3>Data Context</h3>
        <span>Session: {sessionId}</span>
      </div>
      <div className="panel-content">
        <p>Data context information will be displayed here.</p>
      </div>
    </div>
  );
};

export default DataContextPanel;
