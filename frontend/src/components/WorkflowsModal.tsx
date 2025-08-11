import React, { useState } from 'react';
import './WorkflowsModal.css';

interface WorkflowsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const WorkflowsModal: React.FC<WorkflowsModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'analysis' | 'visualization' | 'qa'>('analysis');
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

  const dataAnalysisExamples = [
    {
      id: 1,
      name: '📊 Statistical Analysis',
      description: 'Perform statistical tests, correlations, and descriptive statistics',
      examples: ['Calculate correlation between variables', 'Perform t-test analysis', 'Generate summary statistics']
    },
    {
      id: 2,
      name: '🔍 Data Exploration',
      description: 'Explore data patterns, distributions, and relationships',
      examples: ['Show data distribution', 'Find outliers', 'Analyze trends over time']
    },
    {
      id: 3,
      name: '📈 Trend Analysis',
      description: 'Identify patterns and trends in your data',
      examples: ['Detect seasonal patterns', 'Forecast future values', 'Identify growth trends']
    }
  ];

  const visualizationExamples = [
    {
      id: 1,
      name: '📊 Charts & Graphs',
      description: 'Create various types of charts and visualizations',
      examples: ['Bar charts', 'Line plots', 'Scatter plots', 'Histograms']
    },
    {
      id: 2,
      name: '🗺️ Geographic Visualizations',
      description: 'Map-based visualizations for location data',
      examples: ['Choropleth maps', 'Point maps', 'Heat maps']
    },
    {
      id: 3,
      name: '📋 Interactive Dashboards',
      description: 'Interactive visualizations with filtering and exploration',
      examples: ['Filterable charts', 'Drill-down capabilities', 'Real-time updates']
    }
  ];

  const qaExamples = [
    {
      id: 1,
      name: '❓ Data Questions',
      description: 'Ask specific questions about your data',
      examples: ['What is the average value?', 'Which records have missing data?', 'How many unique values?']
    },
    {
      id: 2,
      name: '🔍 Pattern Discovery',
      description: 'Discover patterns and insights in your data',
      examples: ['Find correlations', 'Identify clusters', 'Detect anomalies']
    },
    {
      id: 3,
      name: '📋 Summary Reports',
      description: 'Generate comprehensive data summaries',
      examples: ['Data quality report', 'Statistical summary', 'Key insights report']
    }
  ];

  const handleAnalysisRequest = (example: string) => {
    console.log('Analysis request:', example);
    // TODO: Implement analysis request
    onClose();
  };

  const handleVisualizationRequest = (example: string) => {
    console.log('Visualization request:', example);
    // TODO: Implement visualization request
    onClose();
  };

  const handleQARequest = (example: string) => {
    console.log('QA request:', example);
    // TODO: Implement QA request
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="workflows-modal-overlay" onClick={onClose}>
      <div className="workflows-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🔬 Data Science</h2>
          <div className="simulation-badge" title="This data is simulated for demonstration purposes. Real data science capabilities need to be implemented for production use.">🧪 Simulation Data</div>
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
              className={`tab-button ${activeTab === 'analysis' ? 'active' : ''}`}
              onClick={() => setActiveTab('analysis')}
            >
              Data Analysis
            </button>
            <button 
              className={`tab-button ${activeTab === 'visualization' ? 'active' : ''}`}
              onClick={() => setActiveTab('visualization')}
            >
              Visualization
            </button>
            <button 
              className={`tab-button ${activeTab === 'qa' ? 'active' : ''}`}
              onClick={() => setActiveTab('qa')}
            >
              Q&A
            </button>
          </div>

          {/* Data Analysis Tab */}
          {activeTab === 'analysis' && (
            <div className="analysis-section">
              <div className="examples-grid">
                {dataAnalysisExamples.map(example => (
                  <div key={example.id} className="example-card">
                    <div className="example-header">
                      <h3 className="example-name">{example.name}</h3>
                    </div>
                    <p className="example-description">{example.description}</p>
                    <div className="example-list">
                      {example.examples.map((item, index) => (
                        <button 
                          key={index}
                          className="example-item"
                          onClick={() => handleAnalysisRequest(item)}
                          title={`Click to request: ${item}`}
                        >
                          {item}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Visualization Tab */}
          {activeTab === 'visualization' && (
            <div className="visualization-section">
              <div className="examples-grid">
                {visualizationExamples.map(example => (
                  <div key={example.id} className="example-card">
                    <div className="example-header">
                      <h3 className="example-name">{example.name}</h3>
                    </div>
                    <p className="example-description">{example.description}</p>
                    <div className="example-list">
                      {example.examples.map((item, index) => (
                        <button 
                          key={index}
                          className="example-item"
                          onClick={() => handleVisualizationRequest(item)}
                          title={`Click to request: ${item}`}
                        >
                          {item}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Q&A Tab */}
          {activeTab === 'qa' && (
            <div className="qa-section">
              <div className="examples-grid">
                {qaExamples.map(example => (
                  <div key={example.id} className="example-card">
                    <div className="example-header">
                      <h3 className="example-name">{example.name}</h3>
                    </div>
                    <p className="example-description">{example.description}</p>
                    <div className="example-list">
                      {example.examples.map((item, index) => (
                        <button 
                          key={index}
                          className="example-item"
                          onClick={() => handleQARequest(item)}
                          title={`Click to request: ${item}`}
                        >
                          {item}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="integration-note" title="Click to learn more about implementing real data science capabilities">
            <p>💡 <strong>Production Integration Required:</strong> This demo shows simulated data. For production use, implement custom integrations with your actual data science and analytics systems.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowsModal;
