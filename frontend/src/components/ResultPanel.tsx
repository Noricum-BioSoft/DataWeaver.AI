import React, { useEffect } from 'react';
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
  Eye,
  Database,
  FileDown
} from 'lucide-react';
import Plot from 'react-plotly.js';
import { bioMatcherApi } from '../services/api';
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

  const renderMergedData = (data: any) => {
    return (
      <div className="result-card merged-data">
        <div className="result-header">
          <Database size={20} />
          <h3>Merged CSV Data</h3>
          <div className="merge-stats">
            <span className="stat-item">
              <strong>{data.totalRows}</strong> total rows
            </span>
            <span className="stat-item">
              <strong>{data.matchedRows}</strong> matched
            </span>
            <span className="stat-item">
              <strong>{data.unmatchedRows}</strong> unmatched
            </span>
          </div>
        </div>
        <div className="result-content">
          <div className="merged-data-preview">
            <div className="data-table">
              <table>
                <thead>
                  <tr>
                    {data.headers.map((header: string, index: number) => (
                      <th key={index}>{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.sampleRows.map((row: any[], rowIndex: number) => (
                    <tr key={rowIndex}>
                      {row.map((cell: any, cellIndex: number) => (
                        <td key={cellIndex}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {data.sampleRows.length < data.totalRows && (
              <p className="table-note">
                Showing first {data.sampleRows.length} rows of {data.totalRows} total rows
              </p>
            )}
          </div>
          <div className="merged-data-actions">
            <a
              href={data.downloadUrl}
              download={data.fileName}
              className="download-button"
            >
              <FileDown size={16} />
              <span>Download Merged CSV</span>
            </a>
          </div>
        </div>
      </div>
    );
  };

  const VisualizationResult: React.FC<{ data: any }> = ({ data }) => {
    const [plotData, setPlotData] = React.useState<any>(null);
    const [layout, setLayout] = React.useState<any>(null);
    
    useEffect(() => {
      if (data.plotJson || data.plotData) {
        try {
          const parsedData = JSON.parse(data.plotJson || data.plotData);
          setPlotData(parsedData.data);
          setLayout({
            ...parsedData.layout,
            autosize: true,
            margin: { l: 50, r: 50, t: 50, b: 50 }
          });
        } catch (error) {
          console.error('Error parsing Plotly data:', error);
        }
      }
    }, [data.plotJson, data.plotData]);

    return (
      <div className="result-card visualization-result">
        <div className="result-header">
          <BarChart3 size={20} />
          <h3>Data Visualization</h3>
          <div className="visualization-info">
            <span className="plot-type">{data.plotType} plot</span>
            <span className="data-info">{data.dataShape[0]} rows, {data.dataShape[1]} columns</span>
          </div>
        </div>
        <div className="result-content">
          <div className="visualization-container">
            {plotData && layout ? (
              <Plot
                data={plotData}
                layout={layout}
                config={{
                  displayModeBar: true,
                  modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                  displaylogo: false,
                  responsive: true
                }}
                style={{ width: '100%', height: '500px' }}
                useResizeHandler={true}
              />
            ) : (
              <div className="plot-loading">
                <BarChart3 size={48} />
                <p>Loading visualization...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderVisualizationResult = (data: any) => {
    return <VisualizationResult data={data} />;
  };

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

  const renderAnalysisResult = (data: any) => {
    return (
      <div className="result-card analysis-result">
        <div className="result-header">
          <Database size={20} />
          <h3>Data Analysis</h3>
          <div className="analysis-info">
            <span className="dataset-size">{data.dataset_info.total_rows} rows, {data.dataset_info.total_columns} columns</span>
            <span className="quality-score">{data.quality_analysis.total_issues} quality issues</span>
          </div>
        </div>
        <div className="result-content">
          {/* Dataset Information */}
          <div className="analysis-section">
            <h4>Dataset Overview</h4>
            <div className="dataset-stats">
              <div className="stat-item">
                <span className="stat-label">Total Rows:</span>
                <span className="stat-value">{data.dataset_info.total_rows}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Total Columns:</span>
                <span className="stat-value">{data.dataset_info.total_columns}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Numeric Columns:</span>
                <span className="stat-value">{data.dataset_info.numeric_columns.length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Categorical Columns:</span>
                <span className="stat-value">{data.dataset_info.categorical_columns.length}</span>
              </div>
            </div>
          </div>

          {/* Quality Analysis */}
          {data.quality_analysis.total_issues > 0 && (
            <div className="analysis-section">
              <h4>Data Quality Issues</h4>
              <div className="quality-issues">
                {data.quality_analysis.issues.map((issue: any, index: number) => (
                  <div key={index} className={`quality-issue ${issue.severity}`}>
                    <div className="issue-header">
                      <span className="issue-type">{issue.type.replace('_', ' ').toUpperCase()}</span>
                      <span className={`issue-severity ${issue.severity}`}>{issue.severity}</span>
                    </div>
                    <div className="issue-details">
                      {issue.column && <span>Column: {issue.column}</span>}
                      <span>Count: {issue.count}</span>
                      <span>Percentage: {issue.percentage.toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Statistical Analysis */}
          {data.statistical_analysis.numeric_columns && data.statistical_analysis.numeric_columns.length > 0 && (
            <div className="analysis-section">
              <h4>Statistical Summary</h4>
              <div className="statistical-summary">
                {data.statistical_analysis.numeric_columns.slice(0, 3).map((col: string) => (
                  <div key={col} className="stat-column">
                    <h5>{col}</h5>
                    <div className="stat-values">
                      <span>Mean: {data.statistical_analysis.statistics[col].mean.toFixed(2)}</span>
                      <span>Std: {data.statistical_analysis.statistics[col].std.toFixed(2)}</span>
                      <span>Min: {data.statistical_analysis.statistics[col].min.toFixed(2)}</span>
                      <span>Max: {data.statistical_analysis.statistics[col].max.toFixed(2)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Correlation Analysis */}
          {data.correlation_analysis.total_correlations > 0 && (
            <div className="analysis-section">
              <h4>Strong Correlations</h4>
              <div className="correlations">
                {data.correlation_analysis.strong_correlations.slice(0, 5).map((corr: any, index: number) => (
                  <div key={index} className="correlation-item">
                    <span className="correlation-pair">{corr.column1} ↔ {corr.column2}</span>
                    <span className={`correlation-value ${corr.strength}`}>
                      {corr.correlation.toFixed(3)} ({corr.strength})
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {data.recommendations.length > 0 && (
            <div className="analysis-section">
              <h4>Recommendations</h4>
              <div className="recommendations">
                {data.recommendations.map((rec: any, index: number) => (
                  <div key={index} className={`recommendation ${rec.priority}`}>
                    <div className="recommendation-header">
                      <span className="recommendation-title">{rec.title}</span>
                      <span className={`recommendation-priority ${rec.priority}`}>{rec.priority}</span>
                    </div>
                    <p className="recommendation-description">{rec.description}</p>
                    <p className="recommendation-action">{rec.action}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderQueryResult = (data: any) => {
    const handleDownload = async () => {
      try {
        const blob = await bioMatcherApi.downloadFilteredData(data.sessionId);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `filtered_data_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error downloading filtered data:', error);
      }
    };

    const hasResults = data.filteredShape[0] > 0;

    return (
      <div className="result-card query-result">
        <div className="result-header">
          <Database size={20} />
          <h3>Query Results</h3>
          <div className="query-stats">
            <span className="stat-item">
              <strong>{data.filteredShape[0]}</strong> filtered rows
            </span>
            <span className="stat-item">
              <strong>{data.rowsRemoved}</strong> rows removed
            </span>
            <span className="stat-item">
              <strong>{data.filteredShape[1]}</strong> columns
            </span>
          </div>
        </div>
        <div className="result-content">
          <div className="query-info">
            <p><strong>Query:</strong> {data.query}</p>
            <p><strong>Original data:</strong> {data.originalShape[0]} rows × {data.originalShape[1]} columns</p>
            <p><strong>Filtered data:</strong> {data.filteredShape[0]} rows × {data.filteredShape[1]} columns</p>
          </div>
          
          {hasResults ? (
            // Show dataframe when there are results
            <div className="filtered-data-preview">
              <h4>Filtered Data Results:</h4>
              <div className="data-table">
                <table>
                  <thead>
                    <tr>
                      {data.columns.map((column: string, index: number) => (
                        <th key={index}>{column}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.sampleRows.map((row: any, rowIndex: number) => (
                      <tr key={rowIndex}>
                        {Object.values(row).map((cell: any, cellIndex: number) => (
                          <td key={cellIndex}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {data.sampleRows.length < data.filteredShape[0] && (
                <p className="table-note">
                  Showing first {data.sampleRows.length} rows of {data.filteredShape[0]} filtered rows
                </p>
              )}
              <div className="filtered-data-actions">
                <button
                  onClick={handleDownload}
                  className="download-button"
                >
                  <FileDown size={16} />
                  <span>Download Filtered CSV</span>
                </button>
              </div>
            </div>
          ) : (
            // Show no results message when there are no matches
            <div className="no-results-message">
              <div className="no-results-icon">
                <AlertCircle size={48} />
              </div>
              <h4>No matching results found</h4>
              <p>Your query returned no rows that match the specified criteria.</p>
              <div className="query-suggestions">
                <p><strong>Try adjusting your query:</strong></p>
                <ul>
                  <li>Check spelling of column names and values</li>
                  <li>Use different comparison operators (&gt;, &lt;, &gt;=, &lt;=, =)</li>
                  <li>Try broader conditions or different values</li>
                  <li>Use OR instead of AND for more inclusive results</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderResult = () => {
    if (!result) {
      return null;
    }
    
    switch (result.type) {
      case 'connector':
        return renderConnectorResult(result.data);
      case 'merged-data':
        return renderMergedData(result.data);
      case 'visualization':
        return renderVisualizationResult(result.data);
      case 'visualization-result':
        return renderVisualizationResult(result.data);
      case 'workflow-list':
        return renderWorkflowList(result.data);
      case 'chart':
        return renderChart(result.data);
      case 'file-list':
        return renderFileList(result.data);
      case 'suggestions':
        return renderSuggestions(result.data);
      case 'analysis-result':
        return renderAnalysisResult(result.data);
      case 'query':
        return renderQueryResult(result.data);
      case 'test-merged-data':
        return renderMergedData({
          totalRows: 100,
          matchedRows: 85,
          unmatchedRows: 15,
          headers: ['ID', 'Name', 'Value', 'Category'],
          sampleRows: [
            ['1', 'Item A', '10.5', 'Category 1'],
            ['2', 'Item B', '20.3', 'Category 2'],
            ['3', 'Item C', '15.7', 'Category 1'],
            ['4', 'Item D', '8.9', 'Category 3'],
            ['5', 'Item E', '12.1', 'Category 2']
          ],
          downloadUrl: '#',
          fileName: 'test_merged.csv'
        });
      case 'general-chat':
        // General chat results don't need special rendering, just return null
        return null;
      case 'plot-explanation':
        // Plot explanation results don't need special rendering, just return null
        return null;
      case 'session-cleared':
        // Session cleared results don't need special rendering, just return null
        return null;
      default:
        // For truly unknown types, just return null instead of debug display
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