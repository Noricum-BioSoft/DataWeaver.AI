import React, { useState } from 'react';
import AIChatHeader from './AIChatHeader';
import AIChatSidebar from './AIChatSidebar';
import AIChatMain from './AIChatMain';
import './AIChatLayout.css';

const AIChatLayout: React.FC = () => {
  const [filesModalOpen, setFilesModalOpen] = useState(false);

  const handlePromptSelect = (prompt: string) => {
    // In a real implementation, this would automatically submit the prompt
    console.log('Sidebar prompt selected:', prompt);
  };

  const handleFilesClick = () => {
    setFilesModalOpen(true);
  };

  return (
    <div className="ai-chat-layout">
      <AIChatHeader />
      <div className="ai-chat-container">
        <AIChatSidebar 
          onPromptSelect={handlePromptSelect}
          onFilesClick={handleFilesClick}
        />
        <AIChatMain 
          onPromptSelect={handlePromptSelect}
          onFilesClick={handleFilesClick}
        />
      </div>
    </div>
  );
};

export default AIChatLayout; 