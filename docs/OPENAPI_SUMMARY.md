# OpenAPI Specification Summary

## Overview

DataWeaver.AI provides a comprehensive OpenAPI specification that documents all API endpoints, request/response schemas, and usage examples. The specification is available in both YAML and JSON formats.

## Files

- **`docs/openapi.yaml`** - YAML format (primary)
- **`docs/openapi.json`** - JSON format (converted from YAML)
- **`docs/API.md`** - Human-readable API documentation

## API Categories

### 1. Session Management
- **Create Session**: `POST /api/bio/create-workflow-session`
- **Clear Session**: `DELETE /api/bio/clear-session/{session_id}`
- **Get Status**: `GET /api/bio/workflow-status/{session_id}`

### 2. File Operations
- **Upload Single File**: `POST /api/bio/upload-single-file`
- **Merge Session Files**: `POST /api/bio/merge-session-files`
- **Merge Multiple Files**: `POST /api/bio/merge-files`

### 3. Data Analysis
- **Generate Visualization**: `POST /api/bio/generate-visualization`
- **Explain Visualization**: `POST /api/bio/explain-visualization`
- **Analyze Data**: `POST /api/bio/analyze-data`

### 4. Data Q&A
- **Ask Questions**: `POST /api/data-qa/ask`
- **Get Suggestions**: `GET /api/data-qa/suggestions/{session_id}`

### 5. AI Chat
- **General Chat**: `POST /api/general-chat/chat`

### 6. Biological Entities
- **Upload Test Results**: `POST /api/bio/upload-test-results`
- **Get Designs**: `GET /api/bio/designs`
- **Get Builds**: `GET /api/bio/builds`
- **Get Tests**: `GET /api/bio/tests`

## Key Features

### Authentication
- Currently: No authentication (development mode)
- Future: API key authentication for production

### Rate Limiting
- Currently: No rate limiting
- Future: Rate limiting based on API keys

### File Upload Limits
- **Maximum size**: 10MB
- **Supported formats**: CSV, JSON, Excel (basic)
- **Encoding**: UTF-8 recommended

### Session Management
- **Timeout**: 24 hours
- **Maximum files**: No limit (memory dependent)
- **Cleanup**: Automatic on timeout

## Usage Examples

### Interactive Documentation
```bash
# Start the server
cd backend
python main.py

# Access interactive docs
open http://localhost:8000/docs
```

### Generate Client Libraries
```bash
# Python client
npx @openapitools/openapi-generator-cli generate \
  -i docs/openapi.yaml \
  -g python \
  -o ./generated/python-client

# JavaScript client
npx @openapitools/openapi-generator-cli generate \
  -i docs/openapi.yaml \
  -g javascript \
  -o ./generated/js-client
```

### Import into Tools
- **Postman**: Import `docs/openapi.yaml`
- **Insomnia**: Import `docs/openapi.yaml`
- **Swagger UI**: Use `/docs` endpoint

## Validation

The OpenAPI specifications are validated using the included validation script:

```bash
python scripts/validate_openapi.py
```

This script checks:
- ✅ YAML specification validity
- ✅ JSON specification validity
- ✅ Consistency between YAML and JSON
- ✅ Required fields and structure

## Conversion

To convert YAML to JSON (ensures consistency):

```bash
python scripts/convert_openapi.py
```

## Schema Definitions

The specification includes comprehensive schema definitions for:

### Request/Response Models
- `FileUploadResponse` - File upload results
- `MergeResponse` - Data merging results
- `VisualizationResponse` - Chart generation results
- `DataQAResponse` - Question/answer results
- `ChatResponse` - AI chat responses
- `ErrorResponse` - Error handling

### Biological Entity Models
- `BioDesign` - Biological design entities
- `BioBuild` - Biological build entities
- `BioTest` - Biological test entities
- `BioTestResultsResponse` - Test processing results

### Workflow Models
- `WorkflowStep` - Individual workflow steps
- `WorkflowStatus` - Session status information

## Error Handling

Standard HTTP status codes with detailed error responses:

- **400** - Bad Request (invalid input)
- **404** - Not Found (resource not found)
- **422** - Validation Error (invalid data format)
- **500** - Internal Server Error
- **503** - Service Unavailable

## Future Enhancements

### Planned Features
- API key authentication
- Rate limiting
- Webhook support
- Real-time notifications
- Advanced filtering and pagination

### Versioning Strategy
- Semantic versioning (1.0.0, 1.1.0, etc.)
- Backward compatibility maintained
- Deprecation notices in advance

## Contributing

When adding new endpoints:

1. **Update YAML spec** (`docs/openapi.yaml`)
2. **Convert to JSON** (`python scripts/convert_openapi.py`)
3. **Validate specs** (`python scripts/validate_openapi.py`)
4. **Update documentation** (`docs/API.md`)
5. **Test endpoints** (ensure they match the spec)

## Support

For OpenAPI specification issues:
- **Validation**: Run the validation script
- **Conversion**: Use the conversion script
- **Documentation**: Check `docs/API.md`
- **Interactive**: Use `/docs` endpoint
- **Issues**: GitHub Issues 