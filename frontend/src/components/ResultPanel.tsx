import React from 'react';
import { 
  FileText, 
  BarChart3, 
  GitBranch, 
  Link, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  TrendingUp,
  Download,
  Eye
} from 'lucide-react';
import './ResultPanel.css';

interface ResultPanelProps {
  result: any;
}

const ResultPanel: React.FC<ResultPanelProps> = ({ result }) => {
  const renderConnectorResult = (data: any) => (
    <div className="result-card connector">
      <div className="result-header">
        <Link size={20} />
        <h3>Connecting to {data.provider}</h3>
        <div className={`status-badge ${data.status}`}>
          {data.status === 'connecting' ? 'Connecting...' : 'Connected'}
        </div>
      </div>
      <div className="result-content">
        <div className="steps-list">
          {data.steps.map((step: string, index: number) => (
            <div key={index} className="step-item">
              <div className="step-icon">
                {index < 2 ? <CheckCircle size={16} /> : <Clock size={16} />}
              </div>
              <span>{step}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderWorkflowList = (data: any[]) => (
    <div className="result-card workflow-list">
      <div className="result-header">
        <GitBranch size={20} />
        <h3>Workflows & Pipelines</h3>
      </div>
      <div className="result-content">
        <div className="workflow-grid">
          {data.map((workflow) => (
            <div key={workflow.id} className="workflow-item">
              <div className="workflow-header">
                <h4>{workflow.name}</h4>
                <div className={`status-badge ${workflow.status}`}>
                  {workflow.status}
                </div>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${workflow.progress}%` }}
                ></div>
              </div>
              <div className="workflow-actions">
                <button className="action-button">
                  <Eye size={14} />
                  <span>View</span>
                </button>
                <button className="action-button">
                  <Download size={14} />
                  <span>Export</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderChart = (data: any) => (
    <div className="result-card chart">
      <div className="result-header">
        <BarChart3 size={20} />
        <h3>{data.title}</h3>
      </div>
      <div className="result-content">
        <div className="chart-container">
          <div className="chart-placeholder">
            <TrendingUp size={48} />
            <p>Chart visualization would be rendered here</p>
            <div className="chart-data">
              {data.data.map((item: any, index: number) => (
                <div key={index} className="data-point">
                  <span className="label">{item.month}</span>
                  <span className="value">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderFileList = (data: any[]) => (
    <div className="result-card file-list">
      <div className="result-header">
        <FileText size={20} />
        <h3>Files & Datasets</h3>
      </div>
      <div className="result-content">
        <div className="file-grid">
          {data.map((file) => (
            <div key={file.id} className="file-item">
              <div className="file-icon">
                <FileText size={20} />
              </div>
              <div className="file-info">
                <h4>{file.name}</h4>
                <p>{file.size} • {file.type}</p>
              </div>
              <div className={`status-badge ${file.status}`}>
                {file.status}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderSuggestions = (data: string[]) => (
    <div className="result-card suggestions">
      <div className="result-header">
        <AlertCircle size={20} />
        <h3>Suggestions</h3>
      </div>
      <div className="result-content">
        <div className="suggestions-list">
          {data.map((suggestion, index) => (
            <button key={index} className="suggestion-button">
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderResult = () => {
    switch (result.type) {
      case 'connector':
        return renderConnectorResult(result.data);
      case 'workflow-list':
        return renderWorkflowList(result.data);
      case 'chart':
        return renderChart(result.data);
      case 'file-list':
        return renderFileList(result.data);
      case 'suggestions':
        return renderSuggestions(result.data);
      default:
        return null;
    }
  };

  return (
    <div className="result-panel">
      {renderResult()}
    </div>
  );
};

export default ResultPanel; 