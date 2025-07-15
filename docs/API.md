# DataWeaver.AI API Documentation

## Overview

The DataWeaver.AI API provides endpoints for data processing, visualization, workflow management, and biological entity handling.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API operates without authentication for development purposes.

## Endpoints

### 🔄 Workflow Management

#### Create Workflow
```http
POST /workflows/
```

**Request Body:**
```json
{
  "name": "Protein Analysis Pipeline",
  "description": "Complete workflow for protein sequence analysis",
  "status": "draft"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Protein Analysis Pipeline",
  "description": "Complete workflow for protein sequence analysis",
  "status": "draft",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Get Workflows
```http
GET /workflows/
```

#### Get Workflow by ID
```http
GET /workflows/{workflow_id}
```

#### Add Workflow Step
```http
POST /workflows/{workflow_id}/steps/
```

**Request Body:**
```json
{
  "name": "Sequence Upload",
  "description": "Upload protein sequence files",
  "step_type": "input",
  "order_index": 1
}
```

### 📁 File Management

#### Upload File
```http
POST /files/upload/{workflow_id}
```

**Form Data:**
- `file`: File to upload
- `step_id`: ID of the workflow step

#### Get Files
```http
GET /files/
```

#### Get File by ID
```http
GET /files/{file_id}
```

### 🧬 Biological Entity Management

#### Create Design Entity
```http
POST /api/bio/designs
```

**Request Body:**
```json
{
  "name": "WT_Protein",
  "alias": "Wild_Type",
  "description": "Wild type protein sequence",
  "sequence": "MGT...L72...K",
  "sequence_type": "protein",
  "mutation_list": "",
  "generation": 0
}
```

#### Create Build Entity
```http
POST /api/bio/builds
```

**Request Body:**
```json
{
  "name": "Mutant_L72F",
  "alias": "L72F_Mutant",
  "description": "L72F mutation variant",
  "sequence": "MGT...L72F...K",
  "sequence_type": "protein",
  "mutation_list": "L72F",
  "design_id": "design-uuid-here",
  "construct_type": "plasmid",
  "build_status": "completed"
}
```

#### Upload Test Results
```http
POST /api/bio/upload-test-results
```

**Form Data:**
- `file`: CSV file with test results
- `test_type`: Type of test (e.g., "activity")
- `assay_name`: Name of the assay

### 🔗 Data Processing

#### Merge Files
```http
POST /api/bio/merge-files
```

**Form Data:**
- `file1`: First CSV file
- `file2`: Second CSV file

**Response:**
```json
{
  "total_rows": 10,
  "matched_rows": 8,
  "unmatched_rows": 2,
  "headers": ["id", "name", "value", "category"],
  "sample_rows": [
    ["1", "Sample_A", "15.5", "Group_1"],
    ["2", "Sample_B", "22.3", "Group_2"]
  ],
  "download_url": "data:text/csv;base64,...",
  "file_name": "merged_data.csv"
}
```

#### Generate Visualization
```http
POST /api/bio/generate-visualization
```

**Request Body:**
```json
{
  "session_id": "session-uuid",
  "plot_type": "scatter",
  "x_column": "activity",
  "y_column": "concentration"
}
```

**Response:**
```json
{
  "plot_type": "scatter",
  "plot_data": "base64-encoded-png-image",
  "data_shape": [10, 5],
  "columns": ["id", "name", "activity", "concentration", "technician"],
  "numeric_columns": ["activity", "concentration"]
}
```

### 🎯 Session Management

#### Create Session
```http
POST /api/bio/create-session
```

**Response:**
```json
{
  "session_id": "session-uuid",
  "created_at": "2024-01-15T10:30:00Z",
  "status": "active"
}
```

#### Get Session Status
```http
GET /api/bio/session/{session_id}
```

**Response:**
```json
{
  "session_id": "session-uuid",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "last_activity": "2024-01-15T11:45:00Z",
  "data_files": ["file1.csv", "file2.csv"],
  "merged_data": {
    "total_rows": 10,
    "headers": ["id", "name", "value"]
  },
  "visualizations": [
    {
      "plot_type": "scatter",
      "created_at": "2024-01-15T11:30:00Z"
    }
  ]
}
```

#### Delete Session
```http
DELETE /api/bio/session/{session_id}
```

### 📊 Dataset Management

#### Process Dataset
```http
POST /datasets/process
```

**Form Data:**
- `file`: Dataset file
- `source_provider`: Data source provider
- `matching_config`: JSON configuration for matching

#### Match Dataset to Workflow
```http
POST /datasets/{dataset_id}/match/{workflow_id}
```

**Request Body:**
```json
{
  "confidence_threshold": 0.7,
  "matching_methods": ["sequence", "mutation", "alias"]
}
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes
- `FILE_NOT_FOUND`: Requested file not found
- `INVALID_FORMAT`: File format not supported
- `MERGE_FAILED`: File merging operation failed
- `VISUALIZATION_FAILED`: Plot generation failed
- `SESSION_EXPIRED`: Session has expired
- `INVALID_COLUMN`: Specified column not found in data

## Rate Limiting

Currently, no rate limiting is implemented for development purposes.

## File Upload Limits

- **Maximum file size**: 50MB
- **Supported formats**: CSV, Excel, JSON, Text
- **Encoding**: UTF-8 recommended

## Data Types

### CSV Format Requirements
- First row must contain column headers
- Consistent data types per column
- UTF-8 encoding
- Comma-separated values

### Visualization Data Requirements
- Numeric columns for plotting
- Categorical columns for grouping
- Minimum 2 rows for visualization
- Maximum 10,000 rows for performance

## Examples

### Complete Workflow Example

1. **Create Session**
```bash
curl -X POST "http://localhost:8000/api/bio/create-session"
```

2. **Upload Files**
```bash
curl -X POST "http://localhost:8000/api/bio/merge-files" \
  -F "file1=@sequences.csv" \
  -F "file2=@assay_results.csv"
```

3. **Generate Visualization**
```bash
curl -X POST "http://localhost:8000/api/bio/generate-visualization" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "plot_type": "scatter",
    "x_column": "activity",
    "y_column": "concentration"
  }'
```

4. **Check Session Status**
```bash
curl -X GET "http://localhost:8000/api/bio/session/your-session-id"
```

### Python Client Example

```python
import requests
import json

# Base URL
base_url = "http://localhost:8000"

# Create session
session_response = requests.post(f"{base_url}/api/bio/create-session")
session_id = session_response.json()["session_id"]

# Upload and merge files
with open("sequences.csv", "rb") as f1, open("assay_results.csv", "rb") as f2:
    merge_response = requests.post(
        f"{base_url}/api/bio/merge-files",
        files={"file1": f1, "file2": f2}
    )

# Generate visualization
viz_response = requests.post(
    f"{base_url}/api/bio/generate-visualization",
    json={
        "session_id": session_id,
        "plot_type": "scatter",
        "x_column": "activity",
        "y_column": "concentration"
    }
)

print("Session ID:", session_id)
print("Merge result:", merge_response.json())
print("Visualization result:", viz_response.json())
```

## Development Notes

- All endpoints return JSON responses
- File uploads use multipart/form-data
- Session IDs are UUIDs for security
- Data is stored temporarily for session duration
- Visualizations are generated as base64 PNG images 