import React, { useState } from 'react';
import { Send, Mic, MicOff, Clock, ChevronDown } from 'lucide-react';
import './PromptBox.css';

interface PromptBoxProps {
  onSubmit: (prompt: string) => void;
  onVoiceToggle: () => void;
  isListening: boolean;
  isProcessing: boolean;
}

const PromptBox: React.FC<PromptBoxProps> = ({
  onSubmit,
  onVoiceToggle,
  isListening,
  isProcessing
}) => {
  const [prompt, setPrompt] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [promptHistory] = useState([
    'Show me my recent files',
    'Connect to Google Drive',
    'Create a new workflow',
    'Visualize test results from the past 30 days'
  ]);

  const suggestions = [
    'Show unmatched datasheets from Vendor X',
    'Connect my Google Drive',
    'Visualize test results from the past 30 days',
    'Create a new data pipeline',
    'Show workflow performance metrics'
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && !isProcessing) {
      onSubmit(prompt);
      setPrompt('');
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setPrompt(suggestion);
    setShowSuggestions(false);
  };

  const handleHistoryClick = (historyItem: string) => {
    setPrompt(historyItem);
  };

  return (
    <div className="prompt-box">
      {/* Prompt History */}
      {promptHistory.length > 0 && (
        <div className="prompt-history">
          <div className="history-header">
            <Clock size={16} />
            <span>Recent Commands</span>
          </div>
          <div className="history-chips">
            {promptHistory.map((item, index) => (
              <button
                key={index}
                className="history-chip"
                onClick={() => handleHistoryClick(item)}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Prompt Input */}
      <form onSubmit={handleSubmit} className="prompt-form">
        <div className="prompt-input-container">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask me anything about your data, workflows, or visualizations..."
            className="prompt-input"
            disabled={isProcessing}
            onFocus={() => setShowSuggestions(true)}
          />
          
          <div className="prompt-actions">
            <button
              type="button"
              className={`voice-button ${isListening ? 'listening' : ''}`}
              onClick={onVoiceToggle}
              disabled={isProcessing}
              title={isListening ? 'Stop listening' : 'Start voice input'}
            >
              {isListening ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
            
            <button
              type="submit"
              className="send-button"
              disabled={!prompt.trim() || isProcessing}
            >
              <Send size={18} />
            </button>
          </div>
        </div>

        {/* Auto-suggestions */}
        {showSuggestions && suggestions.length > 0 && (
          <div className="suggestions-dropdown">
            <div className="suggestions-header">
              <span>Suggestions</span>
              <button
                type="button"
                className="close-suggestions"
                onClick={() => setShowSuggestions(false)}
              >
                <ChevronDown size={16} />
              </button>
            </div>
            <div className="suggestions-list">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  type="button"
                  className="suggestion-item"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </form>

      {/* Processing Indicator */}
      {isProcessing && (
        <div className="processing-indicator">
          <div className="processing-spinner"></div>
          <span>AI is processing your request...</span>
        </div>
      )}
    </div>
  );
};

export default PromptBox; 