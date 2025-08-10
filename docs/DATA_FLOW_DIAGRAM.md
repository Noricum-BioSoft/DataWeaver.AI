# DataWeaver.AI Data Flow Diagram

## High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend (React)"
        UI[User Interface]
        CHAT[Chat Components]
        RESULT[Result Panel]
        STATE[State Management]
    end
    
    subgraph "Backend (FastAPI)"
        API[API Gateway]
        MERGE[Intelligent Merge]
        QA[Data Q&A]
        ANALYZE[Data Analysis]
        FILES[File Management]
    end
    
    subgraph "Database (PostgreSQL)"
        DB[(Database)]
        WORKFLOW[(Workflows)]
        FILES_DB[(Files)]
        SESSIONS[(Sessions)]
    end
    
    subgraph "External Services"
        LLM[LLM Services]
        STORAGE[File Storage]
    end
    
    UI --> CHAT
    CHAT --> API
    API --> MERGE
    API --> QA
    API --> ANALYZE
    API --> FILES
    MERGE --> DB
    QA --> DB
    ANALYZE --> DB
    FILES --> DB
    API --> LLM
    FILES --> STORAGE
    RESULT --> STATE
    STATE --> CHAT
```

## User Interaction Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant D as Database
    participant S as Storage
    
    U->>F: Upload Files
    F->>B: POST /api/files/upload
    B->>S: Store Files
    B->>D: Save File Metadata
    B->>F: Return File IDs
    F->>U: Show Upload Success
    
    U->>F: "Merge the files"
    F->>B: POST /api/intelligent-merge/execute
    B->>D: Get File Data
    B->>B: Analyze & Merge
    B->>S: Store Result
    B->>D: Save Workflow
    B->>F: Return Merged Data
    F->>U: Display Results
```

## Data Processing Pipeline

```mermaid
flowchart TD
    A[User Input] --> B{Command Type}
    
    B -->|Merge| C[File Analysis]
    B -->|Q&A| D[Data Context]
    B -->|Visualize| E[Chart Generation]
    B -->|Analyze| F[Statistical Analysis]
    
    C --> G[Strategy Selection]
    G --> H[Data Processing]
    H --> I[Quality Validation]
    I --> J[Result Generation]
    
    D --> K[Query Processing]
    K --> L[Analysis Execution]
    L --> M[Response Formatting]
    
    E --> N[Data Preparation]
    N --> O[Chart Configuration]
    O --> P[Interactive Display]
    
    F --> Q[Pattern Detection]
    Q --> R[Insight Generation]
    R --> S[Report Creation]
    
    J --> T[API Response]
    M --> T
    P --> T
    S --> T
    
    T --> U[Frontend State]
    U --> V[UI Rendering]
    V --> W[User Feedback]
```

## State Management Flow

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: User Input
    Processing --> FileUpload: Upload Files
    Processing --> DataAnalysis: Analyze Request
    Processing --> MergeRequest: Merge Request
    Processing --> Visualization: Chart Request
    
    FileUpload --> FileStored: Files Saved
    FileStored --> Idle: Return to Chat
    
    DataAnalysis --> AnalysisComplete: Results Ready
    AnalysisComplete --> Idle: Display Results
    
    MergeRequest --> MergeComplete: Merge Done
    MergeComplete --> Idle: Show Merged Data
    
    Visualization --> ChartReady: Chart Generated
    ChartReady --> Idle: Display Chart
    
    Processing --> Error: Error Occurred
    Error --> Idle: Show Error Message
```

## API Communication Flow

```mermaid
graph LR
    subgraph "Frontend API Layer"
        A[api.ts]
        B[bioMatcherApi]
        C[dataQaApi]
        D[generalChatApi]
    end
    
    subgraph "Backend API Routes"
        E[/api/files]
        F[/api/intelligent-merge]
        G[/api/data-qa]
        H[/api/workflows]
        I[/api/general-chat]
    end
    
    subgraph "Backend Services"
        J[IntelligentMerger]
        K[DataQAService]
        L[FileService]
        M[WorkflowService]
    end
    
    A --> B
    A --> C
    A --> D
    
    B --> E
    B --> F
    C --> G
    D --> I
    
    E --> L
    F --> J
    G --> K
    H --> M
    I --> K
