import React from 'react';
import Sidebar from './Sidebar';
import ConnectorsSection from './ConnectorsSection';
import PipelineSection from './PipelineSection';
import DashboardSection from './DashboardSection';

const SidebarLayout: React.FC = () => {
  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        <div className="content-wrapper">
          <ConnectorsSection />
          <PipelineSection />
          <DashboardSection />
        </div>
      </main>
    </div>
  );
};

export default SidebarLayout; 