# DataWeaver.AI Data/Control Flow Documentation

## Overview

DataWeaver.AI is a comprehensive data management platform that enables users to perform natural language-driven workflows for data analysis, merging, and visualization. This document outlines the complete data and control flow from user interaction to final results display.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Components │    │   API Services  │    │   Data Models   │
│   - Chat        │    │   - File Mgmt   │    │   - Workflows   │
│   - Results     │    │   - Merge       │    │   - Files       │
│   - Visuals     │    │   - Analysis    │    │   - Datasets    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 1. Application Initialization Flow

### Frontend Initialization
```
App.tsx
├── Theme Selection (Sidebar/Dashboard)
├── AIChatLayout.tsx
│   ├── AIChatHeader.tsx
│   ├── AIChatSidebar.tsx
│   └── AIChatMain.tsx
│       ├── ChatHistory.tsx
│       ├── PromptBox.tsx
│       ├── ResultPanel.tsx
│       └── WorkflowCreationForm.tsx
```

### Backend Initialization
```
main.py
├── FastAPI App Setup
├── CORS Middleware
├── Database Connection
└── API Router Registration
    ├── files.router
    ├── workflows.router
    ├── datasets.router
    ├── bio_matcher.router
    ├── intelligent_merge.router
    ├── data_qa.router
    └── general_chat.router
```

## 2. User Interaction Flow

### 2.1 Natural Language Command Processing

```
User Input → AIChatMain.handlePromptSubmit()
├── Command Classification
│   ├── Plot/Visualization Requests
│   ├── Data Q&A Requests
│   ├── File Merge Requests
│   ├── Data Analysis Requests
│   └── General Chat Requests
├── Session Management
│   ├── Create/Retrieve Session ID
│   └── Maintain Context
└── Route to Appropriate Handler
```

### 2.2 Command Classification Logic

```typescript
// Priority-based command classification
if (plotExplanationKeywords && hasData) {
  handlePlotExplanation(prompt);
} else if (visualizationKeywords && hasData) {
  handleVisualization(prompt);
} else if (qaKeywords && hasData) {
  handleDataQA(prompt);
} else if (mergeKeywords && hasFiles) {
  handleFileMerge();
} else if (analysisKeywords && hasData) {
  handleDataAnalysis(prompt);
} else {
  handleGeneralChat(prompt);
}
```

## 3. File Management Flow

### 3.1 File Upload Process

```
File Upload → AIChatMain.handleFileUpload()
├── File Validation
│   ├── Size Limits
│   ├── Type Validation
│   └── Content Verification
├── Backend Processing
│   ├── files.upload_file() API
│   ├── File Storage (uploads/)
│   ├── Database Record Creation
│   └── Metadata Extraction
└── Frontend State Update
    ├── uploadedFiles State
    ├── UI Feedback
    └── Session Context Update
```

### 3.2 File Storage Structure

```
uploads/
├── session_id/
│   ├── original_files/
│   │   ├── file1.csv
│   │   └── file2.csv
│   ├── processed_files/
│   │   ├── merged_data.csv
│   │   └── analysis_results.csv
│   └── metadata.json
```

## 4. Data Processing Flow

### 4.1 Intelligent Merge Process

```
Merge Request → intelligent_merge.execute_merge()
├── File Analysis
│   ├── Column Detection
│   ├── Data Type Inference
│   ├── Quality Assessment
│   └── Schema Analysis
├── Strategy Selection
│   ├── Join Key Detection
│   ├── Merge Strategy Suggestion
│   └── Confidence Scoring
├── Data Processing
│   ├── Data Cleaning
│   ├── Schema Alignment
│   ├── Duplicate Handling
│   └── Quality Validation
└── Result Generation
    ├── Merged Dataset
    ├── Statistics
    ├── Quality Report
    └── Download URL
```

### 4.2 Data Analysis Process

```
Analysis Request → data_qa.ask_question()
├── Data Context Loading
│   ├── Session Data Retrieval
│   ├── File Content Loading
│   └── Schema Understanding
├── Query Processing
│   ├── Natural Language Parsing
│   ├── SQL Query Generation
│   └── Query Optimization
├── Analysis Execution
│   ├── Statistical Analysis
│   ├── Pattern Detection
│   └── Insight Generation
└── Response Formatting
    ├── Structured Answer
    ├── Supporting Data
    ├── Confidence Metrics
    └── Follow-up Suggestions
```

### 4.3 Visualization Process

```
Visualization Request → handleVisualization()
├── Request Parsing
│   ├── Chart Type Detection
│   ├── Data Selection
│   └── Configuration Extraction
├── Data Preparation
│   ├── Data Filtering
│   ├── Aggregation
│   └── Format Conversion
├── Chart Generation
│   ├── Plotly.js Configuration
│   ├── Interactive Features
│   └── Responsive Design
└── Result Display
    ├── Chart Rendering
    ├── Controls
    └── Export Options
```

