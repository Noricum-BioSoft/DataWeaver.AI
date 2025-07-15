from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    BINARY = "binary"
    OTHER = "other"

class FileStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"

# File Schemas
class FileCreate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    original_filename: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_size: int = Field(..., gt=0)
    file_type: FileType
    mime_type: Optional[str] = None
    workflow_id: int
    input_step_id: Optional[int] = None
    output_step_id: Optional[int] = None
    parent_file_id: Optional[int] = None

class FileResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: FileType
    mime_type: Optional[str]
    status: FileStatus
    workflow_id: int
    input_step_id: Optional[int]
    output_step_id: Optional[int]
    parent_file_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    file_id: int
    filename: str
    file_path: str
    file_size: int
    status: FileStatus
    message: str

# File Metadata Schemas
class FileMetadataCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    value: Optional[str] = None
    data_type: str = Field(..., min_length=1, max_length=50)

class FileMetadataResponse(BaseModel):
    id: int
    file_id: int
    key: str
    value: Optional[str]
    data_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# File Relationship Schemas
class FileRelationshipCreate(BaseModel):
    related_file_id: int
    relationship_type: str = Field(..., min_length=1, max_length=100)
    confidence_score: Optional[int] = Field(None, ge=0, le=100)

class FileRelationshipResponse(BaseModel):
    id: int
    file_id: int
    related_file_id: int
    relationship_type: str
    confidence_score: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True 