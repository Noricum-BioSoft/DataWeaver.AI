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
  Connector,
  ConnectorCreate,
  ConnectorUpdate,
  DataSource,
  DataSourceCreate,
  DataSourceUpdate,
  DataExtract,
  ConnectorSyncLog,
  DemoScenario,
  ConnectorTestResult,
  DataDiscoveryResult,
  SyncResult,

  // ApiResponse,
  // PaginatedResponse
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

// Data Q&A API
export const dataQaApi = {
  // Ask a question about data
  askQuestion: async (sessionId: string, question: string): Promise<{
    success: boolean;
    answer?: string;
    insights?: string[];
    confidence?: string;
    suggestions?: string[];
    data_summary?: any;
    error?: string;
  }> => {
    const response = await api.post('/data-qa/ask', {
      session_id: sessionId,
      question: question
    });
    return response.data;
  },

  // Get data preview
  getDataPreview: async (sessionId: string, limit: number = 10): Promise<{
    success: boolean;
    preview?: any;
    error?: string;
  }> => {
    const response = await api.get(`/data-qa/preview/${sessionId}?limit=${limit}`);
    return response.data;
  },

  // Get question suggestions
  getQuestionSuggestions: async (sessionId: string): Promise<{
    suggestions: string[];
  }> => {
    const response = await api.get(`/data-qa/suggestions/${sessionId}`);
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<{
    status: string;
    service: string;
    llm_available: boolean;
  }> => {
    const response = await api.get('/data-qa/health');
    return response.data;
  },
};

// Workflow API - Enhanced for natural language commands and data merging
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

  // Execute natural language command
  executeCommand: async (workflowId: number, command: string): Promise<{
    workflow_id: number;
    command: string;
    result: any;
    status: string;
    message: string;
  }> => {
    const response = await api.post(`/workflows/${workflowId}/execute`, {
      command: command
    });
    return response.data;
  },

  // Get workflow data lineage
  getDataLineage: async (workflowId: number): Promise<{
    workflow_id: number;
    data_sources: Array<{
      file_id: number;
      filename: string;
      step_id: number;
      step_name: string;
      data_type: string;
    }>;
    data_outputs: Array<{
      file_id: number;
      filename: string;
      step_id: number;
      step_name: string;
      data_type: string;
    }>;
    data_relationships: Array<{
      source_file_id: number;
      target_file_id: number;
      relationship_type: string;
      confidence_score: number;
    }>;
  }> => {
    const response = await api.get(`/workflows/${workflowId}/lineage`);
    return response.data;
  },

  // Auto-merge workflow data
  autoMergeData: async (workflowId: number): Promise<{
    workflow_id: number;
    merged_files: Array<{
      file_id: number;
      filename: string;
      merged_from: Array<number>;
      merge_strategy: string;
    }>;
    message: string;
  }> => {
    const response = await api.post(`/workflows/${workflowId}/merge`);
    return response.data;
  },

  // Get workflow execution history
  getExecutionHistory: async (workflowId: number): Promise<{
    workflow_id: number;
    commands: Array<{
      command: string;
      timestamp: string;
      status: string;
      result: any;
    }>;
    data_changes: Array<{
      file_id: number;
      filename: string;
      change_type: string;
      timestamp: string;
    }>;
  }> => {
    const response = await api.get(`/workflows/${workflowId}/history`);
    return response.data;
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

  // Clear workflow session
  clearWorkflowSession: async (sessionId: string): Promise<{ session_id: string; message: string }> => {
    const response = await api.delete(`/bio/clear-session/${sessionId}`);
    return response.data;
  },

  // Upload a single CSV file to session
  uploadSingleFile: async (formData: FormData): Promise<{
    headers: string[];
    rows: any[][];
    totalRows: number;
    matchedRows: number;
    unmatchedRows: number;
    session_id?: string;
    workflow_step: string;
    filename: string;
  }> => {
    const response = await api.post('/bio/upload-single-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
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

  // Merge files that are already uploaded to a session
  mergeSessionFiles: async (formData: FormData, forceRemerge: boolean = false): Promise<{
    headers: string[];
    rows: any[][];
    totalRows: number;
    matchedRows: number;
    unmatchedRows: number;
    session_id?: string;
    workflow_step: string;
    message?: string;
    cached?: boolean;
  }> => {
    // Add force_remerge parameter to form data
    formData.append('force_remerge', forceRemerge.toString());
    
    const response = await api.post('/bio/merge-session-files', formData, {
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
    useSessionData: boolean = false,
    columns?: string,
    isSubplot: boolean = false
  ): Promise<{
    plot_type: string;
    plot_json: string;
    columns: string[];
    data_shape: [number, number];
    numeric_columns: string[];
    session_id?: string;
    workflow_step: string;
    is_subplot?: boolean;
    matched_columns?: string[];
  }> => {
    const formData = new FormData();
    
    if (file) {
      formData.append('file', file);
    }
    
    if (sessionId) {
      formData.append('session_id', sessionId);
    }
    
    formData.append('plot_type', plotType);
    formData.append('use_session_data', useSessionData.toString());
    formData.append('is_subplot', isSubplot.toString());
    
    if (xColumn) {
      formData.append('x_column', xColumn);
    }
    
    if (yColumn) {
      formData.append('y_column', yColumn);
    }
    
    if (columns) {
      formData.append('columns', columns);
    }
    
    const response = await api.post('/bio/generate-visualization', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Explain visualization trends and patterns
  explainVisualization: async (
    sessionId: string,
    plotType: string = "scatter",
    xColumn?: string,
    yColumn?: string
  ): Promise<{
    plot_type: string;
    data_shape: [number, number];
    analysis: any;
    session_id: string;
  }> => {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('plot_type', plotType);
    
    if (xColumn) {
      formData.append('x_column', xColumn);
    }
    
    if (yColumn) {
      formData.append('y_column', yColumn);
    }
    
    const response = await api.post('/bio/explain-visualization', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Analyze data and generate insights and recommendations
  analyzeData: async (
    file?: File,
    sessionId?: string,
    useSessionData: boolean = true
  ): Promise<{
    dataset_info: any;
    insights: any[];
    quality_analysis: any;
    statistical_analysis: any;
    correlation_analysis: any;
    pattern_analysis: any;
    recommendations: any[];
    session_id?: string;
  }> => {
    const formData = new FormData();
    
    if (file) {
      formData.append('file', file);
    }
    
    if (sessionId) {
      formData.append('session_id', sessionId);
    }
    
    formData.append('use_session_data', useSessionData.toString());
    
    const response = await api.post('/bio/analyze-data', formData, {
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

  // General AI chat
  generalChat: async (message: string, sessionId?: string, context?: any): Promise<{
    response: string;
    suggestions: string[];
    confidence: string;
    context?: any;
  }> => {
    const response = await api.post('/general-chat/chat', {
      message,
      session_id: sessionId,
      context
    });
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

  // Get data context
  getDataContext: async (sessionId: string): Promise<{
    session_id: string;
    total_data_items: number;
    uploaded_files: any[];
    merged_datasets: any[];
    visualizations: any[];
    data_lineage: Record<string, any>;
  }> => {
    const response = await api.get(`/bio/data-context/${sessionId}`);
    return response.data;
  },

  // Get filtered data
  getFilteredData: async (sessionId: string): Promise<{
    session_id: string;
    query: string;
    original_shape: [number, number];
    filtered_shape: [number, number];
    rows_removed: number;
    filtered_data: any;
    columns: string[];
    sample_rows: any[];
  }> => {
    const response = await api.get(`/bio/filtered-data/${sessionId}`);
    return response.data;
  },

  // Download filtered data as CSV
  downloadFilteredData: async (sessionId: string): Promise<Blob> => {
    const response = await api.get(`/bio/download-filtered-data/${sessionId}`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Query and filter data
  queryData: async (
    sessionId: string,
    query: string,
    useSessionData: boolean = true
  ): Promise<{
    session_id: string;
    query: string;
    original_shape: [number, number];
    filtered_shape: [number, number];
    rows_removed: number;
    filtered_data: any;
    columns: string[];
    sample_rows: any[];
  }> => {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('query', query);
    formData.append('use_session_data', useSessionData.toString());
    
    const response = await api.post('/bio/query-data', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },
};



export default api;

// Export individual APIs for easier imports
export const generalChatApi = {
  chat: bioMatcherApi.generalChat
};

// Connector API
export const connectorApi = {
  // Get all connectors
  getConnectors: async (): Promise<Connector[]> => {
    const response = await api.get('/connectors');
    return response.data;
  },

  // Get connector by ID
  getConnector: async (id: number): Promise<Connector> => {
    const response = await api.get(`/connectors/${id}`);
    return response.data;
  },

  // Create connector
  createConnector: async (connector: ConnectorCreate): Promise<Connector> => {
    const response = await api.post('/connectors', connector);
    return response.data;
  },

  // Update connector
  updateConnector: async (id: number, connector: ConnectorUpdate): Promise<Connector> => {
    const response = await api.put(`/connectors/${id}`, connector);
    return response.data;
  },

  // Delete connector
  deleteConnector: async (id: number): Promise<void> => {
    await api.delete(`/connectors/${id}`);
  },

  // Test connector connection
  testConnection: async (id: number, testConfig?: Record<string, any>): Promise<ConnectorTestResult> => {
    const response = await api.post(`/connectors/${id}/test`, { test_config: testConfig });
    return response.data;
  },

  // Discover data sources
  discoverDataSources: async (id: number): Promise<DataDiscoveryResult> => {
    const response = await api.post(`/connectors/${id}/discover`);
    return response.data;
  },

  // Sync data sources
  syncDataSources: async (id: number): Promise<SyncResult> => {
    const response = await api.post(`/connectors/${id}/sync`);
    return response.data;
  },

  // Get supported connector types
  getSupportedTypes: async (): Promise<string[]> => {
    const response = await api.get('/connectors/types/supported');
    return response.data;
  },

  // Get demo scenarios
  getDemoScenarios: async (): Promise<DemoScenario[]> => {
    const response = await api.get('/connectors/scenarios');
    return response.data;
  },

  // Setup demo scenario
  setupDemoScenario: async (scenarioId: string): Promise<{
    scenario_id: string;
    connectors: Connector[];
    data_sources: DataSource[];
    message: string;
  }> => {
    const response = await api.post(`/connectors/scenarios/${scenarioId}/setup`);
    return response.data;
  },

  // Data Source Management
  getDataSources: async (connectorId: number): Promise<DataSource[]> => {
    const response = await api.get(`/connectors/${connectorId}/data-sources`);
    return response.data;
  },

  // Create data source
  createDataSource: async (dataSource: DataSourceCreate): Promise<DataSource> => {
    const response = await api.post('/connectors/data-sources', dataSource);
    return response.data;
  },

  // Update data source
  updateDataSource: async (id: number, dataSource: DataSourceUpdate): Promise<DataSource> => {
    const response = await api.put(`/connectors/data-sources/${id}`, dataSource);
    return response.data;
  },

  // Delete data source
  deleteDataSource: async (id: number): Promise<void> => {
    await api.delete(`/connectors/data-sources/${id}`);
  },

  // Extract data from data source
  extractData: async (dataSourceId: number, extractConfig?: Record<string, any>): Promise<DataExtract> => {
    const response = await api.post(`/connectors/data-sources/${dataSourceId}/extract`, { extract_config: extractConfig });
    return response.data;
  },

  // Get sync logs
  getSyncLogs: async (connectorId: number): Promise<ConnectorSyncLog[]> => {
    const response = await api.get(`/connectors/${connectorId}/sync-logs`);
    return response.data;
  },
}; 