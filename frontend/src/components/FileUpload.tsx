import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File as FileIcon, X, CheckCircle, AlertCircle } from 'lucide-react';
import { fileApi } from '../services/api';
import { FileUploadResponse } from '../types';

interface FileUploadProps {
  workflowId: number;
  stepId?: number;
  parentFileId?: number;
  onUploadComplete?: (response: FileUploadResponse) => void;
  onUploadError?: (error: string) => void;
}

interface UploadingFile {
  file: File; // browser File type
  progress: number;
  status: 'uploading' | 'success' | 'error';
  response?: FileUploadResponse;
  error?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  workflowId,
  stepId,
  parentFileId,
  onUploadComplete,
  onUploadError,
}) => {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const newUploadingFiles: UploadingFile[] = acceptedFiles.map((file) => ({
        file,
        progress: 0,
        status: 'uploading',
      }));

      setUploadingFiles((prev) => [...prev, ...newUploadingFiles]);

      for (let i = 0; i < acceptedFiles.length; i++) {
        const file = acceptedFiles[i];
        const fileIndex = uploadingFiles.length + i;

        try {
          // Simulate progress
          const progressInterval = setInterval(() => {
            setUploadingFiles((prev) =>
              prev.map((f, index) =>
                index === fileIndex
                  ? { ...f, progress: Math.min(f.progress + 10, 90) }
                  : f
              )
            );
          }, 100);

          const response = await fileApi.uploadFile(workflowId, file, stepId, parentFileId);

          clearInterval(progressInterval);

          setUploadingFiles((prev) =>
            prev.map((f, index) =>
              index === fileIndex
                ? { ...f, progress: 100, status: 'success', response }
                : f
            )
          );

          onUploadComplete?.(response);
        } catch (error) {
          setUploadingFiles((prev) =>
            prev.map((f, index) =>
              index === fileIndex
                ? {
                    ...f,
                    status: 'error',
                    error: error instanceof Error ? error.message : 'Upload failed',
                  }
                : f
            )
          );

          onUploadError?.(error instanceof Error ? error.message : 'Upload failed');
        }
      }
    },
    [workflowId, stepId, parentFileId, uploadingFiles.length, onUploadComplete, onUploadError]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/plain': ['.txt'],
      'application/json': ['.json'],
      'application/xml': ['.xml'],
    },
  });

  const removeFile = (index: number) => {
    setUploadingFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full">
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm text-gray-600">
          {isDragActive
            ? 'Drop the files here...'
            : 'Drag & drop files here, or click to select files'}
        </p>
        <p className="mt-1 text-xs text-gray-500">
          Supports CSV, Excel, JSON, XML, and text files
        </p>
      </div>

      {/* Upload Progress */}
      {uploadingFiles.length > 0 && (
        <div className="mt-4 space-y-2">
          <h3 className="text-sm font-medium text-gray-900">Uploading Files</h3>
          {uploadingFiles.map((uploadingFile, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-3 flex-1">
                <FileIcon className="h-5 w-5 text-gray-400" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {uploadingFile.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(uploadingFile.file.size)}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                {/* Progress Bar */}
                {uploadingFile.status === 'uploading' && (
                  <div className="flex-1 max-w-xs">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadingFile.progress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Status Icon */}
                {uploadingFile.status === 'success' && (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                )}
                {uploadingFile.status === 'error' && (
                  <AlertCircle className="h-5 w-5 text-red-500" />
                )}

                {/* Remove Button */}
                <button
                  onClick={() => removeFile(index)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload; 