```

## Database Schema Flow

```mermaid
erDiagram
    WORKFLOW ||--o{ WORKFLOW_STEP : contains
    WORKFLOW ||--o{ FILE : has
    WORKFLOW_STEP ||--o{ FILE : produces
    WORKFLOW_STEP ||--o{ FILE : consumes
    
    WORKFLOW {
        int id PK
        string name
        string description
        enum status
        datetime created_at
        datetime updated_at
        json workflow_metadata
    }
    
    WORKFLOW_STEP {
        int id PK
        int workflow_id FK
        string name
        string description
        enum step_type
        enum status
        int order_index
        string external_provider
        json external_config
        datetime created_at
        datetime updated_at
    }
    
    FILE {
        int id PK
        int workflow_id FK
        string filename
        string file_path
        string file_type
        int file_size
        datetime upload_date
        int input_step_id FK
        int output_step_id FK
        json metadata
    }
    
    DATASET {
        int id PK
        string name
        string description
        string data_type
        json schema
        json statistics
        json quality_metrics
        datetime created_at
        datetime updated_at
    }
```

## Error Handling Flow

```mermaid
flowchart TD
    A[Request] --> B{Validation}
    B -->|Pass| C[Process Request]
    B -->|Fail| D[Return 400 Error]
    
    C --> E{Processing}
    E -->|Success| F[Return Response]
    E -->|Error| G[Log Error]
    
    G --> H{Error Type}
    H -->|Network| I[Retry Logic]
    H -->|Database| J[Rollback Transaction]
    H -->|Validation| K[Return 422 Error]
    H -->|Server| L[Return 500 Error]
    
    I --> M{Retry Count}
    M -->|< 3| C
    M -->|>= 3| N[Return Timeout Error]
    
    J --> O[Return Database Error]
    K --> P[Return Validation Details]
    L --> Q[Return Generic Error]
```

## Performance Monitoring Flow

```mermaid
graph TD
    A[Request Start] --> B[Start Timer]
    B --> C[Process Request]
    C --> D[End Timer]
    D --> E[Log Metrics]
    
    E --> F{Performance Check}
    F -->|Good| G[Continue]
    F -->|Slow| H[Alert]
    F -->|Error| I[Error Log]
    
    H --> J[Performance Analysis]
    J --> K[Optimization Suggestions]
    
    I --> L[Error Analysis]
    L --> M[Debug Information]
    
    G --> N[Response Sent]
    H --> N
    I --> N
```

## Security Flow

```mermaid
flowchart TD
    A[User Input] --> B[Input Sanitization]
    B --> C[Authentication Check]
    C --> D{Authenticated?}
    
    D -->|Yes| E[Authorization Check]
    D -->|No| F[Return 401]
    
    E --> G{Authorized?}
    G -->|Yes| H[Process Request]
    G -->|No| I[Return 403]
    
    H --> J[Data Encryption]
    J --> K[Secure Processing]
    K --> L[Response Encryption]
    L --> M[Secure Response]
    
    F --> N[Error Response]
    I --> N
    M --> O[Client]
    N --> O
```

## Session Management Flow

```mermaid
stateDiagram-v2
    [*] --> NoSession
    NoSession --> SessionCreated: Create Session
    SessionCreated --> FilesUploaded: Upload Files
    FilesUploaded --> Processing: Start Workflow
    Processing --> ResultsReady: Complete Processing
    ResultsReady --> SessionActive: Continue Session
    SessionActive --> Processing: New Request
    SessionActive --> SessionExpired: Timeout
    SessionExpired --> NoSession: Cleanup
    ResultsReady --> SessionEnded: User Ends
    SessionEnded --> NoSession: Cleanup
```

This visual documentation provides a clear understanding of how data flows through the DataWeaver.AI application, making it easier for developers to understand the system architecture and data processing pipeline. 