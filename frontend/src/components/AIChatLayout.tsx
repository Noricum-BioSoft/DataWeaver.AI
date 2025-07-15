import React from 'react';
import AIChatHeader from './AIChatHeader';
import AIChatSidebar from './AIChatSidebar';
import AIChatMain from './AIChatMain';
import './AIChatLayout.css';

const AIChatLayout: React.FC = () => {
  const handlePromptSelect = (prompt: string) => {
    // In a real implementation, this would automatically submit the prompt
    console.log('Sidebar prompt selected:', prompt);
  };

  return (
    <div className="ai-chat-layout">
      <AIChatHeader />
      <div className="ai-chat-container">
        <AIChatSidebar onPromptSelect={handlePromptSelect} />
        <AIChatMain onPromptSelect={handlePromptSelect} />
      </div>
    </div>
  );
};

export default AIChatLayout; 