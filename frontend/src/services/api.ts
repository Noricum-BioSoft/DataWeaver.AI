import axios from 'axios';
import {
  Workflow,
  WorkflowCreate,
  WorkflowUpdate,
  WorkflowStep,
  WorkflowStepCreate,
  WorkflowStepUpdate,
  AppFile,
  FileUploadResponse,
  Dataset,
  DatasetCreate,
  DatasetMatch,
  ApiResponse,
  PaginatedResponse
} from '../types';

// API base configuration
// Use relative URLs since we have proxy configured in package.json
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Workflow API
export const workflowApi = {
  // Get all workflows
  getWorkflows: async (): Promise<Workflow[]> => {
    const response = await api.get('/workflows');
    return response.data;
  },

  // Get workflow by ID
  getWorkflow: async (id: number): Promise<Workflow> => {
    const response = await api.get(`/workflows/${id}`);
    return response.data;
  },

  // Create workflow
  createWorkflow: async (workflow: WorkflowCreate): Promise<Workflow> => {
    const response = await api.post('/workflows', workflow);
    return response.data;
  },

  // Update workflow
  updateWorkflow: async (id: number, workflow: WorkflowUpdate): Promise<Workflow> => {
    const response = await api.put(`/workflows/${id}`, workflow);
    return response.data;
  },

  // Delete workflow
  deleteWorkflow: async (id: number): Promise<void> => {
    await api.delete(`/workflows/${id}`);
  },

  // Get workflow steps
  getWorkflowSteps: async (workflowId: number): Promise<WorkflowStep[]> => {
    const response = await api.get(`/workflows/${workflowId}/steps`);
    return response.data;
  },

  // Create workflow step
  createWorkflowStep: async (workflowId: number, step: WorkflowStepCreate): Promise<WorkflowStep> => {
    const response = await api.post(`/workflows/${workflowId}/steps`, step);
    return response.data;
  },

  // Update workflow step
  updateWorkflowStep: async (workflowId: number, stepId: number, step: WorkflowStepUpdate): Promise<WorkflowStep> => {
    const response = await api.put(`/workflows/${workflowId}/steps/${stepId}`, step);
    return response.data;
  },

  // Delete workflow step
  deleteWorkflowStep: async (workflowId: number, stepId: number): Promise<void> => {
    await api.delete(`/workflows/${workflowId}/steps/${stepId}`);
  },
};

