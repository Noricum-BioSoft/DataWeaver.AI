// Workflow Types
export interface Workflow {
  id: number;
  name: string;
  description?: string;
  status: WorkflowStatus;
  created_at: string;
  updated_at?: string;
  metadata?: Record<string, any>;
}

export enum WorkflowStatus {
  DRAFT = "draft",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled"
}

export interface WorkflowCreate {
  name: string;
  description?: string;
  metadata?: Record<string, any>;
}

export interface WorkflowUpdate {
  name?: string;
  description?: string;
  status?: WorkflowStatus;
  metadata?: Record<string, any>;
}

// Workflow Step Types
export interface WorkflowStep {
  id: number;
  workflow_id: number;
  name: string;
  description?: string;
  step_type: StepType;
  status: StepStatus;
  order_index: number;
  external_provider?: string;
  external_config?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export enum StepStatus {
  PENDING = "pending",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed",
  SKIPPED = "skipped"
}

export enum StepType {
  INPUT = "input",
  PROCESSING = "processing",
  OUTPUT = "output",
  EXTERNAL = "external"
}

export interface WorkflowStepCreate {
  name: string;
  description?: string;
  step_type: StepType;
  order_index: number;
  external_provider?: string;
  external_config?: Record<string, any>;
}

export interface WorkflowStepUpdate {
  name?: string;
  description?: string;
  step_type?: StepType;
  status?: StepStatus;
  order_index?: number;
  external_provider?: string;
  external_config?: Record<string, any>;
}

// File Types
export interface AppFile {
  id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  file_type: AppFileType;
  mime_type?: string;
  status: AppFileStatus;
  workflow_id: number;
  input_step_id?: number;
  output_step_id?: number;
  parent_file_id?: number;
  created_at: string;
  updated_at?: string;
}

export enum AppFileType {
  CSV = "csv",
  EXCEL = "excel",
  TEXT = "text",
  JSON = "json",
  XML = "xml",
  BINARY = "binary",
  OTHER = "other"
}

export enum AppFileStatus {
  UPLOADING = "uploading",
  PROCESSING = "processing",
  READY = "ready",
  ERROR = "error",
  DELETED = "deleted"
}

export interface FileUploadResponse {
  file_id: number;
  filename: string;
  file_path: string;
  file_size: number;
  status: AppFileStatus;
  message: string;
}

// Dataset Types
export interface Dataset {
  id: number;
  name: string;
  description?: string;
  source_provider?: string;
  source_file_path?: string;
  file_type?: string;
  status: DatasetStatus;
  matching_config?: Record<string, any>;
  identifiers?: Record<string, any>;
  row_count?: number;
  column_count?: number;
  file_size?: number;
  created_at: string;
  updated_at?: string;
}

export enum DatasetStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  MATCHED = "matched",
  UNMATCHED = "unmatched",
  ERROR = "error"
}

export interface DatasetCreate {
  name: string;
  description?: string;
  source_provider?: string;
  source_file_path?: string;
  file_type?: string;
  matching_config?: Record<string, any>;
  identifiers?: Record<string, any>;
}

// Dataset Match Types
export interface DatasetMatch {
  id: number;
  dataset_id: number;
  workflow_id: number;
  step_id?: number;
  file_id?: number;
  match_type: MatchType;
  confidence_score?: number;
  matching_criteria?: Record<string, any>;
  matched_identifiers?: Record<string, any>;
  is_confirmed: number;
  confirmed_by?: string;
  confirmed_at?: string;
  created_at: string;
}

export enum MatchType {
  EXACT = "exact",
  FUZZY = "fuzzy",
  ML_BASED = "ml_based",
  MANUAL = "manual"
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

// Form Types
export interface FileUploadForm {
  workflow_id: number;
  step_id?: number;
  parent_file_id?: number;
}

export interface DatasetProcessingForm {
  source_provider?: string;
  matching_config?: Record<string, any>;
} 