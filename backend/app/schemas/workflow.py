from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class WorkflowStatus(str, Enum):
    DRAFT = "DRAFT"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class StepType(str, Enum):
    INPUT = "INPUT"
    PROCESSING = "PROCESSING"
    OUTPUT = "OUTPUT"
    EXTERNAL = "EXTERNAL"

# Workflow Schemas
class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    workflow_metadata: Optional[Dict[str, Any]] = None

class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[WorkflowStatus] = None
    workflow_metadata: Optional[Dict[str, Any]] = None

class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: WorkflowStatus
    created_at: datetime
    updated_at: Optional[datetime]
    workflow_metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

# Workflow Step Schemas
class WorkflowStepCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    step_type: StepType
    order_index: int = Field(..., ge=0)
    external_provider: Optional[str] = None
    external_config: Optional[Dict[str, Any]] = None

class WorkflowStepUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    step_type: Optional[StepType] = None
    status: Optional[StepStatus] = None
    order_index: Optional[int] = Field(None, ge=0)
    external_provider: Optional[str] = None
    external_config: Optional[Dict[str, Any]] = None

class WorkflowStepResponse(BaseModel):
    id: int
    workflow_id: int
    name: str
    description: Optional[str]
    step_type: StepType
    status: StepStatus
    order_index: int
    external_provider: Optional[str]
    external_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True 