import React from 'react';
import ConnectorsSection from './ConnectorsSection';
import PipelineSection from './PipelineSection';
import DashboardSection from './DashboardSection';
import './DashboardGrid.css';

const DashboardGrid: React.FC = () => {
  return (
    <div className="dashboard-grid">
      <div className="grid-container">
        {/* Quick Stats Row */}
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <h3>Active Workflows</h3>
              <p className="stat-value">12</p>
              <p className="stat-change positive">+2 this week</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">📁</div>
            <div className="stat-content">
              <h3>Total Files</h3>
              <p className="stat-value">1,247</p>
              <p className="stat-change positive">+15 today</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">🔗</div>
            <div className="stat-content">
              <h3>Connected Sources</h3>
              <p className="stat-value">8</p>
              <p className="stat-change neutral">All healthy</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">⚡</div>
            <div className="stat-content">
              <h3>Processing Speed</h3>
              <p className="stat-value">2.3s</p>
              <p className="stat-change positive">-0.5s avg</p>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="main-grid">
          <div className="grid-item connectors-section">
            <ConnectorsSection />
          </div>
          
          <div className="grid-item pipeline-section">
            <PipelineSection />
          </div>
          
          <div className="grid-item dashboard-section">
            <DashboardSection />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardGrid; 