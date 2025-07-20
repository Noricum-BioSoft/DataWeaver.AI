from sqlalchemy import Column, String, DateTime, Float, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base


class WorkflowProject(Base):
    __tablename__ = "workflow_projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String, nullable=False)
    project_description = Column(Text)
    target_protein = Column(String)
    project_manager = Column(String)
    priority = Column(String, default="medium")
    status = Column(String, default="design")
    start_date = Column(DateTime)
    target_completion = Column(DateTime)
    actual_completion = Column(DateTime)
    budget = Column(Float)
    vendor_costs = Column(Float)
    test_costs = Column(Float)
    project_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DesignPhase(Base):
    __tablename__ = "design_phases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(String, nullable=False)
    design_name = Column(String, nullable=False)
    original_sequence = Column(Text, nullable=False)
    optimized_sequence = Column(Text)
    vector_sequence = Column(Text)
    host_organism = Column(String)
    expression_system = Column(String)
    design_parameters = Column(JSON)
    optimization_score = Column(Float)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BuildPhase(Base):
    __tablename__ = "build_phases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    design_id = Column(UUID(as_uuid=True), ForeignKey("design_phases.id"))
    build_name = Column(String, nullable=False)
    vendor_name = Column(String)
    vendor_id = Column(String)
    order_date = Column(DateTime)
    expected_completion = Column(DateTime)
    actual_completion = Column(DateTime)
    plasmid_concentration = Column(Float)
    plasmid_volume = Column(Float)
    sequence_verification = Column(String)
    gel_analysis = Column(String)
    qc_results = Column(JSON)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TestPhase(Base):
    __tablename__ = "test_phases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    design_id = Column(UUID(as_uuid=True), ForeignKey("design_phases.id"))
    build_id = Column(UUID(as_uuid=True), ForeignKey("build_phases.id"))
    test_name = Column(String, nullable=False)
    test_type = Column(String, nullable=False)
    expression_level = Column(String)
    protein_concentration = Column(Float)
    enzyme_activity = Column(Float)
    km_value = Column(Float)
    vmax_value = Column(Float)
    assay_conditions = Column(JSON)
    test_results = Column(JSON)
    quality_metrics = Column(JSON)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowFile(Base):
    __tablename__ = "workflow_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("workflow_projects.id"))
    phase_id = Column(UUID(as_uuid=True))
    phase_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    description = Column(Text)
    file_metadata = Column(JSON)
    upload_date = Column(DateTime, default=datetime.utcnow)


class WorkflowCorrelation(Base):
    __tablename__ = "workflow_correlations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("workflow_projects.id"))
    source_phase = Column(String, nullable=False)
    target_phase = Column(String, nullable=False)
    correlation_type = Column(String, nullable=False)
    correlation_score = Column(Float)
    correlation_data = Column(JSON)
    analysis_date = Column(DateTime, default=datetime.utcnow) 