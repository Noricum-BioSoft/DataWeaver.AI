from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class WorkflowStatus(enum.Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StepStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class StepType(enum.Enum):
    INPUT = "input"
    PROCESSING = "processing"
    OUTPUT = "output"
    EXTERNAL = "external"

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    workflow_metadata = Column(JSON)  # For flexible workflow-specific data
    
    # Relationships
    steps = relationship("WorkflowStep", back_populates="workflow", cascade="all, delete-orphan")
    files = relationship("File", back_populates="workflow")

class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    step_type = Column(Enum(StepType), nullable=False)
    status = Column(Enum(StepStatus), default=StepStatus.PENDING)
    order_index = Column(Integer, nullable=False)
    external_provider = Column(String(255))  # For external API calls
    external_config = Column(JSON)  # Configuration for external providers
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="steps")
    input_files = relationship("File", foreign_keys="File.input_step_id", back_populates="input_step")
    output_files = relationship("File", foreign_keys="File.output_step_id", back_populates="output_step") 