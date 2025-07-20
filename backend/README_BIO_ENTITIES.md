# DataWeaver.AI Backend

The backend service for DataWeaver.AI, providing API endpoints for data processing, file management, and workflow automation.

## 🏗️ Architecture

### Core Components

#### API Endpoints (`app/api/`)
- **`bio_matcher.py`**: Main data processing endpoints
  - File upload and session management
  - CSV merging with intelligent column matching
  - Data visualization generation
  - Data analysis and Q&A functionality
- **`datasets.py`**: Dataset processing and matching
- **`files.py`**: File upload and management
- **`workflows.py`**: Workflow management

#### Data Models (`app/models/`)
- **`workflow.py`**: Workflow and step entities
- **`file.py`**: File storage and metadata
- **`dataset.py`**: Dataset and matching entities
- **`bio_entities.py`**: Biological entity models (Design, Build, Test)

#### Services (`app/services/`)
- **`file_service.py`**: File upload and storage management
- **`matching_service.py`**: Dataset matching algorithms
- **`data_context.py`**: Data context management
- **`data_analyzer.py`**: Data analysis and insights
- **`intelligent_merger.py`**: Advanced merging logic
- **`simple_visualizer.py`**: Fallback visualization service

#### Session Management (`services/`)
- **`workflow_state.py`**: Session state management
- **`bio_matcher.py`**: Biological entity matching

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite used by default)
- pip

### Installation

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run database migrations** (if using PostgreSQL):
   ```bash
   alembic upgrade head
   ```

5. **Start the server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📡 API Endpoints

### Session Management
```http
POST /api/bio/create-workflow-session
DELETE /api/bio/clear-session/{session_id}
GET /api/bio/workflow-status/{session_id}
GET /api/bio/workflow-history/{session_id}
```

### File Operations
```http
POST /api/bio/upload-single-file
POST /api/bio/merge-session-files
POST /api/bio/merge-files
```

### Data Analysis
```http
POST /api/bio/generate-visualization
POST /api/bio/explain-visualization
POST /api/bio/analyze-data
POST /api/data-qa/ask
GET /api/data-qa/suggestions/{session_id}
```

### AI Chat
```http
POST /api/general-chat/chat
```

### Biological Entities
```http
POST /api/bio/upload-test-results
GET /api/bio/designs
GET /api/bio/builds
GET /api/bio/tests
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dataweaver
# or for SQLite: DATABASE_URL=sqlite:///./dataweaver.db

# Security
SECRET_KEY=your-secret-key-here

# Development
DEBUG=True
LOG_LEVEL=INFO

# File Storage
STORAGE_PATH=./storage
MAX_FILE_SIZE=10485760  # 10MB

# Session Management
SESSION_TIMEOUT=86400  # 24 hours
```

### Database Setup

#### PostgreSQL (Recommended)
```bash
# Install PostgreSQL
brew install postgresql  # macOS
sudo apt-get install postgresql postgresql-contrib  # Ubuntu

# Create database
createdb dataweaver

# Run migrations
alembic upgrade head
```

#### SQLite (Development)
```bash
# SQLite is used by default for development
# No additional setup required
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api_endpoints.py

# Run with coverage
pytest --cov=app tests/

# Run integration tests
pytest tests/test_integration.py -v
```

### Test Configuration
- Test database: `test.db` (SQLite)
- Test data: `test_data/` directory
- Mock services for external dependencies

## 📊 Data Processing

### File Upload Flow
1. **File Validation**: Check file type and size
2. **Content Processing**: Parse CSV/JSON data
3. **Metadata Extraction**: Extract column info and statistics
4. **Session Storage**: Store in workflow session
5. **Context Tracking**: Add to data context for analysis

### Merge Process
1. **Column Analysis**: Find common columns across files
2. **ID Detection**: Identify primary key columns
3. **Data Merging**: Perform outer join on ID columns
4. **Result Processing**: Convert to JSON-serializable format
5. **Session Storage**: Store merged result for visualization

### Visualization Generation
1. **Data Retrieval**: Get data from session or uploaded file
2. **Plot Type Selection**: Determine appropriate chart type
3. **Data Processing**: Prepare data for visualization
4. **Chart Generation**: Create Plotly JSON
5. **Response Formatting**: Return chart data and metadata

## 🔍 Error Handling

### Common Error Responses
```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_type": "validation_error"
}
```

### Error Types
- **ValidationError**: Invalid input data
- **FileError**: File processing issues
- **SessionError**: Session management problems
- **MergeError**: Data merging failures
- **VisualizationError**: Chart generation issues

## 📈 Performance

### Optimization Strategies
- **Lazy Loading**: Load data only when needed
- **Session Caching**: Cache frequently accessed session data
- **File Streaming**: Stream large files instead of loading entirely
- **Async Processing**: Use async/await for I/O operations
- **Database Indexing**: Index frequently queried columns

### Monitoring
- Request/response logging
- Performance metrics collection
- Error tracking and alerting
- Resource usage monitoring

## 🔒 Security

### Current Security Measures
- Input validation and sanitization
- File type verification
- Size limits on uploads
- Session timeout management
- Error message sanitization

### Planned Security Features
- API key authentication
- Rate limiting
- CORS configuration
- Data encryption
- Audit logging

## 🚀 Deployment

### Production Setup
1. **Environment Configuration**:
   ```bash
   export DATABASE_URL=postgresql://user:pass@host/db
   export SECRET_KEY=production-secret-key
   export DEBUG=False
   ```

2. **Database Migration**:
   ```bash
   alembic upgrade head
   ```

3. **Static Files**:
   ```bash
   mkdir -p storage
   chmod 755 storage
   ```

4. **Process Management**:
   ```bash
   # Using gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   
   # Using systemd
   sudo systemctl enable dataweaver
   sudo systemctl start dataweaver
   ```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN alembic upgrade head

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📚 Development

### Code Style
- **Python**: PEP 8 with Black formatting
- **Type Hints**: Use type annotations
- **Docstrings**: Document all functions
- **Error Handling**: Comprehensive exception handling

### Adding New Endpoints
1. Create endpoint in appropriate API module
2. Add Pydantic schemas for request/response
3. Add database models if needed
4. Write tests for the endpoint
5. Update API documentation

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-endpoint`
3. **Make changes**: Follow code style guidelines
4. **Add tests**: Ensure all new code is tested
5. **Run tests**: `pytest tests/`
6. **Submit PR**: Include description of changes

## 📄 License

This project is licensed under the MIT License.

---

**DataWeaver.AI Backend** - Powering intelligent data workflows. 