// File API
export const fileApi = {
  // Upload file
  uploadFile: async (
    workflowId: number,
    file: File, // browser File type
    stepId?: number,
    parentFileId?: number
  ): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (stepId) formData.append('step_id', stepId.toString());
    if (parentFileId) formData.append('parent_file_id', parentFileId.toString());

    const response = await api.post(`/files/upload/${workflowId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get file by ID
  getFile: async (id: number): Promise<AppFile> => {
    const response = await api.get(`/files/${id}`);
    return response.data;
  },

  // Download file
  downloadFile: async (id: number): Promise<Blob> => {
    const response = await api.get(`/files/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Delete file
  deleteFile: async (id: number): Promise<void> => {
    await api.delete(`/files/${id}`);
  },

  // Get workflow files
  getWorkflowFiles: async (workflowId: number): Promise<AppFile[]> => {
    const response = await api.get(`/files/workflow/${workflowId}`);
    return response.data;
  },

  // Get step files
  getStepFiles: async (stepId: number): Promise<AppFile[]> => {
    const response = await api.get(`/files/step/${stepId}`);
    return response.data;
  },

  // Add file metadata
  addFileMetadata: async (fileId: number, metadata: Record<string, any>): Promise<void> => {
    await api.post(`/files/${fileId}/metadata`, metadata);
  },

  // Get file metadata
  getFileMetadata: async (fileId: number): Promise<Record<string, any>[]> => {
    const response = await api.get(`/files/${fileId}/metadata`);
    return response.data;
  },
};

// Dataset API
export const datasetApi = {
  // Get all datasets
  getDatasets: async (): Promise<Dataset[]> => {
    const response = await api.get('/datasets');
    return response.data;
  },

  // Get dataset by ID
  getDataset: async (id: number): Promise<Dataset> => {
    const response = await api.get(`/datasets/${id}`);
    return response.data;
  },

  // Create dataset
  createDataset: async (dataset: DatasetCreate): Promise<Dataset> => {
    const response = await api.post('/datasets', dataset);
    return response.data;
  },

  // Delete dataset
  deleteDataset: async (id: number): Promise<void> => {
    await api.delete(`/datasets/${id}`);
  },

  // Process dataset file
  processDataset: async (
    file: File, // browser File type
    sourceProvider?: string,
    matchingConfig?: Record<string, any>
  ): Promise<Dataset> => {
    const formData = new FormData();
    formData.append('file', file);
    if (sourceProvider) formData.append('source_provider', sourceProvider);
    if (matchingConfig) formData.append('matching_config', JSON.stringify(matchingConfig));

    const response = await api.post('/datasets/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Match dataset to workflow
  matchDatasetToWorkflow: async (
    datasetId: number,
    workflowId: number,
    matchingConfig?: Record<string, any>
  ): Promise<DatasetMatch[]> => {
    const response = await api.post(`/datasets/${datasetId}/match/${workflowId}`, {
      matching_config: matchingConfig,
    });
    return response.data;
  },

  // Auto match dataset
  autoMatchDataset: async (
    datasetId: number,
    matchingConfig?: Record<string, any>
  ): Promise<DatasetMatch[]> => {
    const response = await api.post(`/datasets/${datasetId}/auto-match`, {
      matching_config: matchingConfig,
    });
    return response.data;
  },

  // Get dataset matches
  getDatasetMatches: async (datasetId: number): Promise<DatasetMatch[]> => {
    const response = await api.get(`/datasets/${datasetId}/matches`);
    return response.data;
  },

  // Confirm match
  confirmMatch: async (matchId: number, confirmedBy: string): Promise<void> => {
    await api.put(`/datasets/matches/${matchId}/confirm`, { confirmed_by: confirmedBy });
  },

  // Reject match
  rejectMatch: async (matchId: number, rejectedBy: string): Promise<void> => {
    await api.put(`/datasets/matches/${matchId}/reject`, { rejected_by: rejectedBy });
  },

  // Get workflow matches
  getWorkflowMatches: async (workflowId: number): Promise<DatasetMatch[]> => {
    const response = await api.get(`/datasets/workflow/${workflowId}/matches`);
    return response.data;
  },
};

// Bio-Matcher API
export const bioMatcherApi = {
  // Create workflow session
  createWorkflowSession: async (): Promise<{ session_id: string; message: string }> => {
    const response = await api.post('/bio/create-workflow-session');
    return response.data;
  },

  // Merge two CSV files with session support
  mergeFiles: async (formData: FormData): Promise<{
    headers: string[];
    rows: any[][];
    totalRows: number;
    matchedRows: number;
    unmatchedRows: number;
    session_id?: string;
    workflow_step: string;
  }> => {
    const response = await api.post('/bio/merge-files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Generate visualization from CSV data or session data
  generateVisualization: async (
    file?: File,
    plotType: string = "scatter",
    xColumn?: string,
    yColumn?: string,
    sessionId?: string,
    useSessionData: boolean = false
  ): Promise<{
    plot_type: string;
    plot_data: string;
    columns: string[];
    data_shape: [number, number];
    numeric_columns: string[];
    session_id?: string;
    workflow_step: string;
  }> => {
    const formData = new FormData();
    if (file) formData.append('file', file);
    formData.append('plot_type', plotType);
    if (xColumn) formData.append('x_column', xColumn);
    if (yColumn) formData.append('y_column', yColumn);
    if (sessionId) formData.append('session_id', sessionId);
    formData.append('use_session_data', useSessionData.toString());

    const response = await api.post('/bio/generate-visualization', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get workflow status
  getWorkflowStatus: async (sessionId: string): Promise<{
    session_id: string;
    created_at: string;
    last_updated: string;
    steps: any[];
    has_merged_data: boolean;
    has_visualization_data: boolean;
  }> => {
    const response = await api.get(`/bio/workflow-status/${sessionId}`);
    return response.data;
  },

  // Get workflow history
  getWorkflowHistory: async (sessionId: string): Promise<{
    session_id: string;
    history: any[];
  }> => {
    const response = await api.get(`/bio/workflow-history/${sessionId}`);
    return response.data;
  },

  // Upload test results
  uploadTestResults: async (
    file: File,
    testType: string = "activity",
    assayName?: string,
    protocol?: string
  ): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('test_type', testType);
    if (assayName) formData.append('assay_name', assayName);
    if (protocol) formData.append('protocol', protocol);

    const response = await api.post('/bio/upload-test-results', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get designs
  getDesigns: async (): Promise<any[]> => {
    const response = await api.get('/bio/designs');
    return response.data;
  },

  // Get builds
  getBuilds: async (): Promise<any[]> => {
    const response = await api.get('/bio/builds');
    return response.data;
  },

  // Get tests
  getTests: async (): Promise<any[]> => {
    const response = await api.get('/bio/tests');
    return response.data;
  },
};

export default api; 