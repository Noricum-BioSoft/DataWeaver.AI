import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Database, 
  BarChart3, 
  Eye,
  Calendar
} from 'lucide-react';
import { bioMatcherApi } from '../services/api';
import './DataContextPanel.css';

interface DataContextItem {
  id: string;
  name: string;
  description: string;
  created_at: string;
  metadata: any;
}

interface DataContext {
  session_id: string;
  total_data_items: number;
  uploaded_files: DataContextItem[];
  merged_datasets: DataContextItem[];
  visualizations: DataContextItem[];
  data_lineage: Record<string, { parents: string[], children: string[] }>;
}

interface DataContextPanelProps {
  sessionId: string;
}

const DataContextPanel: React.FC<DataContextPanelProps> = ({ sessionId }) => {
  const [dataContext, setDataContext] = useState<DataContext | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    uploaded_files: true,
    merged_datasets: true,
    visualizations: true
  });

  const fetchDataContext = async () => {
    try {
      setLoading(true);
      const context = await bioMatcherApi.getDataContext(sessionId);
      setDataContext(context);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data context');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (sessionId) {
      fetchDataContext();
    }
  }, [sessionId]);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getItemIcon = (type: string) => {
    switch (type) {
      case 'uploaded_file':
        return <FileText size={16} />;
      case 'merged_dataset':
        return <Database size={16} />;
      case 'visualization':
        return <BarChart3 size={16} />;
      default:
        return <FileText size={16} />;
    }
  };

  const getItemColor = (type: string) => {
    switch (type) {
      case 'uploaded_file':
        return '#3b82f6';
      case 'merged_dataset':
        return '#10b981';
      case 'visualization':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="data-context-panel">
        <div className="data-context-header">
          <h3>Data Context</h3>
        </div>
        <div className="data-context-loading">
          Loading data context...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="data-context-panel">
        <div className="data-context-header">
          <h3>Data Context</h3>
        </div>
        <div className="data-context-error">
          Error: {error}
        </div>
      </div>
    );
  }

  if (!dataContext) {
    return (
      <div className="data-context-panel">
        <div className="data-context-header">
          <h3>Data Context</h3>
        </div>
        <div className="data-context-empty">
          No data context available
        </div>
      </div>
    );
  }

  return (
    <div className="data-context-panel">
      <div className="data-context-header">
        <h3>Data Context</h3>
        <div className="data-context-summary">
          <span>{dataContext.total_data_items} items</span>
        </div>
      </div>

      <div className="data-context-content">
        {/* Uploaded Files Section */}
        <div className="data-context-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('uploaded_files')}
          >
            <div className="section-title">
              <FileText size={20} />
              <span>Uploaded Files ({dataContext.uploaded_files.length})</span>
            </div>
            <span className="section-toggle">
              {expandedSections.uploaded_files ? '−' : '+'}
            </span>
          </div>
          
          {expandedSections.uploaded_files && (
            <div className="section-content">
              {dataContext.uploaded_files.length === 0 ? (
                <div className="empty-section">No uploaded files</div>
              ) : (
                dataContext.uploaded_files.map((item) => (
                  <div key={item.id} className="context-item">
                    <div className="item-header">
                      <div className="item-icon" style={{ color: getItemColor('uploaded_file') }}>
                        {getItemIcon('uploaded_file')}
                      </div>
                      <div className="item-info">
                        <div className="item-name">{item.name}</div>
                        <div className="item-description">{item.description}</div>
                        <div className="item-meta">
                          <Calendar size={12} />
                          <span>{formatDate(item.created_at)}</span>
                        </div>
                      </div>
                    </div>
                    {item.metadata && (
                      <div className="item-metadata">
                        <div className="metadata-row">
                          <span>Columns:</span>
                          <span>{item.metadata.columns?.length || 0}</span>
                        </div>
                        <div className="metadata-row">
                          <span>Rows:</span>
                          <span>{item.metadata.row_count || 0}</span>
                        </div>
                        <div className="metadata-row">
                          <span>Numeric Columns:</span>
                          <span>{item.metadata.numeric_columns?.length || 0}</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Merged Datasets Section */}
        <div className="data-context-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('merged_datasets')}
          >
            <div className="section-title">
              <Database size={20} />
              <span>Merged Datasets ({dataContext.merged_datasets.length})</span>
            </div>
            <span className="section-toggle">
              {expandedSections.merged_datasets ? '−' : '+'}
            </span>
          </div>
          
          {expandedSections.merged_datasets && (
            <div className="section-content">
              {dataContext.merged_datasets.length === 0 ? (
                <div className="empty-section">No merged datasets</div>
              ) : (
                dataContext.merged_datasets.map((item) => (
                  <div key={item.id} className="context-item">
                    <div className="item-header">
                      <div className="item-icon" style={{ color: getItemColor('merged_dataset') }}>
                        {getItemIcon('merged_dataset')}
                      </div>
                      <div className="item-info">
                        <div className="item-name">{item.name}</div>
                        <div className="item-description">{item.description}</div>
                        <div className="item-meta">
                          <Calendar size={12} />
                          <span>{formatDate(item.created_at)}</span>
                        </div>
                      </div>
                    </div>
                    {item.metadata && (
                      <div className="item-metadata">
                        <div className="metadata-row">
                          <span>Total Rows:</span>
                          <span>{item.metadata.total_rows || 0}</span>
                        </div>
                        <div className="metadata-row">
                          <span>Matched Rows:</span>
                          <span>{item.metadata.matched_rows || 0}</span>
                        </div>
                        <div className="metadata-row">
                          <span>Columns:</span>
                          <span>{item.metadata.columns?.length || 0}</span>
                        </div>
                        <div className="metadata-row">
                          <span>Merge Column:</span>
                          <span>{item.metadata.merge_column || 'N/A'}</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Visualizations Section */}
        <div className="data-context-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('visualizations')}
          >
            <div className="section-title">
              <BarChart3 size={20} />
              <span>Visualizations ({dataContext.visualizations.length})</span>
            </div>
            <span className="section-toggle">
              {expandedSections.visualizations ? '−' : '+'}
            </span>
          </div>
          
          {expandedSections.visualizations && (
            <div className="section-content">
              {dataContext.visualizations.length === 0 ? (
                <div className="empty-section">No visualizations</div>
              ) : (
                dataContext.visualizations.map((item) => (
                  <div key={item.id} className="context-item">
                    <div className="item-header">
                      <div className="item-icon" style={{ color: getItemColor('visualization') }}>
                        {getItemIcon('visualization')}
                      </div>
                      <div className="item-info">
                        <div className="item-name">{item.name}</div>
                        <div className="item-description">{item.description}</div>
                        <div className="item-meta">
                          <Calendar size={12} />
                          <span>{formatDate(item.created_at)}</span>
                        </div>
                      </div>
                    </div>
                    {item.metadata && (
                      <div className="item-metadata">
                        <div className="metadata-row">
                          <span>Plot Type:</span>
                          <span>{item.metadata.plot_type || 'N/A'}</span>
                        </div>
                        <div className="metadata-row">
                          <span>Data Shape:</span>
                          <span>{item.metadata.data_shape?.join(' × ') || 'N/A'}</span>
                        </div>
                        {item.metadata.x_column && (
                          <div className="metadata-row">
                            <span>X Column:</span>
                            <span>{item.metadata.x_column}</span>
                          </div>
                        )}
                        {item.metadata.y_column && (
                          <div className="metadata-row">
                            <span>Y Column:</span>
                            <span>{item.metadata.y_column}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataContextPanel; 