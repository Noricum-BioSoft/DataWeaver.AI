import React, { useState, useEffect, useCallback } from 'react';
import AIChatHeader from './AIChatHeader';
import AIChatSidebar from './AIChatSidebar';
import AIChatMain from './AIChatMain';
import ConnectorsModal from './ConnectorsModal';
import FilesModal from './FilesModal';
import WorkflowsModal from './WorkflowsModal';
import VendorsModal from './VendorsModal';
import PipelinesModal from './PipelinesModal';
import DashboardModal from './DashboardModal';
import './AIChatLayout.css';

const AIChatLayout: React.FC = () => {
  // const [filesModalOpen, setFilesModalOpen] = useState(false);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [connectorsModalOpen, setConnectorsModalOpen] = useState(false);
  const [filesModalOpen, setFilesModalOpen] = useState(false);
  const [workflowsModalOpen, setWorkflowsModalOpen] = useState(false);
  const [vendorsModalOpen, setVendorsModalOpen] = useState(false);
  const [pipelinesModalOpen, setPipelinesModalOpen] = useState(false);
  const [dashboardModalOpen, setDashboardModalOpen] = useState(false);

  const handlePromptSelect = (prompt: string) => {
    // In a real implementation, this would automatically submit the prompt
    console.log('Sidebar prompt selected:', prompt);
  };

  const handleConnectorsClick = () => {
    setConnectorsModalOpen(true);
  };

  const handleFilesClick = () => {
    setFilesModalOpen(true);
  };

  const handleWorkflowsClick = () => {
    setWorkflowsModalOpen(true);
  };

  const handleVendorsClick = () => {
    setVendorsModalOpen(true);
  };

  const handlePipelinesClick = () => {
    setPipelinesModalOpen(true);
  };

  const handleDashboardClick = () => {
    setDashboardModalOpen(true);
  };

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
    <div className={`ai-chat-layout ${sidebarVisible ? 'sidebar-visible' : 'sidebar-hidden'}`}>
      <AIChatHeader />
      <div className="ai-chat-container">
        <AIChatSidebar 
          isVisible={sidebarVisible}
          onToggle={toggleSidebar}
          onPromptSelect={handlePromptSelect}
          onFilesClick={handleFilesClick}
          onConnectorsClick={handleConnectorsClick}
          onWorkflowsClick={handleWorkflowsClick}
          onVendorsClick={handleVendorsClick}
          onPipelinesClick={handlePipelinesClick}
          onDashboardClick={handleDashboardClick}
        />
        <AIChatMain 
          onPromptSelect={handlePromptSelect}
          onFilesClick={handleFilesClick}
        />
      </div>
      
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

      {/* Connectors Modal */}
      <ConnectorsModal 
        isOpen={connectorsModalOpen}
        onClose={() => setConnectorsModalOpen(false)}
      />

      {/* Files Modal */}
      <FilesModal 
        isOpen={filesModalOpen}
        onClose={() => setFilesModalOpen(false)}
      />

      {/* Workflows Modal */}
      <WorkflowsModal 
        isOpen={workflowsModalOpen}
        onClose={() => setWorkflowsModalOpen(false)}
      />

      {/* Vendors Modal */}
      <VendorsModal 
        isOpen={vendorsModalOpen}
        onClose={() => setVendorsModalOpen(false)}
      />

      {/* Pipelines Modal */}
      <PipelinesModal 
        isOpen={pipelinesModalOpen}
        onClose={() => setPipelinesModalOpen(false)}
      />

      {/* Dashboard Modal */}
      <DashboardModal 
        isOpen={dashboardModalOpen}
        onClose={() => setDashboardModalOpen(false)}
      />
    </div>
  );
};

export default AIChatLayout; 