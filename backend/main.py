from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import files, workflows, datasets
from app.api import bio_matcher
from app.api import intelligent_merge
from app.api import data_qa
from app.api import general_chat
from app.api import connectors
from app.api import auth
from app.api import health
import api.bio_entities
from sqlalchemy import create_engine, text
from app.database import get_db
from sqlalchemy.orm import Session
from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="DataWeaver.AI API",
    description="Data management system for workflows and biological entities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(files.router, prefix="/api")
app.include_router(workflows.router, prefix="/api")
app.include_router(datasets.router, prefix="/api")
app.include_router(bio_matcher.router, prefix="/api")
app.include_router(api.bio_entities.router, prefix="/api/bio")
app.include_router(intelligent_merge.router, prefix="/api")
app.include_router(data_qa.router, prefix="/api/data-qa")
app.include_router(general_chat.router, prefix="/api")
app.include_router(connectors.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(health.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "DataWeaver.AI API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/system/info")
def get_system_info():
    """Get system information"""
    return {
        "version": "1.0.0",
        "database_status": "connected",
        "environment": "development"
    }

@app.get("/api/system/db-status")
def get_database_status(db: Session = Depends(get_db)):
    """Check database connectivity"""
    try:
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        return {"connected": True, "status": "healthy"}
    except Exception as e:
        return {"connected": False, "status": str(e)} 