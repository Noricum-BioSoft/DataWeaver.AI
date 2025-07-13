from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class DatasetStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    MATCHED = "matched"
    UNMATCHED = "unmatched"
    ERROR = "error"

class MatchType(enum.Enum):
    EXACT = "exact"
    FUZZY = "fuzzy"
    ML_BASED = "ml_based"
    MANUAL = "manual"

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    source_provider = Column(String(255))  # External provider name
    source_file_path = Column(String(500))  # Path to the external file
    file_type = Column(String(50))  # csv, excel, etc.
    status = Column(Enum(DatasetStatus), default=DatasetStatus.PENDING)
    
    # Matching configuration
    matching_config = Column(JSON)  # Configuration for matching logic
    identifiers = Column(JSON)  # Extracted identifiers for matching
    
    # Metadata
    row_count = Column(Integer)
    column_count = Column(Integer)
    file_size = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    matches = relationship("DatasetMatch", back_populates="dataset", cascade="all, delete-orphan")

class DatasetMatch(Base):
    __tablename__ = "dataset_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    step_id = Column(Integer, ForeignKey("workflow_steps.id"))
    file_id = Column(Integer, ForeignKey("files.id"))
    
    # Matching details
    match_type = Column(Enum(MatchType), nullable=False)
    confidence_score = Column(Float)  # 0.0 to 1.0
    matching_criteria = Column(JSON)  # What criteria were used for matching
    matched_identifiers = Column(JSON)  # Which identifiers matched
    
    # User confirmation
    is_confirmed = Column(Integer, default=0)  # 0 = pending, 1 = confirmed, -1 = rejected
    confirmed_by = Column(String(255))
    confirmed_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    dataset = relationship("Dataset", back_populates="matches")
    workflow = relationship("Workflow")
    step = relationship("WorkflowStep")
    file = relationship("File") 