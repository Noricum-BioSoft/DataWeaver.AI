# DataWeaver.AI Setup Guide

## Overview

This guide will help you set up DataWeaver.AI on your local machine for development or production use. The system consists of a FastAPI backend and a React frontend.

## Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for package installation

### Required Software

#### Python Environment
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Install pip if not available
python3 -m ensurepip --upgrade
```

#### Node.js Environment
```bash
# Check Node.js version
node --version  # Should be 16+

# Check npm version
npm --version   # Should be 6+
```

#### Git
```bash
# Check Git version
git --version
```

## Quick Start (Automated)

### Option 1: Automated Setup Script

**macOS/Linux:**
```bash
# Clone the repository
git clone https://github.com/your-username/DataWeaver.AI.git
cd DataWeaver.AI

# Make setup script executable
chmod +x setup.sh

# Run automated setup
./setup.sh
```

**Windows:**
```cmd
# Clone the repository
git clone https://github.com/your-username/DataWeaver.AI.git
cd DataWeaver.AI

# Run automated setup
setup.bat
```

### Option 2: Start Scripts

**macOS/Linux:**
```bash
# Make start script executable
chmod +x start.sh

# Start all services
./start.sh

# Or start specific services
./start.sh backend    # Backend only
./start.sh frontend   # Frontend only
./start.sh status     # Check service status
```

**Windows:**
```cmd
# Start all services
start.bat

# Or start specific services
start.bat backend    # Backend only
start.bat frontend   # Frontend only
start.bat status     # Check service status
```

## Manual Setup

### Step 1: Backend Setup

#### 1.1 Create Python Virtual Environment
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 1.2 Install Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

#### 1.3 Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit environment variables
nano .env  # or use your preferred editor
```

**Environment Variables:**
```bash
# Database
DATABASE_URL=sqlite:///./dataweaver.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/dataweaver

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

#### 1.4 Database Setup

**SQLite (Default - Development):**
```bash
# No additional setup required
# Database will be created automatically
```

**PostgreSQL (Production):**
```bash
# Install PostgreSQL
# macOS:
brew install postgresql

# Ubuntu:
sudo apt-get install postgresql postgresql-contrib

# Create database
createdb dataweaver

# Run migrations
alembic upgrade head
```

#### 1.5 Start Backend Server
```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Step 2: Frontend Setup

#### 2.1 Install Node.js Dependencies
```bash
cd frontend

# Install dependencies
npm install
```

#### 2.2 Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit environment variables
nano .env
```

**Environment Variables:**
```bash
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development
```

#### 2.3 Start Frontend Development Server
```bash
# Development mode
npm start

# Build for production
npm run build
```

### Step 3: Verify Installation

#### 3.1 Check Backend
```bash
# Test backend health
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs
```

#### 3.2 Check Frontend
```bash
# Open frontend in browser
open http://localhost:3000
```

#### 3.3 Test Complete Workflow
1. **Upload test files** from `test_data/` directory
2. **Merge files** using chat interface
3. **Generate visualizations** from merged data
4. **Ask questions** about the data

## Production Setup

### Docker Deployment

#### 1. Create Dockerfile
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN alembic upgrade head

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db/dataweaver
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=dataweaver
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 3. Deploy with Docker
```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Systemd Service (Linux)

#### 1. Create Service File
```bash
sudo nano /etc/systemd/system/dataweaver.service
```

#### 2. Add Service Configuration
```ini
[Unit]
Description=DataWeaver.AI Backend
After=network.target

[Service]
Type=simple
User=dataweaver
WorkingDirectory=/opt/dataweaver/backend
Environment=PATH=/opt/dataweaver/backend/venv/bin
ExecStart=/opt/dataweaver/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 3. Enable and Start Service
```bash
sudo systemctl enable dataweaver
sudo systemctl start dataweaver
sudo systemctl status dataweaver
```

## Configuration Options

### Backend Configuration

#### Database Options
```bash
# SQLite (Development)
DATABASE_URL=sqlite:///./dataweaver.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@localhost/dataweaver

# MySQL (Alternative)
DATABASE_URL=mysql://user:password@localhost/dataweaver
```

#### Security Settings
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in environment
SECRET_KEY=your-generated-secret-key
```

#### File Storage
```bash
# Local storage (default)
STORAGE_PATH=./storage

# Cloud storage (future)
STORAGE_PATH=s3://your-bucket/dataweaver

# Note: storage/, uploads/, and logs/ directories are gitignored
# They will be created automatically when the application starts
```

### Frontend Configuration

#### API Endpoints
```bash
# Development
REACT_APP_API_URL=http://localhost:8000/api

# Production
REACT_APP_API_URL=https://api.dataweaver.ai/api
```

#### Feature Flags
```bash
# Enable/disable features
REACT_APP_ENABLE_VOICE_INPUT=true
REACT_APP_ENABLE_FILE_EXPORT=true
REACT_APP_ENABLE_COLLABORATION=false
```

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :3000

# Kill processes if needed
kill -9 <PID>
```

#### Python Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### Database Issues
```bash
# Reset database
rm -f dataweaver.db
alembic upgrade head

# Check database connection
python -c "from app.database import engine; print(engine.execute('SELECT 1').fetchone())"
```

### Performance Tuning

#### Backend Optimization
```bash
# Increase worker processes
gunicorn main:app -w 8 -k uvicorn.workers.UvicornWorker

# Enable caching
pip install redis
# Configure Redis in settings

# Database optimization
# Add indexes for frequently queried columns
```

#### Frontend Optimization
```bash
# Build optimized version
npm run build

# Serve with nginx
sudo apt-get install nginx
# Configure nginx for static files
```

### Monitoring

#### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Database health
python -c "from app.database import engine; print('DB OK' if engine.execute('SELECT 1').fetchone() else 'DB ERROR')"
```

#### Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs
# Check browser developer console

# System logs
journalctl -u dataweaver -f
```

## Development Setup

### IDE Configuration

#### VS Code
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

#### PyCharm
1. **Open project** in PyCharm
2. **Configure interpreter** to `backend/venv/bin/python`
3. **Install plugins**: Python, React, TypeScript
4. **Configure run configurations** for backend and frontend

### Development Tools

#### Code Quality
```bash
# Backend linting
pip install black flake8 mypy
black backend/
flake8 backend/
mypy backend/

# Frontend linting
npm run lint
npm run type-check
```

#### Testing
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Integration tests
python test_integration.py
```

## Security Considerations

### Development
- **Use environment variables** for sensitive data
- **Don't commit secrets** to version control
- **Use HTTPS** in production
- **Implement rate limiting** for API endpoints

### Production
- **Use strong secret keys**
- **Enable HTTPS/TLS**
- **Implement authentication** (planned)
- **Set up monitoring** and alerting
- **Regular security updates**

## Support

### Getting Help
- **Documentation**: Check `/docs` folder
- **Issues**: Report on GitHub
- **Discussions**: Use GitHub Discussions
- **Email**: contact@dataweaver.ai

### Contributing
1. **Fork the repository**
2. **Create feature branch**
3. **Make changes** following style guidelines
4. **Add tests** for new functionality
5. **Submit pull request**

---

**DataWeaver.AI** - Making data analysis accessible and powerful. 