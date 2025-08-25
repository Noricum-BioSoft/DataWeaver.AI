# DataWeaver.AI Documentation

## Overview
DataWeaver.AI is a comprehensive data integration and workflow management platform that enables step-by-step execution of generic workflows using natural language commands and automatically merges data used and generated across workflows.

## Core Goals
- **Natural Language Workflow Execution**: Execute complex workflows using simple natural language commands
- **Automatic Data Merging**: Intelligently merge data from multiple sources and workflows
- **Data Lineage Tracking**: Maintain complete traceability of data transformations and relationships

## Architecture

### System Components
- **Backend**: FastAPI-based REST API with SQLAlchemy ORM
- **Frontend**: React TypeScript application with modern UI
- **Database**: PostgreSQL with SQLite fallback for development
- **Connector System**: Modular architecture for data source integration

### Data Flow
1. **Data Ingestion**: Connectors extract data from various sources
2. **Data Processing**: AI-powered analysis and transformation
3. **Data Merging**: Intelligent merging of related datasets
4. **Workflow Execution**: Natural language command processing
5. **Result Storage**: Persistent storage with lineage tracking

## Connector System

### Supported Connectors
- **Google Workspace**: Drive, Sheets, Docs integration
- **Microsoft 365**: Excel, Word, SharePoint
- **Slack**: Message and file integration
- **Email**: IMAP/POP3 email processing
- **Database**: SQL database connections
- **API**: REST API integrations
- **File System**: Local and network file access
- **LIMS**: Laboratory Information Management Systems
- **Omics**: Biological data sources
- **Literature**: Research paper and document processing
- **Clinical**: Healthcare data integration

### Authentication Types
- **OAuth2**: For Google, Microsoft, and other OAuth providers
- **API Key**: For service-to-service integrations
- **Username/Password**: For traditional authentication
- **Token**: For bearer token authentication
- **None**: For public data sources

## API Documentation

### Core Endpoints
- `GET /api/health` - System health check
- `GET /api/connectors/` - List all connectors
- `POST /api/connectors/` - Create new connector
- `GET /api/connectors/{id}` - Get connector details
- `POST /api/connectors/{id}/test` - Test connector connection
- `POST /api/connectors/{id}/discover` - Discover data sources
- `POST /api/connectors/{id}/sync` - Sync connector data

### Authentication Endpoints
- `GET /api/auth/google/authorize/{connector_id}` - Start OAuth2 flow
- `GET /api/auth/callback` - OAuth2 callback handler
- `POST /api/auth/google/refresh/{connector_id}` - Refresh OAuth2 tokens

### Demo Scenarios
- `GET /api/connectors/scenarios` - List available demo scenarios
- `POST /api/connectors/scenarios/{scenario_id}/setup` - Setup demo scenario

## Setup and Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite for development)
- Google Cloud Console project (for Google Drive integration)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///./dataweaver.db

# Google OAuth2 (for Google Drive integration)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Security
SECRET_KEY=your_secret_key
```

## Development

### Testing
```bash
# Run all tests
cd backend
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_connectors.py -v
python -m pytest tests/test_api_endpoints.py -v
```

### Code Quality
- **Linting**: Use `black` for Python formatting
- **Type Checking**: Use `mypy` for Python type checking
- **Frontend**: Use ESLint and Prettier for TypeScript/JavaScript

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Deployment

### Production Setup
1. **Database**: Use PostgreSQL in production
2. **Environment**: Set production environment variables
3. **Security**: Configure proper CORS and authentication
4. **Monitoring**: Set up logging and health checks
5. **SSL**: Configure HTTPS with proper certificates

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual containers
docker build -t dataweaver-backend ./backend
docker build -t dataweaver-frontend ./frontend
```

## Security

### Authentication
- OAuth2 integration for external services
- Secure token storage and refresh
- API key management for service integrations

### Data Protection
- Encrypted credential storage
- Secure data transmission (HTTPS)
- Access control and authorization

### Best Practices
- Regular security updates
- Input validation and sanitization
- Error handling without information disclosure
- Audit logging for sensitive operations

## Monitoring and Health

### System Health
- Database connectivity monitoring
- Connector status tracking
- Resource usage monitoring (CPU, memory, disk)
- Real-time system status dashboard

### Logging
- Structured logging with different levels
- Error tracking and alerting
- Performance monitoring
- Audit trail for data operations

## Contributing

### Development Workflow
1. Create feature branch from `main`
2. Implement changes with tests
3. Run linting and type checking
4. Submit pull request with description
5. Code review and approval process

### Code Standards
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write comprehensive tests
- Document new features and APIs
- Update documentation as needed

## Support and Troubleshooting

### Common Issues
- **OAuth2 Errors**: Check Google Cloud Console configuration
- **Database Issues**: Verify connection and migration status
- **Frontend Build Errors**: Clear node_modules and reinstall
- **Test Failures**: Check environment setup and dependencies

### Getting Help
- Check the troubleshooting guide
- Review API documentation
- Examine test cases for examples
- Create issue with detailed description

## License
See LICENSE file for project licensing information.
