# DataWeaver.AI API Documentation

## Overview

The DataWeaver.AI API provides endpoints for data processing, file management, workflow automation, and AI-powered analysis. The API is built with FastAPI and supports both synchronous and asynchronous operations.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.dataweaver.ai`

## Authentication

Currently, the API operates without authentication for development. Production deployments will include API key authentication.

## Response Format

All API responses follow this standard format:

```json
{
  "data": {...},
  "message": "Success message",
  "status": "success"
}
```

Error responses:

```json
{
  "detail": "Error description",
  "status_code": 400,
  "error_type": "validation_error"
}
```

## Core Endpoints

### Session Management

#### Create Workflow Session
```http
POST /api/bio/create-workflow-session
```

Creates a new workflow session for data processing.

**Response:**
```json
{
  "session_id": "uuid-string",
  "message": "Session created successfully"
}
```

#### Clear Session
```http
DELETE /api/bio/clear-session/{session_id}
```

Clears all data from a session.

**Response:**
```json
{
  "session_id": "uuid-string",
  "message": "Session cleared successfully"
}
```

#### Get Workflow Status
```http
GET /api/bio/workflow-status/{session_id}
```

Returns the current status of a workflow session.

**Response:**
```json
{
  "session_id": "uuid-string",
  "created_at": "2024-01-01T00:00:00Z",
  "last_updated": "2024-01-01T00:00:00Z",
  "steps": [...],
  "has_merged_data": true,
  "has_visualization_data": false
}
```

### File Operations

#### Upload Single File
```http
POST /api/bio/upload-single-file
```

Upload a single CSV file to a session.

**Request:**
- `file`: CSV file (multipart/form-data)
- `session_id`: Session ID (optional)

**Response:**
```json
{
  "headers": ["column1", "column2"],
  "rows": [[value1, value2]],
  "totalRows": 100,
  "matchedRows": 100,
  "unmatchedRows": 0,
  "session_id": "uuid-string",
  "workflow_step": "upload_single_file",
  "filename": "data.csv"
}
```

#### Merge Session Files
```http
POST /api/bio/merge-session-files
```

Merge all uploaded files in a session.

**Request:**
- `session_id`: Session ID (required)

**Response:**
```json
{
  "headers": ["id", "col1", "col2", "col3"],
  "rows": [[1, "a", "b", "c"]],
  "totalRows": 100,
  "matchedRows": 95,
  "unmatchedRows": 5,
  "session_id": "uuid-string",
  "workflow_step": "merge_session_files",
  "merge_column": "id",
  "common_columns": ["id"],
  "message": "Successfully merged session files"
}
```

#### Merge Files (Direct)
```http
POST /api/bio/merge-files
```

Merge multiple files uploaded in a single request.

**Request:**
- `files`: Multiple CSV files (multipart/form-data)
- `session_id`: Session ID (optional)

**Response:** Same as merge session files

### Data Analysis

#### Generate Visualization
```http
POST /api/bio/generate-visualization
```

Generate charts from data.

**Request:**
- `file`: CSV file (optional)
- `session_id`: Session ID (optional)
- `plot_type`: Chart type (scatter, histogram, correlation, boxplot)
- `x_column`: X-axis column (optional)
- `y_column`: Y-axis column (optional)
- `use_session_data`: Use session data (boolean)

**Response:**
```json
{
  "plot_type": "scatter",
  "plot_json": "{...}",
  "columns": ["x", "y"],
  "data_shape": [100, 2],
  "numeric_columns": ["x", "y"],
  "session_id": "uuid-string",
  "workflow_step": "generate_visualization"
}
```

#### Explain Visualization
```http
POST /api/bio/explain-visualization
```

Get AI explanation of a visualization.

**Request:**
- `session_id`: Session ID (required)
- `plot_type`: Chart type (optional)
- `x_column`: X-axis column (optional)
- `y_column`: Y-axis column (optional)

**Response:**
```json
{
  "plot_type": "scatter",
  "data_shape": [100, 2],
  "analysis": {
    "trends": ["Positive correlation between x and y"],
    "correlations": [...],
    "outliers": [...],
    "insights": [...]
  },
  "session_id": "uuid-string"
}
```

#### Analyze Data
```http
POST /api/bio/analyze-data
```

Perform comprehensive data analysis.

**Request:**
- `file`: CSV file (optional)
- `session_id`: Session ID (optional)
- `use_session_data`: Use session data (boolean)

**Response:**
```json
{
  "dataset_info": {...},
  "insights": [...],
  "quality_analysis": {...},
  "statistical_analysis": {...},
  "correlation_analysis": {...},
  "pattern_analysis": {...},
  "recommendations": [...],
  "session_id": "uuid-string"
}
```

### Data Q&A

#### Ask Question
```http
POST /api/data-qa/ask
```

Ask questions about your data.

**Request:**
- `question`: Your question (required)
- `session_id`: Session ID (required)

**Response:**
```json
{
  "answer": "Answer to your question",
  "confidence": "high",
  "data_points": [...],
  "session_id": "uuid-string"
}
```

#### Get Suggestions
```http
GET /api/data-qa/suggestions/{session_id}
```

Get suggested questions based on your data.

**Response:**
```json
{
  "suggestions": [
    "What columns are in the data?",
    "Are there any missing values?",
    "What is the correlation between x and y?"
  ]
}
```

### AI Chat

#### General Chat
```http
POST /api/general-chat/chat
```

General AI chat for data-related questions.

**Request:**
- `message`: Your message (required)
- `session_id`: Session ID (optional)
- `context`: Additional context (optional)

**Response:**
```json
{
  "response": "AI response",
  "suggestions": [...],
  "confidence": "high",
  "context": {...}
}
```

### Biological Entities

#### Upload Test Results
```http
POST /api/bio/upload-test-results
```

Upload biological assay results.

**Request:**
- `file`: CSV file (required)
- `test_type`: Type of test (optional)
- `assay_name`: Assay name (optional)
- `protocol`: Protocol description (optional)

**Response:**
```json
{
  "total_rows": 100,
  "matched_rows": 95,
  "unmatched_rows": 5,
  "high_confidence": 80,
  "medium_confidence": 15,
  "low_confidence": 0,
  "matches": [...],
  "errors": [...]
}
```

#### Get Designs
```http
GET /api/bio/designs
```

Get all biological designs.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Design Name",
    "sequence": "ATCG...",
    "mutations": "L72F,R80K"
  }
]
```

