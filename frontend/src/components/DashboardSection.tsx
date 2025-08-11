import React from 'react';
import './DashboardSection.css';

const DashboardSection: React.FC = () => {
  const recentDatasets = [
    {
      id: 1,
      name: 'Sales Data Q1 2024',
      type: 'CSV',
      size: '2.3 MB',
      lastModified: '2 hours ago',
      status: 'Processed'
    },
    {
      id: 2,
      name: 'Customer Analytics',
      type: 'JSON',
      size: '1.8 MB',
      lastModified: '1 day ago',
      status: 'Processing'
    },
    {
      id: 3,
      name: 'Inventory Report',
      type: 'Excel',
      size: '4.1 MB',
      lastModified: '3 days ago',
      status: 'Processed'
    }
  ];

  // Mock chart data
  const chartData = [
    { month: 'Jan', value: 65 },
    { month: 'Feb', value: 78 },
    { month: 'Mar', value: 90 },
    { month: 'Apr', value: 85 },
    { month: 'May', value: 95 },
    { month: 'Jun', value: 88 }
  ];

  const maxValue = Math.max(...chartData.map(d => d.value));

  return (
    <div className="section">
      <div className="section-header">
        <h2>📊 Data Dashboard</h2>
        <div className="simulation-badge" title="This data is simulated for demonstration purposes. Real monitoring and analytics need to be implemented for production use.">🧪 Simulation Data</div>
      </div>
      <div className="section-content">
        <div className="dashboard-grid">
          {/* Chart Section */}
          <div className="chart-section">
            <h3>Data Processing Trends</h3>
            <div className="chart-container">
              <div className="chart-bars">
                {chartData.map((data, index) => (
                  <div key={index} className="chart-bar-container">
                    <div 
                      className="chart-bar"
                      style={{ 
                        height: `${(data.value / maxValue) * 100}%`,
                        backgroundColor: data.value === maxValue ? '#007bff' : '#e9ecef'
                      }}
                    ></div>
                    <span className="chart-label">{data.month}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Datasets Section */}
          <div className="datasets-section">
            <h3>Recent Datasets</h3>
            <div className="datasets-list">
              {recentDatasets.map(dataset => (
                <div key={dataset.id} className="dataset-item">
                  <div className="dataset-info">
                    <h4 className="dataset-name">{dataset.name}</h4>
                    <div className="dataset-meta">
                      <span className="dataset-type">{dataset.type}</span>
                      <span className="dataset-size">{dataset.size}</span>
                      <span className="dataset-time">{dataset.lastModified}</span>
                    </div>
                  </div>
                  <div className="dataset-status">
                    <span className={`status-badge ${dataset.status.toLowerCase()}`}>
                      {dataset.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="integration-note" title="Click to learn more about implementing real monitoring and analytics">
          <p>💡 <strong>Production Integration Required:</strong> This demo shows simulated data. For production use, implement custom integrations with your actual monitoring and analytics systems.</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardSection; 