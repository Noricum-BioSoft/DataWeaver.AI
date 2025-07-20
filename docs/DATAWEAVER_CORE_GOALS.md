# DataWeaver.AI Core Goals & Architecture

## Overview

DataWeaver.AI is a comprehensive data management system designed to enable **step-by-step execution of generic workflows using natural language commands** and **automatic merging of data used and generated across workflows**.

## Core Goals

### 1. Natural Language Workflow Execution
- **Goal**: Enable users to execute workflows using natural language commands
- **Implementation**: 
  - Natural language command parsing and interpretation
  - Step-by-step workflow execution with real-time feedback
  - Command history and execution tracking
  - Error handling and recovery mechanisms

### 2. Automatic Data Merging
- **Goal**: Automatically merge data that is used and generated across workflows
- **Implementation**:
  - Data lineage tracking across workflow steps
  - Automatic identification of related datasets
  - Intelligent merging strategies based on data types
  - Relationship mapping between input and output files

## System Architecture

### Backend Components

#### 1. Workflow Management
```python
# Core workflow entities
- Workflow: Main workflow container
- WorkflowStep: Individual execution steps
- WorkflowExecution: Execution history and state
```

#### 2. Natural Language Processing
```python
# Command interpretation and execution
- CommandParser: Parse natural language into executable actions
- CommandExecutor: Execute parsed commands against workflows
- CommandHistory: Track command execution and results
```

#### 3. Data Management
```python
# Data tracking and merging
- DataLineage: Track data flow through workflows
- DataMerger: Automatic merging of related datasets
- FileRelationships: Map relationships between files
```

#### 4. File Management
```python
# File handling and metadata
- FileService: Upload, storage, and retrieval
- FileMetadata: Flexible metadata storage
- FileRelationships: Track file dependencies
```

### Frontend Components

#### 1. AI Chat Interface
- **Natural Language Input**: Chat-based command interface
- **Real-time Feedback**: Live execution status and results
- **Command History**: Browse and replay previous commands
- **Workflow Visualization**: Visual representation of workflow state

#### 2. Workflow Dashboard
- **Workflow Management**: Create, edit, and monitor workflows
- **Step Execution**: Individual step control and monitoring
- **Data Lineage**: Visual data flow tracking
- **File Management**: Upload, organize, and track files

#### 3. Data Explorer
- **Dataset Browsing**: Browse and search datasets
- **Relationship Mapping**: Visual data relationships
- **Merge Preview**: Preview automatic merges
- **Export Tools**: Export merged datasets

## API Endpoints

### Workflow Management
- `GET /api/workflows` - List all workflows
- `POST /api/workflows` - Create new workflow
- `GET /api/workflows/{id}` - Get workflow details
- `PUT /api/workflows/{id}` - Update workflow
- `DELETE /api/workflows/{id}` - Delete workflow

### Natural Language Commands
- `POST /api/workflows/{id}/execute` - Execute natural language command
- `GET /api/workflows/{id}/history` - Get command execution history
- `GET /api/workflows/{id}/lineage` - Get data lineage information

### Data Management
- `POST /api/workflows/{id}/merge` - Auto-merge workflow data
- `GET /api/files/workflow/{id}` - Get workflow files
- `POST /api/files/upload/{workflow_id}` - Upload file to workflow
- `GET /api/files/{id}/relationships` - Get file relationships

### File Management
- `POST /api/files/upload/{workflow_id}` - Upload file
- `GET /api/files/{id}` - Get file metadata
- `GET /api/files/{id}/download` - Download file
- `DELETE /api/files/{id}` - Delete file

## Data Models

### Core Entities
```python
class Workflow:
    id: int
    name: str
    description: str
    status: WorkflowStatus
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

class WorkflowStep:
    id: int
    workflow_id: int
    name: str
    description: str
    step_type: StepType
    status: StepStatus
    order_index: int
    external_config: Dict[str, Any]

class File:
    id: int
    filename: str
    file_path: str
    file_size: int
    file_type: FileType
    workflow_id: int
    step_id: Optional[int]
    parent_file_id: Optional[int]
    status: FileStatus
    metadata: Dict[str, Any]

class FileRelationship:
    id: int
    source_file_id: int
    target_file_id: int
    relationship_type: str
    confidence_score: float
    metadata: Dict[str, Any]
```

## Natural Language Command Examples

### Workflow Management
```
"Create a new workflow called 'Data Analysis Pipeline'"
"Add a data cleaning step to workflow 123"
"Run the next step in workflow 123"
"Show me the status of workflow 123"
```

### Data Operations
```
"Upload the sales data CSV file"
"Merge the customer and order datasets"
"Export the merged results as JSON"
"Show me the data lineage for workflow 123"
```

### File Management
```
"List all files in workflow 123"
"Download the processed data file"
"Show me the relationships between files"
"Delete the temporary files"
```

## Data Merging Strategies

### 1. Schema-Based Merging
- **Column Matching**: Match columns by name and type
- **Key-Based Joins**: Use common keys for merging
- **Schema Inference**: Automatically infer relationships

### 2. Content-Based Merging
- **Similarity Matching**: Find similar datasets
- **Pattern Recognition**: Identify common patterns
- **Semantic Analysis**: Understand data meaning

### 3. Temporal Merging
- **Time-Based**: Merge by timestamps
- **Version Tracking**: Track data versions
- **Change Detection**: Identify data changes

## Implementation Priorities

### Phase 1: Core Infrastructure
1. **Workflow Management**: Basic workflow CRUD operations
2. **File Management**: File upload, storage, and metadata
3. **Natural Language Interface**: Basic command parsing
4. **Data Lineage**: Track file relationships

### Phase 2: Advanced Features
1. **Intelligent Merging**: Automatic data merging algorithms
2. **Command History**: Advanced command tracking
3. **Visualization**: Data lineage and workflow visualization
4. **Error Recovery**: Robust error handling

### Phase 3: Optimization
1. **Performance**: Optimize for large datasets
2. **Scalability**: Support multiple concurrent workflows
3. **Integration**: Connect with external data sources
4. **Advanced NLP**: More sophisticated command interpretation

## Success Metrics

### Technical Metrics
- **Command Accuracy**: >95% successful command interpretation
- **Merge Accuracy**: >90% correct automatic merges
- **Performance**: <5 seconds for command execution
- **Scalability**: Support 100+ concurrent workflows

### User Experience Metrics
- **Workflow Completion Rate**: >80%
- **User Satisfaction**: >4.5/5 rating
- **Time to Results**: <10 minutes for typical workflows
- **Learning Curve**: New users productive within 1 hour

## Future Enhancements

### Advanced Natural Language Processing
- **Context Awareness**: Understand workflow context
- **Multi-step Commands**: Execute complex multi-step operations
- **Learning**: Improve from user interactions
- **Voice Interface**: Voice command support

### Advanced Data Management
- **Real-time Merging**: Live data merging capabilities
- **Predictive Merging**: Anticipate data relationships
- **Quality Assessment**: Automatic data quality scoring
- **Version Control**: Advanced versioning and rollbacks

### Collaboration Features
- **Multi-user Workflows**: Collaborative workflow execution
- **Sharing**: Share workflows and results
- **Templates**: Reusable workflow templates
- **Integration**: Connect with external tools and platforms 