import React, { useState, useCallback } from 'react';
import { Send, Mic, MicOff, Upload, FileText, ChevronDown, ChevronUp, FileDown } from 'lucide-react';
import './PromptBox.css';

interface PromptBoxProps {
  onSubmit: (prompt: string) => void;
  onVoiceToggle: () => void;
  isListening: boolean;
  isProcessing: boolean;
  onFileUpload?: (files: File[]) => Promise<void>;
  generatedFiles?: Array<{
    name: string;
    size: string;
    downloadUrl: string;
    type: string;
  }>;
}

const PromptBox: React.FC<PromptBoxProps> = ({
  onSubmit,
  onVoiceToggle,
  isListening,
  isProcessing,
  onFileUpload,
  generatedFiles = []
}) => {
  const [prompt, setPrompt] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [showUploadedFiles, setShowUploadedFiles] = useState(false);
  const [showGeneratedFiles, setShowGeneratedFiles] = useState(false);

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
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
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
    }
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

      {/* Files Display Section */}
      {(uploadedFiles.length > 0 || generatedFiles.length > 0) && (
        <div className="files-display-section">
          <div className="files-grid">
            {/* Uploaded Files Column */}
            {uploadedFiles.length > 0 && (
              <div className="uploaded-files-display">
                <div className="files-header">
                  <div className="files-title-section">
                    <FileText size={16} />
                    <span>Uploaded Files ({uploadedFiles.length})</span>
                  </div>
                  <button
                    className="files-toggle"
                    onClick={() => setShowUploadedFiles(!showUploadedFiles)}
                    title={showUploadedFiles ? 'Hide files' : 'Show files'}
                  >
                    {showUploadedFiles ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </button>
                </div>
                {showUploadedFiles && (
                  <div className="files-list">
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="file-item">
                        <span className="file-name">{file.name}</span>
                        <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
                        <button
                          className="remove-file"
                          onClick={() => {
                            const newFiles = uploadedFiles.filter((_, i) => i !== index);
                            setUploadedFiles(newFiles);
                          }}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Generated Files Column */}
            {generatedFiles.length > 0 && (
              <div className="generated-files-display">
                <div className="files-header">
                  <div className="files-title-section">
                    <FileText size={16} />
                    <span>Generated Files ({generatedFiles.length})</span>
                  </div>
                  <button
                    className="files-toggle"
                    onClick={() => setShowGeneratedFiles(!showGeneratedFiles)}
                    title={showGeneratedFiles ? 'Hide files' : 'Show files'}
                  >
                    {showGeneratedFiles ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </button>
                </div>
                {showGeneratedFiles && (
                  <div className="files-list">
                    {generatedFiles.map((file, index) => (
                      <div key={index} className="file-item">
                        <span className="file-name">{file.name}</span>
                        <span className="file-size">({file.size})</span>
                        <a
                          href={file.downloadUrl}
                          download={file.name}
                          className="download-file"
                          title="Download file"
                        >
                          <FileDown size={14} />
                        </a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
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

        {/* Processing Indicator */}
        {isProcessing && (
          <div className="processing-indicator">
            <div className="processing-spinner"></div>
            <span>AI is processing your request...</span>
          </div>
        )}
      </form>
    </div>
  );
};

export default PromptBox; 