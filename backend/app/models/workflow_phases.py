from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text, Float, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..database import Base


class DesignPhase(Base):
    """Design phase entities for protein engineering workflows"""
    __tablename__ = "design_phases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("workflow_projects.id"), nullable=False, index=True)
    design_name = Column(String, nullable=False)
    original_sequence = Column(Text, nullable=False)
    optimized_sequence = Column(Text)
    vector_sequence = Column(Text)
    host_organism = Column(String)
    expression_system = Column(String)
    design_parameters = Column(JSON)
    optimization_score = Column(Float)
    status = Column(String, default="draft")  # draft, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("WorkflowProject", back_populates="design_phases")
    build_phases = relationship("BuildPhase", back_populates="design_phase")
    test_phases = relationship("TestPhase", back_populates="design_phase")


class BuildPhase(Base):
    """Build phase entities for plasmid construction and vendor coordination"""
    __tablename__ = "build_phases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    design_id = Column(UUID(as_uuid=True), ForeignKey("design_phases.id"), nullable=False)
    build_name = Column(String, nullable=False)
    vendor_name = Column(String)
    vendor_id = Column(String)
    order_date = Column(DateTime)
    expected_completion = Column(DateTime)
    actual_completion = Column(DateTime)
    plasmid_concentration = Column(Float)
    plasmid_volume = Column(Float)
    sequence_verification = Column(String)  # passed, failed, pending
    gel_analysis = Column(String)  # passed, failed, pending
    qc_results = Column(JSON)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    design_phase = relationship("DesignPhase", back_populates="build_phases")
    test_phases = relationship("TestPhase", back_populates="build_phase")


class TestPhase(Base):
    """Test phase entities for expression and activity assays"""
    __tablename__ = "test_phases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    design_id = Column(UUID(as_uuid=True), ForeignKey("design_phases.id"), nullable=False)
    build_id = Column(UUID(as_uuid=True), ForeignKey("build_phases.id"), nullable=False)
    test_name = Column(String, nullable=False)
    test_type = Column(String, nullable=False)  # expression, activity, functional, stability
    expression_level = Column(String)  # low, medium, high
    protein_concentration = Column(Float)
    enzyme_activity = Column(Float)
    km_value = Column(Float)
    vmax_value = Column(Float)
    assay_conditions = Column(JSON)
    test_results = Column(JSON)
    quality_metrics = Column(JSON)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    design_phase = relationship("DesignPhase", back_populates="test_phases")
    build_phase = relationship("BuildPhase", back_populates="test_phases")


class WorkflowProject(Base):
    """Master project entity that tracks the entire design-build-test workflow"""
    __tablename__ = "workflow_projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String, nullable=False)
    project_description = Column(Text)
    target_protein = Column(String)
    project_manager = Column(String)
    priority = Column(String, default="medium")  # low, medium, high, urgent
    status = Column(String, default="design")  # design, build, test, completed, failed
    start_date = Column(DateTime, default=datetime.utcnow)
    target_completion = Column(DateTime)
    actual_completion = Column(DateTime)
    budget = Column(Float)
    vendor_costs = Column(Float)
    test_costs = Column(Float)
    project_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    design_phases = relationship("DesignPhase", back_populates="project")


class WorkflowFile(Base):
    """File tracking for workflow documents and data"""
    __tablename__ = "workflow_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("workflow_projects.id"), nullable=False)
    phase_id = Column(UUID(as_uuid=True), nullable=False)  # Generic phase ID
    phase_type = Column(String, nullable=False)  # design, build, test
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # fasta, csv, pdf, jpg, etc.
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    file_metadata = Column(JSON)
    
    # Relationships
    project = relationship("WorkflowProject", backref="files")


class WorkflowCorrelation(Base):
    """Correlation analysis between different workflow phases"""
    __tablename__ = "workflow_correlations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("workflow_projects.id"), nullable=False)
    source_phase = Column(String, nullable=False)  # design, build, test
    target_phase = Column(String, nullable=False)  # design, build, test
    correlation_type = Column(String, nullable=False)  # sequence, expression, activity, performance
    correlation_score = Column(Float)
    correlation_data = Column(JSON)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    project = relationship("WorkflowProject", backref="correlations") 