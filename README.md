# DataWeaver.AI

A comprehensive data management system for workflow-based applications with automatic dataset linking capabilities.

## Architecture

- **Frontend**: React with TypeScript
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL
- **File Storage**: Structured file system with metadata tracking

## Features

- **Workflow Management**: Track workflows, steps, and their relationships
- **File Handling**: Upload/download files with metadata tracking
- **Automatic Dataset Linking**: Intelligent matching of external data to workflow context
- **Scalable Architecture**: Support for large files and parallel workflows

## Quick Start

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Database Setup**:
   ```bash
   # Run database migrations
   cd backend
   alembic upgrade head
   ```

## Project Structure

```
DataWeaver.AI/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript types
│   └── package.json
└── docs/                   # Documentation
```