import React, { useState, useEffect } from 'react';
import { 
  X, 
  Folder, 
  FileText, 
  Download, 
  Trash2, 
  Eye, 
  Copy, 
  Search,
  Grid,
  List,
  SortAsc,
  SortDesc
} from 'lucide-react';
import './FilesModal.css';

interface FileItem {
  id: string;
  name: string;
  type: 'csv' | 'json' | 'xlsx' | 'txt' | 'folder';
  size: string;
  uploadedAt: Date;
  lastModified: Date;
  status: 'processed' | 'processing' | 'error' | 'pending';
  path: string;
  description?: string;
}

interface FilesModalProps {
  isOpen: boolean;
  onClose: () => void;
  files: FileItem[];
  onFileSelect?: (file: FileItem) => void;
  onFileDelete?: (fileId: string) => void;
  onFileDownload?: (file: FileItem) => void;
}

const FilesModal: React.FC<FilesModalProps> = ({
  isOpen,
  onClose,
  files,
  onFileSelect,
  onFileDelete,
  onFileDownload
}) => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size' | 'type'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [showContextMenu, setShowContextMenu] = useState(false);
  const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
  const [contextMenuFile, setContextMenuFile] = useState<FileItem | null>(null);

  // Filter files based on search query
  const filteredFiles = files.filter(file => 
    file.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    file.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Sort files
  const sortedFiles = [...filteredFiles].sort((a, b) => {
    let comparison = 0;
    
    switch (sortBy) {
      case 'name':
        comparison = a.name.localeCompare(b.name);
        break;
      case 'date':
        comparison = new Date(a.lastModified).getTime() - new Date(b.lastModified).getTime();
        break;
      case 'size':
        comparison = parseFloat(a.size.replace(/[^\d.]/g, '')) - parseFloat(b.size.replace(/[^\d.]/g, ''));
        break;
      case 'type':
        comparison = a.type.localeCompare(b.type);
        break;
    }
    
    return sortOrder === 'asc' ? comparison : -comparison;
  });

  const getFileIcon = (file: FileItem) => {
    switch (file.type) {
      case 'csv':
        return <FileText size={20} className="file-icon csv" />;
      case 'json':
        return <FileText size={20} className="file-icon json" />;
      case 'xlsx':
        return <FileText size={20} className="file-icon xlsx" />;
      case 'txt':
        return <FileText size={20} className="file-icon txt" />;
      case 'folder':
        return <Folder size={20} className="file-icon folder" />;
      default:
        return <FileText size={20} className="file-icon" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
        return 'status-processed';
      case 'processing':
        return 'status-processing';
      case 'error':
        return 'status-error';
      case 'pending':
        return 'status-pending';
      default:
        return '';
    }
  };

  const handleFileClick = (file: FileItem, event: React.MouseEvent) => {
    if (event.ctrlKey || event.metaKey) {
      // Multi-select
      setSelectedFiles(prev => 
        prev.includes(file.id) 
          ? prev.filter(id => id !== file.id)
          : [...prev, file.id]
      );
    } else {
      // Single select
      setSelectedFiles([file.id]);
      onFileSelect?.(file);
    }
  };

  const handleContextMenu = (event: React.MouseEvent, file: FileItem) => {
    event.preventDefault();
    setContextMenuPosition({ x: event.clientX, y: event.clientY });
    setContextMenuFile(file);
    setShowContextMenu(true);
  };

  const handleSort = (field: 'name' | 'date' | 'size' | 'type') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const handleDeleteSelected = () => {
    selectedFiles.forEach(fileId => {
      onFileDelete?.(fileId);
    });
    setSelectedFiles([]);
  };

  const handleDownloadSelected = () => {
    selectedFiles.forEach(fileId => {
      const file = files.find(f => f.id === fileId);
      if (file) {
        onFileDownload?.(file);
      }
    });
  };

  useEffect(() => {
    if (!isOpen) {
      setSelectedFiles([]);
      setSearchQuery('');
    }
  }, [isOpen]);

  useEffect(() => {
    const handleClickOutside = () => {
      setShowContextMenu(false);
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  if (!isOpen) return null;

  return (
    <div className="files-modal-overlay" onClick={onClose}>
      <div className="files-modal" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="header-left">
            <h2 className="modal-title">Files</h2>
            <div className="breadcrumb">
              <span className="breadcrumb-item">DataWeaver</span>
              <span className="breadcrumb-separator">/</span>
              <span className="breadcrumb-item">Files</span>
            </div>
          </div>
          <div className="header-right">
            <button className="view-toggle" onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}>
              {viewMode === 'grid' ? <List size={16} /> : <Grid size={16} />}
            </button>
            <button className="close-button" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Toolbar */}
        <div className="modal-toolbar">
          <div className="toolbar-left">
            <div className="search-container">
              <Search size={16} className="search-icon" />
              <input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
            </div>
          </div>
          <div className="toolbar-right">
            {selectedFiles.length > 0 && (
              <>
                <button className="toolbar-button" onClick={handleDownloadSelected}>
                  <Download size={16} />
                  <span>Download ({selectedFiles.length})</span>
                </button>
                <button className="toolbar-button danger" onClick={handleDeleteSelected}>
                  <Trash2 size={16} />
                  <span>Delete ({selectedFiles.length})</span>
                </button>
              </>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="modal-content">
          {viewMode === 'list' ? (
            <div className="files-list">
              {/* List Header */}
              <div className="list-header">
                <div className="header-cell name-cell">
                  <button 
                    className="sort-button"
                    onClick={() => handleSort('name')}
                  >
                    Name
                    {sortBy === 'name' && (
                      sortOrder === 'asc' ? <SortAsc size={12} /> : <SortDesc size={12} />
                    )}
                  </button>
                </div>
                <div className="header-cell type-cell">
                  <button 
                    className="sort-button"
                    onClick={() => handleSort('type')}
                  >
                    Type
                    {sortBy === 'type' && (
                      sortOrder === 'asc' ? <SortAsc size={12} /> : <SortDesc size={12} />
                    )}
                  </button>
                </div>
                <div className="header-cell size-cell">
                  <button 
                    className="sort-button"
                    onClick={() => handleSort('size')}
                  >
                    Size
                    {sortBy === 'size' && (
                      sortOrder === 'asc' ? <SortAsc size={12} /> : <SortDesc size={12} />
                    )}
                  </button>
                </div>
                <div className="header-cell date-cell">
                  <button 
                    className="sort-button"
                    onClick={() => handleSort('date')}
                  >
                    Modified
                    {sortBy === 'date' && (
                      sortOrder === 'asc' ? <SortAsc size={12} /> : <SortDesc size={12} />
                    )}
                  </button>
                </div>
                <div className="header-cell status-cell">Status</div>
              </div>

              {/* List Items */}
              <div className="list-items">
                {sortedFiles.map(file => (
                  <div
                    key={file.id}
                    className={`list-item ${selectedFiles.includes(file.id) ? 'selected' : ''}`}
                    onClick={(e) => handleFileClick(file, e)}
                    onContextMenu={(e) => handleContextMenu(e, file)}
                  >
                    <div className="item-cell name-cell">
                      {getFileIcon(file)}
                      <span className="file-name">{file.name}</span>
                    </div>
                    <div className="item-cell type-cell">
                      <span className="file-type">{file.type.toUpperCase()}</span>
                    </div>
                    <div className="item-cell size-cell">
                      <span className="file-size">{file.size}</span>
                    </div>
                    <div className="item-cell date-cell">
                      <span className="file-date">
                        {file.lastModified.toLocaleDateString()}
                      </span>
                    </div>
                    <div className="item-cell status-cell">
                      <span className={`status-badge ${getStatusColor(file.status)}`}>
                        {file.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="files-grid">
              {sortedFiles.map(file => (
                <div
                  key={file.id}
                  className={`grid-item ${selectedFiles.includes(file.id) ? 'selected' : ''}`}
                  onClick={(e) => handleFileClick(file, e)}
                  onContextMenu={(e) => handleContextMenu(e, file)}
                >
                  <div className="grid-item-icon">
                    {getFileIcon(file)}
                  </div>
                  <div className="grid-item-name">{file.name}</div>
                  <div className="grid-item-meta">
                    <span className="grid-item-size">{file.size}</span>
                    <span className={`grid-item-status ${getStatusColor(file.status)}`}>
                      {file.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <div className="footer-left">
            <span className="file-count">
              {selectedFiles.length > 0 
                ? `${selectedFiles.length} of ${files.length} selected`
                : `${files.length} items`
              }
            </span>
          </div>
          <div className="footer-right">
            <button className="footer-button" onClick={onClose}>
              Close
            </button>
          </div>
        </div>

        {/* Context Menu */}
        {showContextMenu && contextMenuFile && (
          <div 
            className="context-menu"
            style={{
              left: contextMenuPosition.x,
              top: contextMenuPosition.y
            }}
          >
            <button className="context-menu-item" onClick={() => onFileSelect?.(contextMenuFile)}>
              <Eye size={16} />
              <span>Open</span>
            </button>
            <button className="context-menu-item" onClick={() => onFileDownload?.(contextMenuFile)}>
              <Download size={16} />
              <span>Download</span>
            </button>
            <button className="context-menu-item">
              <Copy size={16} />
              <span>Copy Path</span>
            </button>
            <div className="context-menu-separator"></div>
            <button 
              className="context-menu-item danger" 
              onClick={() => onFileDelete?.(contextMenuFile.id)}
            >
              <Trash2 size={16} />
              <span>Delete</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default FilesModal; 