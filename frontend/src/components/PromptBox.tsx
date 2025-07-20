import React, { useState, useCallback } from 'react';
import { Send, Mic, MicOff, Clock, ChevronDown, Upload, FileText } from 'lucide-react';
import './PromptBox.css';

interface PromptBoxProps {
  onSubmit: (prompt: string) => void;
  onVoiceToggle: () => void;
  isListening: boolean;
  isProcessing: boolean;
  onFileUpload?: (files: File[]) => Promise<void>;
}

const PromptBox: React.FC<PromptBoxProps> = ({
  onSubmit,
  onVoiceToggle,
  isListening,
  isProcessing,
  onFileUpload
}) => {
  const [prompt, setPrompt] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  const suggestions = [
    'Show unmatched datasheets from Vendor X',
    'Connect my Google Drive',
    'Visualize test results from the past 30 days',
    'Create a new data pipeline',
    'Show workflow performance metrics'
  ];

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    const csvFiles = files.filter(file => 
      file.type === 'text/csv' || file.name.toLowerCase().endsWith('.csv')
    );

    if (csvFiles.length > 0) {
      setUploadedFiles(prev => [...prev, ...csvFiles]);
      
      // Create a message about the uploaded files
      const fileNames = csvFiles.map(f => f.name).join(', ');
      const uploadMessage = `I've uploaded ${csvFiles.length} CSV file(s): ${fileNames}. What would you like me to do with these files?`;
      
      // Call the file upload handler if provided
      if (onFileUpload) {
        try {
          await onFileUpload(csvFiles);
        } catch (error) {
          console.error('Error uploading files:', error);
        }
      }
      
      // Submit the upload message
      onSubmit(uploadMessage);
    }
  }, [onSubmit, onFileUpload]);

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



  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const csvFiles = files.filter(file => 
      file.type === 'text/csv' || file.name.toLowerCase().endsWith('.csv')
    );

    if (csvFiles.length > 0) {
      setUploadedFiles(prev => [...prev, ...csvFiles]);
      
      // Create a message about the uploaded files
      const fileNames = csvFiles.map(f => f.name).join(', ');
      const uploadMessage = `I've uploaded ${csvFiles.length} CSV file(s): ${fileNames}. What would you like me to do with these files?`;
      
      // Call the file upload handler if provided
      if (onFileUpload) {
        try {
          await onFileUpload(csvFiles);
        } catch (error) {
          console.error('Error uploading files:', error);
        }
      }
      
      // Submit the upload message
      onSubmit(uploadMessage);
    }
    
    // Reset the input value so the same file can be selected again
    e.target.value = '';
  }, [onSubmit, onFileUpload]);

  return (
    <div className="prompt-box">

      {/* Uploaded Files Display */}
      {uploadedFiles.length > 0 && (
        <div className="uploaded-files-display">
          <div className="files-header">
            <FileText size={16} />
            <span>Uploaded Files ({uploadedFiles.length})</span>
          </div>
          <div className="files-list">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="file-item">
                <FileText size={14} />
                <span className="file-name">{file.name}</span>
                <span className="file-size">{formatFileSize(file.size)}</span>
                <button
                  onClick={() => removeFile(index)}
                  className="remove-file"
                  title="Remove file"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Prompt Input */}
      <form onSubmit={handleSubmit} className="prompt-form">
        <div 
          className={`prompt-input-container ${isDragOver ? 'drag-over' : ''}`}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask me anything about your data, workflows, or visualizations... (or drag CSV files here)"
            className="prompt-input"
            disabled={isProcessing}
            onFocus={() => setShowSuggestions(true)}
          />
          
          <div className="prompt-actions">
            <input
              type="file"
              multiple
              accept=".csv,text/csv"
              onChange={handleFileSelect}
              className="file-input"
              id="file-input"
              style={{ display: 'none' }}
            />
            <button
              type="button"
              className="upload-button"
              title="Upload CSV files"
              disabled={isProcessing}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <Upload size={18} />
            </button>
            
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