from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DatasetStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    MATCHED = "matched"
    UNMATCHED = "unmatched"
    ERROR = "error"

class MatchType(str, Enum):
    EXACT = "exact"
    FUZZY = "fuzzy"
    ML_BASED = "ml_based"
    MANUAL = "manual"

# Dataset Schemas
class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    source_provider: Optional[str] = None
    source_file_path: Optional[str] = None
    file_type: Optional[str] = None
    matching_config: Optional[Dict[str, Any]] = None
    identifiers: Optional[Dict[str, Any]] = None

class DatasetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    source_provider: Optional[str]
    source_file_path: Optional[str]
    file_type: Optional[str]
    status: DatasetStatus
    matching_config: Optional[Dict[str, Any]]
    identifiers: Optional[Dict[str, Any]]
    row_count: Optional[int]
    column_count: Optional[int]
    file_size: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Dataset Match Schemas
class DatasetMatchCreate(BaseModel):
    workflow_id: int
    step_id: Optional[int] = None
    file_id: Optional[int] = None
    match_type: MatchType
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    matching_criteria: Optional[Dict[str, Any]] = None
    matched_identifiers: Optional[Dict[str, Any]] = None

class DatasetMatchResponse(BaseModel):
    id: int
    dataset_id: int
    workflow_id: int
    step_id: Optional[int]
    file_id: Optional[int]
    match_type: MatchType
    confidence_score: Optional[float]
    matching_criteria: Optional[Dict[str, Any]]
    matched_identifiers: Optional[Dict[str, Any]]
    is_confirmed: int
    confirmed_by: Optional[str]
    confirmed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dataset Processing Schemas
class DatasetProcessingRequest(BaseModel):
    file_path: str
    source_provider: Optional[str] = None
    matching_config: Optional[Dict[str, Any]] = None

class DatasetProcessingResponse(BaseModel):
    dataset_id: int
    status: DatasetStatus
    message: str
    extracted_identifiers: Optional[Dict[str, Any]] = None
    potential_matches: Optional[List[Dict[str, Any]]] = None

# Matching Configuration Schemas
class MatchingConfig(BaseModel):
    identifier_columns: List[str] = Field(default_factory=list)
    fuzzy_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    ml_model: Optional[str] = None
    custom_rules: Optional[Dict[str, Any]] = None 