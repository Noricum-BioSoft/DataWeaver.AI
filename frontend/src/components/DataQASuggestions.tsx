import React from 'react';

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
  if (!visible) return null;

  return (
    <div className="data-qa-suggestions">
      <div className="suggestions-header">
        <span className="suggestions-title">Suggested Questions</span>
      </div>
      <div className="suggestions-list">
        <button
          className="suggestion-item"
          onClick={() => onSuggestionClick("Show me a summary of the data")}
        >
          📊 Show me a summary of the data
        </button>
        <button
          className="suggestion-item"
          onClick={() => onSuggestionClick("Create a scatter plot of the data")}
        >
          📈 Create a scatter plot of the data
        </button>
        <button
          className="suggestion-item"
          onClick={() => onSuggestionClick("What are the main trends in the data?")}
        >
          🔍 What are the main trends in the data?
        </button>
        <button
          className="suggestion-item"
          onClick={() => onSuggestionClick("Merge these datasets together")}
        >
          🔄 Merge these datasets together
        </button>
      </div>
    </div>
  );
};

export default DataQASuggestions;
