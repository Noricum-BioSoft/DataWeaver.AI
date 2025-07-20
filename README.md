# DataWeaver.AI

A comprehensive data management system with AI-powered workflow automation, file processing, and visualization capabilities.

## 🚀 Features

### Core Functionality
- **AI Chat Interface**: Natural language data processing and analysis
- **Drag-and-Drop File Upload**: Seamless file handling with automatic format detection
- **Smart File Merging**: Automatic CSV merging with intelligent column matching
- **Data Visualization**: Generate scatter plots, histograms, correlation heatmaps, and boxplots
- **Workflow Session Management**: Persistent data storage between processing steps
- **Biological Entity Management**: Specialized support for protein sequences and assay data
- **Real File Processing**: Complete file upload, storage, and processing pipeline

### Technical Capabilities
- **Multi-file Upload**: Upload multiple CSV files individually
- **Intelligent Merging**: Merge files based on common ID columns (e.g., protein_id)
- **Session-based Workflows**: Maintain state across multiple processing steps
- **Data Analysis**: Q&A interface for exploring uploaded data
- **Visualization Generation**: Create plots from merged datasets
- **Error Handling**: Robust error handling with user-friendly messages

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **File Storage**: Structured file system with metadata tracking
- **Data Processing**: Pandas for CSV manipulation and analysis
- **Visualization**: Plotly for interactive charts
- **Session Management**: In-memory session storage with timeout

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS for modern, responsive design
- **State Management**: React hooks for local state
- **API Integration**: Axios for backend communication
- **File Handling**: Drag-and-drop file upload with progress tracking

### Key Components
- **AI Chat Interface**: Natural language interaction for data operations
- **File Upload System**: Multi-file upload with validation
- **Merge Engine**: Intelligent CSV merging based on common columns
- **Visualization Engine**: Dynamic chart generation from merged data
- **Session Manager**: Persistent workflow state across operations

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

**macOS/Linux:**
```bash
# Make script executable (first time only)
chmod +x start.sh

# Start all services
./start.sh

# Or start specific services
./start.sh backend    # Backend only
./start.sh frontend   # Frontend only
./start.sh status     # Check service status
./start.sh help       # Show all options
```

**Windows:**
```cmd
# Start all services
start.bat

# Or start specific services
start.bat backend    # Backend only
start.bat frontend   # Frontend only
start.bat status     # Check service status
start.bat help       # Show all options
```

### Option 2: Manual Setup

1. **Backend Setup**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Set up database (if PostgreSQL is available)
   alembic upgrade head
   
   # Start backend server
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 Usage Guide

### Basic Workflow

1. **Upload Files**:
   - Drag and drop CSV files into the upload area
   - Files are uploaded individually and stored in session
   - Supported formats: CSV, JSON, Excel (basic support)

2. **Merge Files**:
   - Ask "merge the files" in the chat interface
   - System automatically identifies common ID columns
   - Merges all uploaded files into a single dataset

3. **Analyze Data**:
   - Ask questions about your data: "What columns are in the data?"
   - Get statistical summaries: "Show me the average values"
   - Explore relationships: "Are there correlations between columns?"

4. **Visualize Data**:
   - Request visualizations: "Create a scatter plot"
   - Generate different chart types: "Make a histogram"
   - Get plot explanations: "Explain this visualization"

### Example Workflow

```
1. Upload protein_abundance.csv, protein_expression.csv, protein_sequences.csv, protein_spr.csv
2. Ask: "merge the files"
3. Ask: "What columns are in the merged data?"
4. Ask: "Create a scatter plot of abundance vs expression_level"
5. Ask: "Explain this visualization"
```

### Supported File Types

- **CSV Files**: Primary format with automatic column detection
- **JSON Files**: Basic support for structured data
- **Excel Files**: Limited support (requires pandas)

### Data Analysis Features

- **Column Analysis**: Identify data types, missing values, unique counts
- **Statistical Summaries**: Mean, median, standard deviation
- **Correlation Analysis**: Find relationships between numeric columns
- **Outlier Detection**: Identify unusual data points
- **Data Quality**: Check for missing values and data consistency

## 🔧 Configuration

### Environment Variables

**Backend (.env)**:
```bash
DATABASE_URL=postgresql://user:password@localhost/dataweaver
SECRET_KEY=your-secret-key
DEBUG=True
```

**Frontend (.env)**:
```bash
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development
```

### Database Setup

1. **Install PostgreSQL**:
   ```bash
   # macOS
   brew install postgresql
   
   # Ubuntu
   sudo apt-get install postgresql postgresql-contrib
   ```

2. **Create Database**:
   ```bash
   createdb dataweaver
   ```

3. **Run Migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Run the test script
python test_merge_functionality.py
```

## 📁 Project Structure

```
DataWeaver.AI/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript types
│   └── package.json        # Node.js dependencies
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── test_data/             # Sample data files
```

## 🔍 API Documentation

### Interactive API Docs
- **Swagger UI**: Visit `http://localhost:8000/docs` when the server is running
- **ReDoc**: Visit `http://localhost:8000/redoc` for alternative documentation

### OpenAPI Specification
- **YAML Format**: `docs/openapi.yaml`
- **JSON Format**: `docs/openapi.json`
- **Complete API Reference**: `docs/API.md`

### Core Endpoints
- `POST /api/bio/create-workflow-session` - Create new session
- `POST /api/bio/upload-single-file` - Upload individual file
- `POST /api/bio/merge-session-files` - Merge uploaded files
- `POST /api/bio/generate-visualization` - Create charts
- `POST /api/data-qa/ask` - Data analysis Q&A
- `POST /api/general-chat/chat` - General AI chat

### Session Management
- `GET /api/bio/workflow-status/{session_id}` - Get session status
- `GET /api/bio/workflow-history/{session_id}` - Get workflow history
- `DELETE /api/bio/clear-session/{session_id}` - Clear session

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**:
   ```bash
   # Check what's using the ports
   lsof -i :8000
   lsof -i :3000
   
   # Kill processes if needed
   kill -9 <PID>
   ```

2. **Database Connection**:
   ```bash
   # Check PostgreSQL status
   brew services list | grep postgresql
   
   # Start PostgreSQL if needed
   brew services start postgresql
   ```

3. **Frontend Build Issues**:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Backend Import Errors**:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Logs

- **Backend logs**: Check terminal where uvicorn is running
- **Frontend logs**: Check browser developer console
- **Database logs**: Check PostgreSQL logs

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make your changes**
4. **Run tests**: `pytest tests/` and `npm test`
5. **Commit your changes**: `git commit -am 'Add new feature'`
6. **Push to the branch**: `git push origin feature/new-feature`
7. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions and ideas

## 🚀 Roadmap

### Planned Features
- [ ] Advanced visualization options (3D plots, interactive charts)
- [ ] Machine learning integration for data analysis
- [ ] Real-time collaboration features
- [ ] Advanced file format support (Parquet, HDF5)
- [ ] Cloud storage integration (AWS S3, Google Cloud Storage)
- [ ] Workflow templates and sharing
- [ ] Advanced data validation and cleaning tools
- [ ] Export capabilities (PDF reports, Excel exports)

### Technical Improvements
- [ ] Performance optimization for large datasets
- [ ] Caching layer for frequently accessed data
- [ ] Advanced security features
- [ ] Multi-tenant architecture
- [ ] API rate limiting and authentication
- [ ] Comprehensive test coverage
- [ ] CI/CD pipeline setup

---

**DataWeaver.AI** - Making data analysis accessible through AI-powered workflows.