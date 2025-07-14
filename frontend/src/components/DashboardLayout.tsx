import React from 'react';
import DashboardHeader from './DashboardHeader';
import DashboardGrid from './DashboardGrid';
import './DashboardLayout.css';

const DashboardLayout: React.FC = () => {
  return (
    <div className="dashboard-layout">
      <DashboardHeader />
      <DashboardGrid />
    </div>
  );
};

export default DashboardLayout; 