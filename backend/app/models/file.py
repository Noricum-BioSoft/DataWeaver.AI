from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, JSON, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class FileType(enum.Enum):
    CSV = "csv"
    EXCEL = "excel"
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    BINARY = "binary"
    OTHER = "other"

class FileStatus(enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Relative path in storage
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    mime_type = Column(String(100))
    status = Column(Enum(FileStatus), default=FileStatus.UPLOADING)
    
    # Workflow and step relationships
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    input_step_id = Column(Integer, ForeignKey("workflow_steps.id"))
    output_step_id = Column(Integer, ForeignKey("workflow_steps.id"))
    
    # File relationships (for tracking input/output dependencies)
    parent_file_id = Column(Integer, ForeignKey("files.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="files")
    input_step = relationship("WorkflowStep", foreign_keys=[input_step_id], back_populates="input_files")
    output_step = relationship("WorkflowStep", foreign_keys=[output_step_id], back_populates="output_files")
    parent_file = relationship("File", remote_side=[id])
    child_files = relationship("File", back_populates="parent_file")
    file_metadata = relationship("FileMetadata", back_populates="file", cascade="all, delete-orphan")
    relationships = relationship("FileRelationship", back_populates="file", cascade="all, delete-orphan")

class FileMetadata(Base):
    __tablename__ = "file_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text)
    data_type = Column(String(50))  # string, number, boolean, json
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    file = relationship("File", back_populates="metadata")

class FileRelationship(Base):
    __tablename__ = "file_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    related_file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    relationship_type = Column(String(100), nullable=False)  # e.g., "derived_from", "input_for", "output_of"
    confidence_score = Column(Integer)  # 0-100 for ML-based relationships
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    file = relationship("File", foreign_keys=[file_id])
    related_file = relationship("File", foreign_keys=[related_file_id]) 