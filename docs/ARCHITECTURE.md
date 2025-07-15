# DataWeaver.AI Architecture

## Overview

DataWeaver.AI is a comprehensive data management system designed for workflow-based applications. It provides automatic dataset linking, file management, and workflow tracking capabilities.

## System Architecture

### Backend (FastAPI + PostgreSQL)

#### Database Schema

**Core Tables:**

1. **workflows** - Main workflow entities
   - `id` (Primary Key)
   - `name` (String)
   - `description` (Text)
   - `status` (Enum: DRAFT, RUNNING, COMPLETED, FAILED, CANCELLED)
   - `created_at`, `updated_at` (Timestamps)
   - `metadata` (JSON for flexible data)

2. **workflow_steps** - Individual steps within workflows
   - `id` (Primary Key)
   - `workflow_id` (Foreign Key)
   - `name`, `description` (String/Text)
   - `step_type` (Enum: INPUT, PROCESSING, OUTPUT, EXTERNAL)
   - `status` (Enum: PENDING, RUNNING, COMPLETED, FAILED, SKIPPED)
   - `order_index` (Integer for step ordering)
   - `external_provider`, `external_config` (For external API integration)

3. **files** - File storage and metadata
   - `id` (Primary Key)
   - `filename`, `original_filename` (String)
   - `file_path` (String - relative path in storage)
   - `file_size`, `file_type`, `mime_type`
   - `status` (Enum: UPLOADING, PROCESSING, READY, ERROR, DELETED)
   - `workflow_id`, `input_step_id`, `output_step_id` (Foreign Keys)
   - `parent_file_id` (Self-referencing for file relationships)

4. **file_metadata** - Flexible metadata storage
   - `id` (Primary Key)
   - `file_id` (Foreign Key)
   - `key`, `value`, `data_type` (Flexible key-value storage)

5. **file_relationships** - Track relationships between files
   - `id` (Primary Key)
   - `file_id`, `related_file_id` (Foreign Keys)
   - `relationship_type` (String)
   - `confidence_score` (Integer 0-100)

6. **datasets** - External dataset tracking
   - `id` (Primary Key)
   - `name`, `description` (String/Text)
   - `source_provider`, `source_file_path` (String)
   - `status` (Enum: PENDING, PROCESSING, MATCHED, UNMATCHED, ERROR)
   - `identifiers`, `matching_config` (JSON)
   - `row_count`, `column_count`, `file_size` (Metadata)

7. **dataset_matches** - Automatic matching results
   - `id` (Primary Key)
   - `dataset_id`, `workflow_id`, `step_id`, `file_id` (Foreign Keys)
   - `match_type` (Enum: EXACT, FUZZY, ML_BASED, MANUAL)
   - `confidence_score` (Float 0.0-1.0)
   - `matching_criteria`, `matched_identifiers` (JSON)
   - `is_confirmed` (Integer: 0=pending, 1=confirmed, -1=rejected)

#### File Storage Structure

```
storage/
├── workflow_1/
│   ├── step_1/
│   │   ├── uuid1.csv
│   │   └── uuid2.xlsx
│   └── step_2/
│       └── uuid3.json
├── workflow_2/
│   └── step_1/
│       └── uuid4.csv
└── temp_uploads/
    └── temp_dataset.csv
```

### Frontend (React + TypeScript)

#### Component Architecture

1. **App.tsx** - Main application with routing
2. **WorkflowList.tsx** - Workflow management interface
3. **FileUpload.tsx** - Drag-and-drop file upload
4. **DatasetMatching.tsx** - Automatic dataset linking

#### State Management

- React Query for server state
- Local state for UI interactions
- Context for global state (if needed)

## Automatic Dataset Linking

### Matching Strategies

1. **Exact Matching**
   - Column name matches
   - Identifier value matches
   - Perfect confidence score (1.0)

