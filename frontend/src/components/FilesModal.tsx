import React from 'react';
import './FilesModal.css';

interface FilesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const FilesModal: React.FC<FilesModalProps> = ({ isOpen, onClose }) => {
  const files = [
    {
      id: 1,
      name: 'protein_data.csv',
      size: '2.3 MB',
      type: 'CSV',
      uploaded: '2 hours ago',
      status: 'Ready'
    },
    {
      id: 2,
      name: 'assay_results.xlsx',
      size: '1.8 MB',
      type: 'Excel',
      uploaded: '1 day ago',
      status: 'Ready'
    },
    {
      id: 3,
      name: 'sequence_data.fasta',
      size: '5.1 MB',
      type: 'FASTA',
      uploaded: '3 days ago',
      status: 'Processing'
    }
  ];

  if (!isOpen) return null;

  return (
    <div className="files-modal-overlay" onClick={onClose}>
      <div className="files-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>📁 Files</h2>
          <button className="modal-close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div className="modal-content">
          <div className="files-list">
            {files.map(file => (
              <div key={file.id} className="file-item">
                <div className="file-icon">
                  {file.type === 'CSV' && '📊'}
                  {file.type === 'Excel' && '📈'}
                  {file.type === 'FASTA' && '🧬'}
                </div>
                <div className="file-info">
                  <h3 className="file-name">{file.name}</h3>
                  <p className="file-details">{file.size} • {file.type} • {file.uploaded}</p>
                </div>
                <div className="file-status">
                  <span className={`status-badge ${file.status.toLowerCase()}`}>
                    {file.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FilesModal; 