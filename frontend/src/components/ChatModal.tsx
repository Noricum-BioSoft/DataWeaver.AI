import React, { useState } from 'react';
import './ChatModal.css';

interface ChatModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatModal: React.FC<ChatModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'new' | 'existing'>('new');
  const [newChatTitle, setNewChatTitle] = useState('');

  const existingChats = [
    { id: 1, title: 'Protein Analysis Discussion', lastMessage: 'Can you analyze the sequence data?', timestamp: '2 hours ago', unread: 0 },
    { id: 2, title: 'Data Merge Questions', lastMessage: 'How do I combine these datasets?', timestamp: '1 day ago', unread: 2 },
    { id: 3, title: 'Workflow Optimization', lastMessage: 'The pipeline is running slowly...', timestamp: '3 days ago', unread: 0 }
  ];

  const handleStartNewChat = () => {
    if (newChatTitle.trim()) {
      console.log('Starting new chat:', newChatTitle);
      // TODO: Implement new chat creation
      setNewChatTitle('');
      onClose();
    }
  };

  const handleOpenChat = (chatId: number) => {
    console.log('Opening chat:', chatId);
    // TODO: Implement chat opening
    onClose();
  };

  const handleDeleteChat = (chatId: number) => {
    console.log('Deleting chat:', chatId);
    // TODO: Implement chat deletion
  };

  if (!isOpen) return null;

  return (
    <div className="chat-modal-overlay" onClick={onClose}>
      <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>💬 Chat Management</h2>
          <div className="simulation-badge" title="This data is simulated for demonstration purposes. Real chat management needs to be implemented for production use.">🧪 Simulation Data</div>
          <button className="modal-close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div className="modal-content">
          {/* Tab Navigation */}
          <div className="chat-tabs">
            <button 
              className={`tab-button ${activeTab === 'new' ? 'active' : ''}`}
              onClick={() => setActiveTab('new')}
            >
              New Chat
            </button>
            <button 
              className={`tab-button ${activeTab === 'existing' ? 'active' : ''}`}
              onClick={() => setActiveTab('existing')}
            >
              Existing Chats ({existingChats.length})
            </button>
          </div>

          {/* New Chat Tab */}
          {activeTab === 'new' && (
            <div className="new-chat-section">
              <div className="input-group">
                <label htmlFor="chat-title">Chat Title (Optional)</label>
                <input
                  id="chat-title"
                  type="text"
                  placeholder="Enter a title for your new chat..."
                  value={newChatTitle}
                  onChange={(e) => setNewChatTitle(e.target.value)}
                  className="chat-title-input"
                />
              </div>
              <button 
                className="start-chat-btn"
                onClick={handleStartNewChat}
                disabled={!newChatTitle.trim()}
              >
                Start New Chat
              </button>
              <div className="quick-start-options">
                <h4>Quick Start Templates</h4>
                <div className="template-buttons">
                  <button 
                    className="template-btn"
                    onClick={() => setNewChatTitle('Data Analysis Chat')}
                  >
                    📊 Data Analysis
                  </button>
                  <button 
                    className="template-btn"
                    onClick={() => setNewChatTitle('Workflow Discussion')}
                  >
                    ⚙️ Workflow Discussion
                  </button>
                  <button 
                    className="template-btn"
                    onClick={() => setNewChatTitle('File Processing Help')}
                  >
                    📁 File Processing
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Existing Chats Tab */}
          {activeTab === 'existing' && (
            <div className="existing-chats-section">
              <div className="chats-list">
                {existingChats.map(chat => (
                  <div key={chat.id} className="chat-item">
                    <div className="chat-info" onClick={() => handleOpenChat(chat.id)}>
                      <h3 className="chat-title">{chat.title}</h3>
                      <p className="chat-preview">{chat.lastMessage}</p>
                      <div className="chat-meta">
                        <span className="chat-time">{chat.timestamp}</span>
                        {chat.unread > 0 && (
                          <span className="unread-badge">{chat.unread}</span>
                        )}
                      </div>
                    </div>
                    <div className="chat-actions">
                      <button 
                        className="action-btn open-btn"
                        onClick={() => handleOpenChat(chat.id)}
                        title="Open this chat"
                      >
                        Open
                      </button>
                      <button 
                        className="action-btn delete-btn"
                        onClick={() => handleDeleteChat(chat.id)}
                        title="Delete this chat"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="integration-note" title="Click to learn more about implementing real chat management">
          <p>💡 <strong>Production Integration Required:</strong> This demo shows simulated data. For production use, implement custom integrations with your actual chat and conversation management systems.</p>
        </div>
      </div>
    </div>
  );
};

export default ChatModal;
