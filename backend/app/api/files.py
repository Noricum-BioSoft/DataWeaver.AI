from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import os
import uuid
import tempfile
import shutil
from datetime import datetime
from ..database import get_db
from ..models.file import File, FileMetadata, FileType, FileStatus
from ..schemas.file import FileResponse as FileSchema, FileUploadResponse
from ..services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])

# Initialize file service
file_service = FileService()

# Simple file upload endpoint (for integration tests)
@router.post("/upload", response_model=dict)
async def upload_file_simple(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db)
):
    """Upload a file and return file_id for processing."""
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Create upload directory if it doesn't exist
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = upload_dir / unique_filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create file record in database
        try:
            file_record = File(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=str(file_path),
                file_size=file_path.stat().st_size,
                file_type=FileType.CSV,
                mime_type=file.content_type or "text/csv",
                status=FileStatus.READY,
                workflow_id=1  # Default workflow ID for integration tests
            )
            db.add(file_record)
            db.commit()
            db.refresh(file_record)
        except Exception as db_exc:
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_exc)}")
        
        return {"file_id": file_record.id, "filename": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File upload endpoints
@router.post("/upload/{workflow_id}", response_model=FileUploadResponse)
async def upload_file(
    workflow_id: int,
    file: UploadFile = FastAPIFile(...),
    step_id: Optional[int] = None,
    parent_file_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Upload a file to a workflow."""
    try:
        result = await file_service.upload_file(
            db=db,
            file=file,
            workflow_id=workflow_id,
            step_id=step_id,
            parent_file_id=parent_file_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}", response_model=FileSchema)
def get_file(file_id: int, db: Session = Depends(get_db)):
    """Get file metadata."""
    file_record = db.query(File).filter(File.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    return file_record

@router.get("/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)):
    """Download a file."""
    file_record = db.query(File).filter(File.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_service.get_file_path(file_record)
    if not file_service.file_exists(file_record):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=str(file_path),
        filename=str(file_record.original_filename),
        media_type=str(file_record.mime_type)
    )

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: int, db: Session = Depends(get_db)):
    """Delete a file."""
    success = file_service.delete_file(db, file_id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return None

# Workflow files endpoints
@router.get("/workflow/{workflow_id}", response_model=List[FileSchema])
def get_workflow_files(workflow_id: int, db: Session = Depends(get_db)):
    """Get all files for a workflow."""
    files = file_service.get_workflow_files(db, workflow_id)
    return files

@router.get("/step/{step_id}", response_model=List[FileSchema])
def get_step_files(step_id: int, db: Session = Depends(get_db)):
    """Get all files for a workflow step."""
    files = file_service.get_step_files(db, step_id)
    return files

# File metadata endpoints
@router.post("/{file_id}/metadata")
def add_file_metadata(
    file_id: int,
    metadata: dict,
    db: Session = Depends(get_db)
):
    """Add metadata to a file."""
    file_record = db.query(File).filter(File.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_service.add_file_metadata(db, file_id, metadata)
    return {"message": "Metadata added successfully"}

@router.get("/{file_id}/metadata")
def get_file_metadata(file_id: int, db: Session = Depends(get_db)):
    """Get metadata for a file."""
    metadata = db.query(FileMetadata).filter(FileMetadata.file_id == file_id).all()
    return metadata

# File relationship endpoints
@router.post("/{file_id}/relationships")
def create_file_relationship(
    file_id: int,
    related_file_id: int,
    relationship_type: str,
    confidence_score: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Create a relationship between two files."""
    file_service.create_file_relationship(
        db, file_id, related_file_id, relationship_type, confidence_score
    )
    return {"message": "Relationship created successfully"}

@router.get("/{file_id}/relationships")
def get_file_relationships(file_id: int, db: Session = Depends(get_db)):
    """Get relationships for a file."""
    from ..models.file import FileRelationship
    
    relationships = db.query(FileRelationship).filter(
        FileRelationship.file_id == file_id
    ).all()
    return relationships 