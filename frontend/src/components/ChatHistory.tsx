import React from 'react';
import { User, Bot, Clock } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import ResultPanel from './ResultPanel';
import './ChatHistory.css';

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  result?: any;
}

interface ChatHistoryProps {
  messages: ChatMessage[];
  isProcessing: boolean;
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ messages, isProcessing }) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-history">
      {messages.map((message) => (
        <div key={message.id} className={`message-container ${message.type}`}>
          <div className="message-avatar">
            {message.type === 'user' ? (
              <User size={20} className="user-icon" />
            ) : (
              <Bot size={20} className="ai-icon" />
            )}
          </div>
          
          <div className="message-content">
            <div className="message-bubble">
              <div className="message-text">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
              <div className="message-time">
                <Clock size={12} />
                <span>{formatTime(message.timestamp)}</span>
              </div>
            </div>
            
            {message.result && (
              <ResultPanel result={message.result} />
            )}
          </div>
        </div>
      ))}
      
      {isProcessing && (
        <div className="message-container ai">
          <div className="message-avatar">
            <Bot size={20} className="ai-icon" />
          </div>
          <div className="message-content">
            <div className="message-bubble processing">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatHistory; 