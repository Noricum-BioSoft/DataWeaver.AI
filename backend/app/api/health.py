from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models.connector import Connector
import psutil
import os

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for system status"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get connector stats
        total_connectors = db.query(Connector).count()
        connected_connectors = db.query(Connector).filter(Connector.status == "connected").count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            },
            "connectors": {
                "total": total_connectors,
                "connected": connected_connectors,
                "disconnected": total_connectors - connected_connectors
            },
            "timestamp": "2025-08-24T18:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-08-24T18:00:00Z"
        }
