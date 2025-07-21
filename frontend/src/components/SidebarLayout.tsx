import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './Sidebar';
import ConnectorsSection from './ConnectorsSection';
import PipelineSection from './PipelineSection';
import DashboardSection from './DashboardSection';
import './SidebarLayout.css';

const SidebarLayout: React.FC = () => {
  const [sidebarVisible, setSidebarVisible] = useState(true);

  const toggleSidebar = useCallback(() => {
    setSidebarVisible(prev => !prev);
  }, []);

  // Keyboard shortcut: Ctrl/Cmd + B to toggle sidebar
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'b') {
        event.preventDefault();
        toggleSidebar();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggleSidebar]);

  return (
    <div className={`app-container ${sidebarVisible ? 'sidebar-visible' : 'sidebar-hidden'}`}>
      <Sidebar isVisible={sidebarVisible} onToggle={toggleSidebar} />
      <main className="main-content">
        <div className="content-wrapper">
          <ConnectorsSection />
          <PipelineSection />
          <DashboardSection />
        </div>
      </main>
      
      {/* Floating toggle button when sidebar is hidden */}
      {!sidebarVisible && (
        <button 
          className="floating-toggle-btn"
          onClick={toggleSidebar}
          aria-label="Show sidebar"
          title="Show sidebar (Ctrl+B)"
        >
          <svg 
            width="20" 
            height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <path d="M9 18l-6-6 6-6"/>
          </svg>
        </button>
      )}
    </div>
  );
};

export default SidebarLayout; 