2. **Fuzzy Matching**
   - String similarity using Levenshtein distance
   - Configurable threshold (default: 0.8)
   - Column name and value comparison

3. **ML-Based Matching**
   - TF-IDF vectorization of file content
   - Cosine similarity scoring
   - Lower threshold for ML matches (0.3)

### Matching Process

1. **Dataset Upload**
   - File uploaded to `/datasets/process`
   - Identifiers extracted automatically
   - Metadata stored in database

2. **Automatic Matching**
   - System scans all workflows
   - Compares identifiers using multiple strategies
   - Generates confidence scores
   - Stores matches in `dataset_matches` table

3. **User Confirmation**
   - Matches displayed in UI
   - Users can confirm/reject matches
   - Confirmation status tracked

## API Endpoints

### Workflows
- `GET /api/v1/workflows` - List workflows
- `POST /api/v1/workflows` - Create workflow
- `GET /api/v1/workflows/{id}` - Get workflow
- `PUT /api/v1/workflows/{id}` - Update workflow
- `DELETE /api/v1/workflows/{id}` - Delete workflow

### Workflow Steps
- `GET /api/v1/workflows/{id}/steps` - List steps
- `POST /api/v1/workflows/{id}/steps` - Create step
- `PUT /api/v1/workflows/{id}/steps/{step_id}` - Update step
- `DELETE /api/v1/workflows/{id}/steps/{step_id}` - Delete step

### Files
- `POST /api/v1/files/upload/{workflow_id}` - Upload file
- `GET /api/v1/files/{id}` - Get file metadata
- `GET /api/v1/files/{id}/download` - Download file
- `DELETE /api/v1/files/{id}` - Delete file
- `GET /api/v1/files/workflow/{workflow_id}` - Get workflow files

### Datasets
- `POST /api/v1/datasets/process` - Process uploaded dataset
- `POST /api/v1/datasets/{id}/auto-match` - Auto-match dataset
- `GET /api/v1/datasets/{id}/matches` - Get dataset matches
- `PUT /api/v1/datasets/matches/{id}/confirm` - Confirm match
- `PUT /api/v1/datasets/matches/{id}/reject` - Reject match

## Scaling Considerations

### Performance Optimizations

1. **File Storage**
   - Structured directory hierarchy
   - Unique filenames to prevent conflicts
   - Metadata extraction for quick queries

2. **Database**
   - Indexes on foreign keys and frequently queried fields
   - JSON fields for flexible metadata
   - Efficient relationship tracking

3. **Matching Algorithm**
   - Configurable thresholds
   - Multiple matching strategies
   - Confidence scoring for quality control

### Scalability Features

1. **Large File Support**
   - Streaming file uploads
   - Chunked processing
   - Background task processing

2. **Parallel Workflows**
   - Independent workflow execution
   - Step-level parallelism
   - Resource isolation

3. **External Integrations**
   - Provider-specific configurations
   - API rate limiting
   - Retry mechanisms

## Security Considerations

1. **File Upload Security**
   - File type validation
   - Size limits
   - Virus scanning (future)

2. **API Security**
   - Input validation
   - SQL injection prevention
   - CORS configuration

3. **Data Privacy**
   - Secure file storage
   - Access control
   - Audit logging

## Deployment

### Backend Deployment
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment
```bash
# Install dependencies
cd frontend
npm install

# Build for production
npm run build

# Serve static files
npx serve -s build
```

### Environment Variables
```bash
# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/dataweaver
STORAGE_PATH=/path/to/storage
LOG_LEVEL=INFO

# Frontend
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Future Enhancements

1. **Advanced Matching**
   - Machine learning models
   - Custom matching rules
   - Batch processing

2. **Workflow Engine**
   - Step dependencies
   - Conditional execution
   - Error handling

3. **Monitoring**
   - Performance metrics
   - Error tracking
   - Usage analytics

4. **Integration**
   - External APIs
   - Cloud storage
   - Message queues 