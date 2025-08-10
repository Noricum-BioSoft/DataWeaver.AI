import React, { useState, useEffect, useCallback } from 'react';
import AIChatHeader from './AIChatHeader';
import AIChatSidebar from './AIChatSidebar';
import AIChatMain from './AIChatMain';
import ConnectorsModal from './ConnectorsModal';
import './AIChatLayout.css';

const AIChatLayout: React.FC = () => {
  // const [filesModalOpen, setFilesModalOpen] = useState(false);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [connectorsModalOpen, setConnectorsModalOpen] = useState(false);

  const handlePromptSelect = (prompt: string) => {
    // In a real implementation, this would automatically submit the prompt
    console.log('Sidebar prompt selected:', prompt);
  };

  const handleFilesClick = () => {
    // TODO: Implement files modal functionality
    console.log('Files clicked');
  };

  const handleConnectorsClick = () => {
    setConnectorsModalOpen(true);
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
    </div>
  );
};

export default AIChatLayout; 