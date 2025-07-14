import React, { useState, useRef, useEffect } from 'react';
import PromptBox from './PromptBox';
import ChatHistory from './ChatHistory';
import './AIChatMain.css';

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  result?: any;
}

interface AIChatMainProps {
  onPromptSelect?: (prompt: string) => void;
}

const AIChatMain: React.FC<AIChatMainProps> = ({ onPromptSelect }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'ai',
      content: 'Hello! I\'m your AI assistant. I can help you with data sources, workflows, and visualizations. What would you like to do?',
      timestamp: new Date(),
      result: null
    }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handlePromptSubmit = async (prompt: string) => {
    if (!prompt.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: prompt,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);

    // Simulate AI processing
    setTimeout(() => {
      const aiResponse = generateAIResponse(prompt);
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: aiResponse.message,
        timestamp: new Date(),
        result: aiResponse.result
      };

      setMessages(prev => [...prev, aiMessage]);
      setIsProcessing(false);
    }, 1500);
  };

  const generateAIResponse = (prompt: string) => {
    const lowerPrompt = prompt.toLowerCase();
    
    // Simple rules-based response system
    if (lowerPrompt.includes('connect') && lowerPrompt.includes('google')) {
      return {
        message: 'I\'ll help you connect to Google Drive. Let me check your current connections and set up the integration.',
        result: {
          type: 'connector',
          data: {
            provider: 'Google Drive',
            status: 'connecting',
            steps: ['Authenticating...', 'Setting up permissions...', 'Testing connection...']
          }
        }
      };
    }

    if (lowerPrompt.includes('workflow') || lowerPrompt.includes('pipeline')) {
      return {
        message: 'Here are your current workflows and pipelines. I can help you create new ones or modify existing ones.',
        result: {
          type: 'workflow-list',
          data: [
            { id: 1, name: 'Data Processing Pipeline', status: 'running', progress: 75 },
            { id: 2, name: 'Vendor Data Sync', status: 'completed', progress: 100 },
            { id: 3, name: 'Analytics Dashboard', status: 'pending', progress: 0 }
          ]
        }
      };
    }

    if (lowerPrompt.includes('visualize') || lowerPrompt.includes('chart')) {
      return {
        message: 'I\'ll create a visualization for you. Here\'s what I found based on your request.',
        result: {
          type: 'chart',
          data: {
            type: 'line',
            title: 'Data Processing Trends',
            data: [
              { month: 'Jan', value: 65 },
              { month: 'Feb', value: 78 },
              { month: 'Mar', value: 90 },
              { month: 'Apr', value: 85 },
              { month: 'May', value: 95 },
              { month: 'Jun', value: 88 }
            ]
          }
        }
      };
    }

    if (lowerPrompt.includes('file') || lowerPrompt.includes('dataset')) {
      return {
        message: 'Here are your recent files and datasets. I can help you process or analyze any of them.',
        result: {
          type: 'file-list',
          data: [
            { id: 1, name: 'Sales Data Q1 2024.csv', size: '2.3 MB', type: 'CSV', status: 'processed' },
            { id: 2, name: 'Customer Analytics.json', size: '1.8 MB', type: 'JSON', status: 'processing' },
            { id: 3, name: 'Inventory Report.xlsx', size: '4.1 MB', type: 'Excel', status: 'processed' }
          ]
        }
      };
    }

    // Default response
    return {
      message: 'I understand you want to work with your data. Let me help you with that. What specific action would you like me to take?',
      result: {
        type: 'suggestions',
        data: [
          'Show me my recent files',
          'Connect to a new data source',
          'Create a new workflow',
          'Generate a visualization'
        ]
      }
    };
  };

  const handleVoiceToggle = () => {
    setIsListening(!isListening);
    // TODO: Implement voice input
  };

  return (
    <main className="ai-chat-main">
      <div className="chat-container">
        <ChatHistory messages={messages} isProcessing={isProcessing} />
        <div ref={messagesEndRef} />
      </div>
      
      <div className="prompt-section">
        <PromptBox 
          onSubmit={handlePromptSubmit}
          onVoiceToggle={handleVoiceToggle}
          isListening={isListening}
          isProcessing={isProcessing}
        />
      </div>
    </main>
  );
};

export default AIChatMain; 