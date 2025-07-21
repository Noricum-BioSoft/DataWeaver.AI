import React, { useState, useEffect, useCallback } from 'react';
import { Lightbulb, ChevronRight, ChevronDown, ChevronUp } from 'lucide-react';
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
  const [isCollapsed, setIsCollapsed] = useState(true);

  const loadSuggestions = useCallback(async () => {
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
  }, [sessionId]);

  useEffect(() => {
    if (visible && sessionId) {
      loadSuggestions();
    }
  }, [sessionId, visible, loadSuggestions]);

  if (!visible) return null;

  return (
    <div className="data-qa-suggestions">
      <div className="suggestions-header">
        <div className="suggestions-title-section">
          <Lightbulb size={16} className="suggestions-icon" />
          <span className="suggestions-title">Suggested Questions</span>
        </div>
        <button
          className="suggestions-toggle"
          onClick={() => setIsCollapsed(!isCollapsed)}
          title={isCollapsed ? 'Show suggestions' : 'Hide suggestions'}
        >
          {isCollapsed ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
        </button>
      </div>
      
      {!isCollapsed && (
        <>
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
        </>
      )}
    </div>
  );
};

export default DataQASuggestions; 