## 5. API Communication Flow

### 5.1 Frontend API Service Layer

```typescript
// api.ts - Centralized API communication
const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
});

// Service modules
export const bioMatcherApi = {
  createWorkflowSession,
  uploadFiles,
  mergeFiles,
  analyzeData
};

export const dataQaApi = {
  askQuestion,
  getDataPreview,
  getQuestionSuggestions
};

export const generalChatApi = {
  sendMessage,
  getResponse
};
```

### 5.2 Backend API Structure

```
/api/
├── /files
│   ├── POST /upload
│   ├── GET /list
│   └── DELETE /{file_id}
├── /intelligent-merge
│   ├── POST /analyze-files
│   ├── POST /execute-merge
│   └── POST /analyze-and-suggest
├── /data-qa
│   ├── POST /ask
│   ├── GET /preview/{session_id}
│   └── GET /suggestions/{session_id}
├── /workflows
│   ├── POST /create
│   ├── GET /list
│   └── GET /{workflow_id}
└── /general-chat
    └── POST /chat
```

## 6. Database Flow

### 6.1 Data Models

```python
# Core entities
Workflow
├── id, name, description, status
├── created_at, updated_at
└── workflow_metadata (JSON)

WorkflowStep
├── id, workflow_id, name, description
├── step_type, status, order_index
├── external_provider, external_config
└── created_at, updated_at

File
├── id, workflow_id, filename, file_path
├── file_type, file_size, upload_date
├── input_step_id, output_step_id
└── metadata (JSON)

Dataset
├── id, name, description, data_type
├── schema, statistics, quality_metrics
└── created_at, updated_at
```

### 6.2 Database Operations Flow

```
API Request → Database Operation
├── Session Management
│   ├── get_db() Dependency
│   ├── Transaction Handling
│   └── Connection Pooling
├── CRUD Operations
│   ├── Create Records
│   ├── Read Data
│   ├── Update States
│   └── Delete Resources
└── Response Generation
    ├── Data Serialization
    ├── Error Handling
    └── Status Codes
```

## 7. State Management Flow

### 7.1 Frontend State Structure

```typescript
// AIChatMain State
interface ChatState {
  messages: ChatMessage[];
  isProcessing: boolean;
  isListening: boolean;
  uploadedFiles: File[];
  currentSessionId: string | null;
  generatedFiles: GeneratedFile[];
  showWorkflowForm: boolean;
  workflowFormData: any;
  showSuggestions: boolean;
  showFilesModal: boolean;
}

// ChatMessage Structure
interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  result?: any;
}
```

### 7.2 State Update Flow

```
User Action → State Update → UI Re-render
├── Action Trigger
│   ├── User Input
│   ├── API Response
│   └── Timer/Event
├── State Modification
│   ├── useState Hook
│   ├── Immutable Updates
│   └── Side Effects
└── Component Re-render
    ├── Virtual DOM Diff
    ├── DOM Updates
    └── User Feedback
```

## 8. Result Display Flow

### 8.1 Result Processing

```
API Response → ResultPanel.renderResult()
├── Result Type Detection
│   ├── merged-data
│   ├── visualization
│   ├── analysis
│   ├── file-list
│   └── suggestions
├── Data Transformation
│   ├── Structure Validation
│   ├── Format Conversion
│   └── Error Handling
└── Component Rendering
    ├── Specialized Components
    ├── Interactive Features
    └── Export Options
```

### 8.2 Result Component Types

```typescript
// ResultPanel Component Structure
const renderResult = () => {
  switch (result.type) {
    case 'merged-data':
      return renderMergedData(result.data);
    case 'visualization':
      return renderVisualizationResult(result.data);
    case 'analysis':
      return renderAnalysisResult(result.data);
    case 'file-list':
      return renderFileList(result.data);
    case 'suggestions':
      return renderSuggestions(result.data);
    default:
      return renderFallback(result);
  }
};
```

## 9. Error Handling Flow

### 9.1 Frontend Error Handling

```
Error Occurrence → Error Handling
├── API Error Interception
│   ├── Network Errors
│   ├── HTTP Status Codes
│   └── Response Validation
├── User Feedback
│   ├── Error Messages
│   ├── Retry Options
│   └── Fallback Actions
└── State Recovery
    ├── Loading State Reset
    ├── Partial Data Display
    └── Session Continuity
```

### 9.2 Backend Error Handling

