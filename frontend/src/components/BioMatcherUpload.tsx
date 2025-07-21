import React, { useState, useCallback } from 'react';
import { Upload, FileText, Database, CheckCircle, AlertCircle } from 'lucide-react';
import { bioMatcherApi } from '../services/api';
import DataContextPanel from './DataContextPanel';
import './BioMatcherUpload.css';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  file: File;
}

interface MergedData {
  headers: string[];
  rows: any[][];
  totalRows: number;
  matchedRows: number;
  unmatchedRows: number;
}

const BioMatcherUpload: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [mergedData, setMergedData] = useState<MergedData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

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

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    setError(null);
    setSuccess(null);

    const files = Array.from(e.dataTransfer.files);
    const csvFiles = files.filter(file => 
      file.type === 'text/csv' || file.name.toLowerCase().endsWith('.csv')
    );

    if (csvFiles.length === 0) {
      setError('Please upload CSV files only');
      return;
    }

    if (csvFiles.length > 2) {
      setError('Please upload maximum 2 CSV files');
      return;
    }

    const newFiles: UploadedFile[] = csvFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      file: file
    }));

    setUploadedFiles(newFiles);
    setSuccess(`Uploaded ${newFiles.length} file(s)`);

    // Auto-merge if 2 files are uploaded
    if (newFiles.length === 2) {
      handleMerge(newFiles);
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const csvFiles = files.filter(file => 
      file.type === 'text/csv' || file.name.toLowerCase().endsWith('.csv')
    );

    if (csvFiles.length === 0) {
      setError('Please select CSV files only');
      return;
    }

    if (csvFiles.length > 2) {
      setError('Please select maximum 2 CSV files');
      return;
    }

    const newFiles: UploadedFile[] = csvFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      file: file
    }));

    setUploadedFiles(newFiles);
    setSuccess(`Uploaded ${newFiles.length} file(s)`);

    // Auto-merge if 2 or more files are selected
    if (newFiles.length >= 2) {
      handleMerge(newFiles);
    }
  }, []);

  const handleMerge = async (files: UploadedFile[]) => {
    if (files.length < 2) {
      setError('Please upload at least 2 CSV files to merge');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setSuccess(null);

    try {
      // Create session if not exists
      if (!sessionId) {
        const sessionResponse = await bioMatcherApi.createWorkflowSession();
        setSessionId(sessionResponse.session_id);
      }

      const formData = new FormData();
      // Add all files to the files array
      files.forEach((file) => {
        formData.append('files', file.file);
      });
      
      // Add session ID if available
      if (sessionId) {
        formData.append('session_id', sessionId);
      }

      const result = await bioMatcherApi.mergeFiles(formData);
      setMergedData(result);
      setSuccess(`Successfully merged ${result.matchedRows} rows with ${result.unmatchedRows} unmatched`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to merge files');
    } finally {
      setIsProcessing(false);
    }
  };

  const removeFile = (id: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== id));
    setMergedData(null);
    setError(null);
    setSuccess(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleUploadAreaClick = useCallback(() => {
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
  }, []);

  return (
    <div className="bio-matcher-upload">
      <div className="upload-header">
        <h2>Bio-Matcher File Upload</h2>
        <p>Drag and drop 2 or more CSV files to automatically merge them</p>
      </div>

      {/* Drag & Drop Area */}
      <div
        className={`upload-area ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleUploadAreaClick}
      >
        <input
          type="file"
          multiple
          accept=".csv,text/csv"
          onChange={handleFileSelect}
          className="file-input"
          id="file-input"
        />
        
        <label htmlFor="file-input" className="upload-label">
          <Upload size={48} />
          <div className="upload-text">
            <h3>Drag & Drop CSV Files Here</h3>
            <p>or click to browse</p>
            <p className="upload-hint">
              Upload 2 or more CSV files to automatically merge them
            </p>
          </div>
        </label>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="message error">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {success && (
        <div className="message success">
          <CheckCircle size={16} />
          {success}
        </div>
      )}

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h3>Uploaded Files ({uploadedFiles.length})</h3>
          <div className="file-list">
            {uploadedFiles.map(file => (
              <div key={file.id} className="file-item">
                <FileText size={16} />
                <div className="file-info">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">{formatFileSize(file.size)}</span>
                </div>
                <button
                  onClick={() => removeFile(file.id)}
                  className="remove-file"
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          {uploadedFiles.length >= 2 && !isProcessing && !mergedData && (
            <button
              onClick={() => handleMerge(uploadedFiles)}
              className="merge-button"
            >
              <Database size={16} />
              Merge Files
            </button>
          )}
        </div>
      )}

      {/* Processing Indicator */}
      {isProcessing && (
        <div className="processing">
          <div className="spinner"></div>
          <p>Processing and merging files...</p>
        </div>
      )}

      {/* Merged Data Display */}
      {mergedData && (
        <div className="merged-data">
          <div className="data-header">
            <h3>Merged Results</h3>
            <div className="data-stats">
              <span>Total Rows: {mergedData.totalRows}</span>
              <span>Matched: {mergedData.matchedRows}</span>
              <span>Unmatched: {mergedData.unmatchedRows}</span>
            </div>
          </div>

          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  {mergedData.headers.map((header, index) => (
                    <th key={index}>{header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {mergedData.rows.slice(0, 10).map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {row.map((cell, cellIndex) => (
                      <td key={cellIndex}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {mergedData.rows.length > 10 && (
              <p className="table-note">
                Showing first 10 rows of {mergedData.totalRows} total rows
              </p>
            )}
          </div>

          <div className="data-actions">
            <button className="download-button">
              Download Merged CSV
            </button>
          </div>
        </div>
      )}

      {/* Data Context Panel */}
      {sessionId && (
        <DataContextPanel sessionId={sessionId} />
      )}
    </div>
  );
};

export default BioMatcherUpload; 