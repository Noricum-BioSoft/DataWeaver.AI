import React, { useState, useEffect } from 'react';
import { Lightbulb, ChevronRight } from 'lucide-react';
import { dataQaApi } from '../services/api';
import './DataQASuggestions.css';

interface DataQASuggestionsProps {
  sessionId: string;
  onSuggestionClick: (suggestion: string) => void;
  visible?: boolean;
}

const DataQASuggestions: React.FC<DataQASuggestionsProps> = ({
  sessionId,
  onSuggestionClick,
  visible = true
}) => {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (visible && sessionId) {
      loadSuggestions();
    }
  }, [sessionId, visible]);

  const loadSuggestions = async () => {
    if (!sessionId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await dataQaApi.getQuestionSuggestions(sessionId);
      setSuggestions(result.suggestions || []);
    } catch (err) {
      setError('Failed to load suggestions');
      console.error('Error loading suggestions:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!visible) return null;

  return (
    <div className="data-qa-suggestions">
      <div className="suggestions-header">
        <Lightbulb size={16} className="suggestions-icon" />
        <span className="suggestions-title">Suggested Questions</span>
      </div>
      
      {loading && (
        <div className="suggestions-loading">
          <div className="loading-dots">
            <div className="loading-dot"></div>
            <div className="loading-dot"></div>
            <div className="loading-dot"></div>
          </div>
        </div>
      )}
      
      {error && (
        <div className="suggestions-error">
          <span>{error}</span>
          <button 
            className="retry-button"
            onClick={loadSuggestions}
          >
            Retry
          </button>
        </div>
      )}
      
      {!loading && !error && suggestions.length > 0 && (
        <div className="suggestions-list">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              className="suggestion-item"
              onClick={() => onSuggestionClick(suggestion)}
            >
              <span className="suggestion-text">{suggestion}</span>
              <ChevronRight size={14} className="suggestion-arrow" />
            </button>
          ))}
        </div>
      )}
      
      {!loading && !error && suggestions.length === 0 && (
        <div className="suggestions-empty">
          <span>No suggestions available</span>
        </div>
      )}
    </div>
  );
};

export default DataQASuggestions; 