```
Exception → Error Response
├── Exception Catching
│   ├── HTTPException
│   ├── ValidationError
│   └── DatabaseError
├── Error Logging
│   ├── Structured Logging
│   ├── Error Context
│   └── Performance Metrics
└── Client Response
    ├── Error Status Code
    ├── Error Message
    └── Debug Information
```

## 10. Session Management Flow

### 10.1 Session Lifecycle

```
Session Creation → Session Usage → Session Cleanup
├── Session Initialization
│   ├── Unique ID Generation
│   ├── Context Setup
│   └── Resource Allocation
├── Session Persistence
│   ├── File Storage
│   ├── Database Records
│   └── Memory State
└── Session Termination
    ├── Resource Cleanup
    ├── Data Archival
    └── Context Destruction
```

### 10.2 Context Management

```typescript
// Session Context Structure
interface SessionContext {
  sessionId: string;
  uploadedFiles: File[];
  processedData: any[];
  workflowState: WorkflowState;
  userPreferences: UserPreferences;
  timestamp: Date;
}
```

## 11. Performance Optimization Flow

### 11.1 Frontend Optimizations

```
Performance Monitoring → Optimization
├── Component Optimization
│   ├── React.memo()
│   ├── useMemo()
│   └── useCallback()
├── Bundle Optimization
│   ├── Code Splitting
│   ├── Lazy Loading
│   └── Tree Shaking
└── Network Optimization
    ├── Request Caching
    ├── Response Compression
    └── Connection Pooling
```

### 11.2 Backend Optimizations

```
Request Processing → Performance Enhancement
├── Database Optimization
│   ├── Query Optimization
│   ├── Index Management
│   └── Connection Pooling
├── Caching Strategy
│   ├── Response Caching
│   ├── Data Caching
│   └── Session Caching
└── Async Processing
    ├── Background Tasks
    ├── Queue Management
    └── Resource Scaling
```

## 12. Security Flow

### 12.1 Input Validation

```
User Input → Security Validation
├── Input Sanitization
│   ├── XSS Prevention
│   ├── SQL Injection Prevention
│   └── File Upload Validation
├── Authentication
│   ├── Session Validation
│   ├── Token Verification
│   └── Permission Checks
└── Authorization
    ├── Resource Access Control
    ├── Operation Permissions
    └── Data Privacy
```

### 12.2 Data Protection

```
Data Processing → Security Measures
├── Data Encryption
│   ├── In-Transit Encryption
│   ├── At-Rest Encryption
│   └── Key Management
├── Access Control
│   ├── Role-Based Access
│   ├── Resource Isolation
│   └── Audit Logging
└── Compliance
    ├── Data Retention
    ├── Privacy Controls
    └── Regulatory Adherence
```

## 13. End-to-End Workflow Example

### 13.1 Complete Merge Workflow

```
1. User Uploads Files
   ├── Frontend: File selection and upload
   ├── Backend: File storage and validation
   └── Database: File metadata storage

2. User Requests Merge
   ├── Frontend: Natural language parsing
   ├── Backend: File analysis and strategy selection
   └── Database: Workflow state tracking

3. Data Processing
   ├── Backend: Intelligent merge execution
   ├── Processing: Data cleaning and alignment
   └── Storage: Result file generation

4. Result Display
   ├── Backend: Response formatting
   ├── Frontend: Result component rendering
   └── UI: Interactive data table display

5. User Interaction
   ├── Download: Merged file export
   ├── Analysis: Further data exploration
   └── Visualization: Chart generation
```

### 13.2 Data Flow Diagram

```
User Input
    ↓
Natural Language Processing
    ↓
Command Classification
    ↓
API Request Formation
    ↓
Backend Processing
    ↓
Database Operations
    ↓
Data Processing/Transformation
    ↓
Result Generation
    ↓
API Response
    ↓
Frontend State Update
    ↓
UI Component Rendering
    ↓
User Feedback
```

## 14. Monitoring and Debugging

### 14.1 Logging Strategy

```
Application Events → Logging Pipeline
├── Frontend Logging
│   ├── User Interactions
│   ├── API Calls
│   └── Error Events
├── Backend Logging
│   ├── Request/Response
│   ├── Database Operations
│   └── Performance Metrics
└── System Monitoring
    ├── Resource Usage
    ├── Error Rates
    └── Response Times
```

### 14.2 Debug Tools

```
Debugging Infrastructure
├── Frontend Debug
│   ├── React DevTools
│   ├── Browser Console
│   └── Network Inspector
├── Backend Debug
│   ├── API Documentation
│   ├── Database Queries
│   └── Performance Profiling
└── Integration Debug
    ├── End-to-End Testing
    ├── API Testing
    └── Load Testing
```

This comprehensive documentation provides a complete understanding of the data and control flow in the DataWeaver.AI application, enabling developers to understand, maintain, and extend the system effectively. 