#### Get Builds
```http
GET /api/bio/builds
```

Get all biological builds.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Build Name",
    "design_id": "uuid",
    "construct_type": "plasmid"
  }
]
```

#### Get Tests
```http
GET /api/bio/tests
```

Get all biological tests.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Test Name",
    "test_type": "activity",
    "result_value": 25.0,
    "design_id": "uuid",
    "build_id": "uuid"
  }
]
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Resource not found |
| 422 | Validation Error - Invalid data format |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Service temporarily unavailable |

## Rate Limiting

Currently, no rate limiting is implemented. Production deployments will include rate limiting based on API keys.

## File Upload Limits

- **Maximum file size**: 10MB
- **Supported formats**: CSV, JSON, Excel (basic)
- **Encoding**: UTF-8 recommended

## Session Management

- **Session timeout**: 24 hours
- **Maximum files per session**: No limit (memory dependent)
- **Session data**: Automatically cleaned up on timeout

## Examples

### Complete Workflow Example

```bash
# 1. Create session
curl -X POST "http://localhost:8000/api/bio/create-workflow-session"

# 2. Upload files
curl -X POST "http://localhost:8000/api/bio/upload-single-file" \
  -F "file=@data1.csv" \
  -F "session_id=your-session-id"

curl -X POST "http://localhost:8000/api/bio/upload-single-file" \
  -F "file=@data2.csv" \
  -F "session_id=your-session-id"

# 3. Merge files
curl -X POST "http://localhost:8000/api/bio/merge-session-files" \
  -F "session_id=your-session-id"

# 4. Generate visualization
curl -X POST "http://localhost:8000/api/bio/generate-visualization" \
  -F "session_id=your-session-id" \
  -F "plot_type=scatter" \
  -F "use_session_data=true"

# 5. Ask questions
curl -X POST "http://localhost:8000/api/data-qa/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What columns are in the data?", "session_id": "your-session-id"}'
```

### Python Example

```python
import requests

# Create session
response = requests.post("http://localhost:8000/api/bio/create-workflow-session")
session_id = response.json()["session_id"]

# Upload file
with open("data.csv", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/bio/upload-single-file",
        files={"file": f},
        data={"session_id": session_id}
    )

# Merge files
response = requests.post(
    "http://localhost:8000/api/bio/merge-session-files",
    data={"session_id": session_id}
)

# Generate visualization
response = requests.post(
    "http://localhost:8000/api/bio/generate-visualization",
    data={
        "session_id": session_id,
        "plot_type": "scatter",
        "use_session_data": True
    }
)
```

## SDKs and Libraries

### Python
```python
pip install requests
```

### JavaScript/Node.js
```javascript
npm install axios
```

### cURL
Available on most systems by default.

## OpenAPI Specification

The complete API specification is available in multiple formats:

- **YAML Format**: `docs/openapi.yaml`
- **JSON Format**: `docs/openapi.json`
- **Interactive Docs**: Visit `http://localhost:8000/docs` when the server is running

### Using the OpenAPI Spec

#### Generate Client Libraries
```bash
# Using openapi-generator-cli
npx @openapitools/openapi-generator-cli generate \
  -i docs/openapi.yaml \
  -g python \
  -o ./generated/python-client

# Using swagger-codegen
swagger-codegen generate \
  -i docs/openapi.yaml \
  -l python \
  -o ./generated/python-client
```

#### Import into API Testing Tools
- **Postman**: Import `docs/openapi.yaml`
- **Insomnia**: Import `docs/openapi.yaml`
- **Swagger UI**: Use the interactive docs at `/docs`

## Support

For API support:
- **Documentation**: This file and `/docs` endpoint
- **OpenAPI Spec**: `docs/openapi.yaml` and `docs/openapi.json`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions 