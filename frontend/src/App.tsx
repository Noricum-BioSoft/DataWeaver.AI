import React from 'react';
import Sidebar from './components/Sidebar';
import ConnectorsSection from './components/ConnectorsSection';
import PipelineSection from './components/PipelineSection';
import DashboardSection from './components/DashboardSection';
import './App.css';

const App: React.FC = () => {
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

export default App; 