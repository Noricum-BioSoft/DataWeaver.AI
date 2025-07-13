import React, { useState, useEffect } from 'react';
import { Upload, Search, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { datasetApi } from '../services/api';
import { Dataset, DatasetMatch, MatchType, DatasetStatus } from '../types';

interface DatasetMatchingProps {
  workflowId?: number;
  onMatchFound?: (match: DatasetMatch) => void;
}

const DatasetMatching: React.FC<DatasetMatchingProps> = ({
  workflowId,
  onMatchFound,
}) => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [matches, setMatches] = useState<DatasetMatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      setLoading(true);
      const data = await datasetApi.getDatasets();
      setDatasets(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load datasets');
    } finally {
      setLoading(false);
    }
  };

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0]; // browser File type
    setLoading(true);
    setError(null);

    try {
      const dataset = await datasetApi.processDataset(file);
      setDatasets(prev => [dataset, ...prev]);
      setSelectedDataset(dataset);

      // Auto-match if workflow is specified
      if (workflowId) {
        const matches = await datasetApi.matchDatasetToWorkflow(dataset.id, workflowId);
        setMatches(matches);
        
        if (matches.length > 0) {
          onMatchFound?.(matches[0]);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process dataset');
    } finally {
      setLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    multiple: false,
  });

  const handleAutoMatch = async (dataset: Dataset) => {
    try {
      setLoading(true);
      const matches = await datasetApi.autoMatchDataset(dataset.id);
      setMatches(matches);
      setSelectedDataset(dataset);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to auto-match dataset');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmMatch = async (match: DatasetMatch) => {
    try {
      await datasetApi.confirmMatch(match.id, 'user');
      setMatches(prev => 
        prev.map(m => 
          m.id === match.id 
            ? { ...m, is_confirmed: 1, confirmed_by: 'user' }
            : m
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to confirm match');
    }
  };

  const handleRejectMatch = async (match: DatasetMatch) => {
    try {
      await datasetApi.rejectMatch(match.id, 'user');
      setMatches(prev => 
        prev.map(m => 
          m.id === match.id 
            ? { ...m, is_confirmed: -1, confirmed_by: 'user' }
            : m
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject match');
    }
  };

  const getMatchTypeColor = (matchType: MatchType) => {
    switch (matchType) {
      case MatchType.EXACT:
        return 'bg-green-100 text-green-800';
      case MatchType.FUZZY:
        return 'bg-yellow-100 text-yellow-800';
      case MatchType.ML_BASED:
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Upload External Dataset</h3>
        
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
              ? 'Drop the dataset file here...'
              : 'Drag & drop CSV or Excel files here, or click to select'}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            The system will automatically extract identifiers and find matches
          </p>
        </div>
      </div>

      {/* Datasets List */}
      {datasets.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Processed Datasets</h3>
          
          <div className="space-y-3">
            {datasets.map((dataset) => (
              <div
                key={dataset.id}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedDataset?.id === dataset.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedDataset(dataset)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">{dataset.name}</h4>
                    <p className="text-sm text-gray-500">
                      {dataset.source_provider && `From: ${dataset.source_provider}`}
                    </p>
                    {dataset.identifiers && (
                      <p className="text-xs text-gray-400 mt-1">
                        {dataset.identifiers.row_count} rows, {dataset.identifiers.column_count} columns
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        dataset.status === DatasetStatus.MATCHED
                          ? 'bg-green-100 text-green-800'
                          : dataset.status === DatasetStatus.UNMATCHED
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {dataset.status}
                    </span>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAutoMatch(dataset);
                      }}
                      className="p-2 text-gray-400 hover:text-blue-600"
                      disabled={loading}
                    >
                      <Search className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Matches Section */}
      {selectedDataset && matches.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Matches for {selectedDataset.name}
          </h3>
          
          <div className="space-y-3">
            {matches.map((match) => (
              <div
                key={match.id}
                className="p-4 border border-gray-200 rounded-lg"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getMatchTypeColor(
                          match.match_type
                        )}`}
                      >
                        {match.match_type}
                      </span>
                      {match.confidence_score && (
                        <span
                          className={`text-sm font-medium ${getConfidenceColor(
                            match.confidence_score
                          )}`}
                        >
                          {Math.round(match.confidence_score * 100)}% confidence
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-600">
                      Workflow ID: {match.workflow_id}
                      {match.step_id && ` • Step ID: ${match.step_id}`}
                      {match.file_id && ` • File ID: ${match.file_id}`}
                    </p>
                    
                    {match.matched_identifiers && (
                      <p className="text-xs text-gray-500 mt-1">
                        Matched identifiers: {Object.keys(match.matched_identifiers).join(', ')}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {match.is_confirmed === 0 && (
                      <>
                        <button
                          onClick={() => handleConfirmMatch(match)}
                          className="p-2 text-green-600 hover:bg-green-50 rounded"
                          title="Confirm match"
                        >
                          <CheckCircle className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleRejectMatch(match)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded"
                          title="Reject match"
                        >
                          <XCircle className="h-4 w-4" />
                        </button>
                      </>
                    )}
                    
                    {match.is_confirmed === 1 && (
                      <span className="text-green-600 text-sm font-medium">
                        Confirmed
                      </span>
                    )}
                    
                    {match.is_confirmed === -1 && (
                      <span className="text-red-600 text-sm font-medium">
                        Rejected
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Processing...</span>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatasetMatching; 