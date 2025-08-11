# DataWeaver.AI

An AI-powered data analysis platform that makes data science accessible through natural language processing, intelligent data merging, and automated visualization.

## 🎯 MVP Features

### Core Capabilities
- **🔬 Natural Language Processing**: Ask questions about your data in plain English
- **🔄 AI-based Data Merging**: Intelligently combine multiple datasets automatically
- **📊 Data Science Tools**: Analysis, visualization, and Q&A capabilities
- **📁 File Upload**: Drag-and-drop CSV file upload with validation
- **💬 Interactive Chat**: AI assistant for data exploration and analysis

### What You Can Do
- **Upload CSV files** and ask questions about your data
- **Merge multiple datasets** with intelligent column matching
- **Generate visualizations** like scatter plots, histograms, and charts
- **Ask data questions** and get AI-powered insights
- **Explore data patterns** and discover relationships

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

### Option 1: Unified Startup Script (Recommended)

**All Platforms:**
```bash
# Install dependencies and setup database
python start.py --install-deps --setup-db

# Or just start with existing setup
python start.py

# Show help
python start.py --help
```

### Option 2: Manual Setup

1. **Configure environment:**
   ```bash
   cp docs/env.example .env
   # Edit .env with your configuration
   ```

2. **Backend Setup**:
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

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🎉 MVP Release

**DataWeaver.AI MVP is now available!** This release focuses on the core data science capabilities:

- ✅ **Natural Language Interface** - Ask questions about your data in plain English
- ✅ **Intelligent Data Merging** - AI-powered combination of multiple datasets
- ✅ **Data Science Tools** - Analysis, visualization, and Q&A capabilities
- ✅ **Unified Startup** - Single `start.py` script for easy setup
- ✅ **Comprehensive Testing** - All test data files verified and working

📖 **View the [Release Summary](docs/RELEASE_1.0.0_SUMMARY.md) for complete details**

## 📖 Usage Guide

### Quick Start

1. **Upload Your Data**:
   - Drag and drop CSV files into the upload area
   - Supported formats: CSV files
   - Files are automatically validated and processed

2. **Ask Questions**:
   - Use natural language: "Show me a summary of this data"
   - Get insights: "What are the main trends?"
   - Request analysis: "Create a scatter plot of the data"

3. **Merge Datasets**:
   - Upload multiple files and ask: "Merge these datasets together"
   - AI automatically identifies common columns for merging
   - Get a unified dataset for analysis

4. **Explore and Visualize**:
   - Ask for specific visualizations: "Create a histogram"
   - Get data summaries: "How many records are in this dataset?"
   - Discover patterns: "Are there any correlations?"

### Example Workflow

```
1. Upload customers.csv and sales.csv
2. Ask: "Merge these datasets together"
3. Ask: "Show me a summary of the merged data"
4. Ask: "Create a scatter plot of sales vs customer age"
5. Ask: "What are the main trends in this data?"
```

### Supported Features

- **📊 Data Analysis**: Statistical summaries, correlations, patterns
- **📈 Visualizations**: Scatter plots, histograms, charts
- **🔄 Data Merging**: Intelligent combination of multiple datasets
- **❓ Q&A Interface**: Ask questions about your data in plain English
- **📁 File Management**: Upload, validate, and process CSV files

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

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

### Commercial Licensing

For commercial use, enterprise deployments, or SaaS offerings, please contact us for commercial licensing options that may be available.

## 🆘 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions and ideas

## 🚀 Future Enhancements

### Planned Features
- [ ] Advanced visualization options (3D plots, interactive charts)
- [ ] Machine learning integration for data analysis
- [ ] Workflow automation and templates
- [ ] Advanced file format support (Parquet, HDF5)
- [ ] Cloud storage integration (AWS S3, Google Cloud Storage)
- [ ] Export capabilities (PDF reports, Excel exports)
- [ ] Real-time collaboration features

### Technical Improvements
- [ ] Performance optimization for large datasets
- [ ] Caching layer for frequently accessed data
- [ ] Advanced security features
- [ ] Multi-tenant architecture
- [ ] API rate limiting and authentication
- [ ] CI/CD pipeline setup

---

**DataWeaver.AI** - Making data analysis accessible through AI-powered workflows.