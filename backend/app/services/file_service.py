import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import UploadFile, HTTPException
import aiofiles
import magic
# TODO: Re-enable pandas import when Python 3.13 compatibility is resolved
# import pandas as pd
from sqlalchemy.orm import Session
from ..models.file import File, FileMetadata, FileType, FileStatus
from ..schemas.file import FileCreate, FileUploadResponse

class FileService:
    def __init__(self, base_storage_path: str = "storage"):
        self.base_storage_path = Path(base_storage_path)
        self.base_storage_path.mkdir(exist_ok=True)
    
    def _get_file_type(self, filename: str, mime_type: Optional[str] = None) -> FileType:
        """Determine file type based on extension and MIME type."""
        ext = Path(filename).suffix.lower()
        
        if ext in ['.csv']:
            return FileType.CSV
        elif ext in ['.xlsx', '.xls']:
            return FileType.EXCEL
        elif ext in ['.txt', '.md']:
            return FileType.TEXT
        elif ext in ['.json']:
            return FileType.JSON
        elif ext in ['.xml']:
            return FileType.XML
        else:
            return FileType.OTHER
    
    def _generate_storage_path(self, workflow_id: int, step_id: Optional[int] = None) -> Path:
        """Generate structured storage path for files."""
        workflow_dir = self.base_storage_path / f"workflow_{workflow_id}"
        if step_id:
            return workflow_dir / f"step_{step_id}"
        return workflow_dir
    
    def _generate_filename(self, original_filename: str) -> str:
        """Generate unique filename to avoid conflicts."""
        ext = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{ext}"
    
    async def upload_file(
        self, 
        db: Session, 
        file: UploadFile, 
        workflow_id: int,
        step_id: Optional[int] = None,
        parent_file_id: Optional[int] = None
    ) -> FileUploadResponse:
        """Upload a file and create database record."""
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Generate storage path and filename
        storage_path = self._generate_storage_path(workflow_id, step_id)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        filename = self._generate_filename(file.filename)
        file_path = storage_path / filename
        
        # Save file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
        # Determine file type
        file_type = self._get_file_type(file.filename, file.content_type)
        
        # Create database record
        file_record = File(
            filename=filename,
            original_filename=file.filename,
            file_path=str(file_path.relative_to(self.base_storage_path)),
            file_size=len(content),
            file_type=file_type,
            mime_type=file.content_type,
            status=FileStatus.READY,
            workflow_id=workflow_id,
            input_step_id=step_id if step_id else None,
            output_step_id=step_id if step_id else None,
            parent_file_id=parent_file_id
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        return FileUploadResponse(
            file_id=file_record.id,
            filename=file_record.filename,
            file_path=file_record.file_path,
            file_size=file_record.file_size,
            status=file_record.status,
            message="File uploaded successfully"
        )
    
    def get_file_path(self, file_record: File) -> Path:
        """Get absolute file path from database record."""
        return self.base_storage_path / file_record.file_path
    
    def file_exists(self, file_record: File) -> bool:
        """Check if file exists on disk."""
        return self.get_file_path(file_record).exists()
    
    def delete_file(self, db: Session, file_id: int) -> bool:
        """Delete file from disk and database."""
        file_record = db.query(File).filter(File.id == file_id).first()
        if not file_record:
            return False
        
        # Delete from disk
        file_path = self.get_file_path(file_record)
        if file_path.exists():
            file_path.unlink()
        
        # Update database record
        file_record.status = FileStatus.DELETED
        db.commit()
        
        return True
    
    def get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from file."""
        metadata = {}
        
        if not file_path.exists():
            return metadata
        
        # Basic file info
        stat = file_path.stat()
        metadata['size'] = stat.st_size
        metadata['created'] = stat.st_ctime
        metadata['modified'] = stat.st_mtime
        
        # File type specific metadata (simplified without pandas)
        if file_path.suffix.lower() in ['.csv', '.xlsx', '.xls']:
            try:
                # Basic CSV parsing without pandas
                if file_path.suffix.lower() == '.csv':
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            # Count rows (excluding header)
                            metadata['row_count'] = len(lines) - 1
                            # Count columns from first line
                            metadata['column_count'] = len(lines[0].split(','))
                            # Sample first few lines
                            metadata['sample_data'] = lines[:5]
                else:
                    # For Excel files, just note the file type
                    metadata['file_type'] = 'excel'
                    metadata['note'] = 'Excel file - detailed parsing requires pandas'
                
            except Exception as e:
                metadata['error'] = str(e)
        
        return metadata
    
    def add_file_metadata(self, db: Session, file_id: int, metadata: Dict[str, Any]) -> None:
        """Add metadata to file record."""
        for key, value in metadata.items():
            if value is not None:
                metadata_record = FileMetadata(
                    file_id=file_id,
                    key=key,
                    value=str(value),
                    data_type=type(value).__name__
                )
                db.add(metadata_record)
        
        db.commit()
    
    def get_workflow_files(self, db: Session, workflow_id: int) -> List[File]:
        """Get all files for a workflow."""
        return db.query(File).filter(
            File.workflow_id == workflow_id,
            File.status != FileStatus.DELETED
        ).all()
    
    def get_step_files(self, db: Session, step_id: int) -> List[File]:
        """Get all files for a workflow step."""
        return db.query(File).filter(
            (File.input_step_id == step_id) | (File.output_step_id == step_id),
            File.status != FileStatus.DELETED
        ).all()
    
    def create_file_relationship(
        self, 
        db: Session, 
        file_id: int, 
        related_file_id: int, 
        relationship_type: str,
        confidence_score: Optional[int] = None
    ) -> None:
        """Create a relationship between two files."""
        from ..models.file import FileRelationship
        
        relationship = FileRelationship(
            file_id=file_id,
            related_file_id=related_file_id,
            relationship_type=relationship_type,
            confidence_score=confidence_score
        )
        
        db.add(relationship)
        db.commit() 