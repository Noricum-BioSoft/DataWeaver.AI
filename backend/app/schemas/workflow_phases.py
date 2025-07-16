from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class DesignPhaseBase(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    design_name: str = Field(..., description="Name of the design")
    original_sequence: str = Field(..., description="Original protein sequence")
    optimized_sequence: Optional[str] = Field(None, description="Codon-optimized sequence")
    vector_sequence: Optional[str] = Field(None, description="Vector sequence")
    host_organism: Optional[str] = Field(None, description="Target host organism")
    expression_system: Optional[str] = Field(None, description="Expression system used")
    design_parameters: Optional[Dict[str, Any]] = Field(None, description="Design parameters")
    optimization_score: Optional[float] = Field(None, description="Optimization score")
    status: str = Field("draft", description="Design status")


class DesignPhaseCreate(DesignPhaseBase):
    pass


class DesignPhaseUpdate(BaseModel):
    optimized_sequence: Optional[str] = None
    vector_sequence: Optional[str] = None
    host_organism: Optional[str] = None
    expression_system: Optional[str] = None
    design_parameters: Optional[Dict[str, Any]] = None
    optimization_score: Optional[float] = None
    status: Optional[str] = None


class DesignPhase(DesignPhaseBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BuildPhaseBase(BaseModel):
    design_id: UUID = Field(..., description="Associated design phase ID")
    build_name: str = Field(..., description="Name of the build")
    vendor_name: Optional[str] = Field(None, description="Vendor name")
    vendor_id: Optional[str] = Field(None, description="Vendor identifier")
    order_date: Optional[datetime] = Field(None, description="Order date")
    expected_completion: Optional[datetime] = Field(None, description="Expected completion date")
    actual_completion: Optional[datetime] = Field(None, description="Actual completion date")
    plasmid_concentration: Optional[float] = Field(None, description="Plasmid concentration")
    plasmid_volume: Optional[float] = Field(None, description="Plasmid volume")
    sequence_verification: Optional[str] = Field(None, description="Sequence verification status")
    gel_analysis: Optional[str] = Field(None, description="Gel analysis status")
    qc_results: Optional[Dict[str, Any]] = Field(None, description="QC results")
    status: str = Field("pending", description="Build status")


class BuildPhaseCreate(BuildPhaseBase):
    pass


class BuildPhaseUpdate(BaseModel):
    vendor_name: Optional[str] = None
    vendor_id: Optional[str] = None
    order_date: Optional[datetime] = None
    expected_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    plasmid_concentration: Optional[float] = None
    plasmid_volume: Optional[float] = None
    sequence_verification: Optional[str] = None
    gel_analysis: Optional[str] = None
    qc_results: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class BuildPhase(BuildPhaseBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TestPhaseBase(BaseModel):
    design_id: UUID = Field(..., description="Associated design phase ID")
    build_id: UUID = Field(..., description="Associated build phase ID")
    test_name: str = Field(..., description="Name of the test")
    test_type: str = Field(..., description="Type of test (expression, activity, functional, stability)")
    expression_level: Optional[str] = Field(None, description="Expression level")
    protein_concentration: Optional[float] = Field(None, description="Protein concentration")
    enzyme_activity: Optional[float] = Field(None, description="Enzyme activity")
    km_value: Optional[float] = Field(None, description="Km value")
    vmax_value: Optional[float] = Field(None, description="Vmax value")
    assay_conditions: Optional[Dict[str, Any]] = Field(None, description="Assay conditions")
    test_results: Optional[Dict[str, Any]] = Field(None, description="Test results")
    quality_metrics: Optional[Dict[str, Any]] = Field(None, description="Quality metrics")
    status: str = Field("pending", description="Test status")


class TestPhaseCreate(TestPhaseBase):
    pass


class TestPhaseUpdate(BaseModel):
    expression_level: Optional[str] = None
    protein_concentration: Optional[float] = None
    enzyme_activity: Optional[float] = None
    km_value: Optional[float] = None
    vmax_value: Optional[float] = None
    assay_conditions: Optional[Dict[str, Any]] = None
    test_results: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class TestPhase(TestPhaseBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowProjectBase(BaseModel):
    project_name: str = Field(..., description="Project name")
    project_description: Optional[str] = Field(None, description="Project description")
    target_protein: Optional[str] = Field(None, description="Target protein")
    project_manager: Optional[str] = Field(None, description="Project manager")
    priority: str = Field("medium", description="Project priority")
    status: str = Field("design", description="Project status")
    start_date: Optional[datetime] = Field(None, description="Start date")
    target_completion: Optional[datetime] = Field(None, description="Target completion date")
    actual_completion: Optional[datetime] = Field(None, description="Actual completion date")
    budget: Optional[float] = Field(None, description="Project budget")
    vendor_costs: Optional[float] = Field(None, description="Vendor costs")
    test_costs: Optional[float] = Field(None, description="Test costs")
    project_metadata: Optional[Dict[str, Any]] = Field(None, description="Project metadata")


class WorkflowProjectCreate(WorkflowProjectBase):
    pass


class WorkflowProjectUpdate(BaseModel):
    project_description: Optional[str] = None
    target_protein: Optional[str] = None
    project_manager: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    target_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    budget: Optional[float] = None
    vendor_costs: Optional[float] = None
    test_costs: Optional[float] = None
    project_metadata: Optional[Dict[str, Any]] = None


class WorkflowProject(WorkflowProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowFileBase(BaseModel):
    project_id: UUID = Field(..., description="Project ID")
    phase_id: UUID = Field(..., description="Phase ID")
    phase_type: str = Field(..., description="Phase type (design, build, test)")
    file_name: str = Field(..., description="File name")
    file_type: str = Field(..., description="File type")
    file_path: str = Field(..., description="File path")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    description: Optional[str] = Field(None, description="File description")
    file_metadata: Optional[Dict[str, Any]] = Field(None, description="File metadata")


class WorkflowFileCreate(WorkflowFileBase):
    pass


class WorkflowFile(WorkflowFileBase):
    id: UUID
    upload_date: datetime
    
    class Config:
        from_attributes = True


class WorkflowCorrelationBase(BaseModel):
    project_id: UUID = Field(..., description="Project ID")
    source_phase: str = Field(..., description="Source phase")
    target_phase: str = Field(..., description="Target phase")
    correlation_type: str = Field(..., description="Correlation type")
    correlation_score: Optional[float] = Field(None, description="Correlation score")
    correlation_data: Optional[Dict[str, Any]] = Field(None, description="Correlation data")
    notes: Optional[str] = Field(None, description="Analysis notes")


class WorkflowCorrelationCreate(WorkflowCorrelationBase):
    pass


class WorkflowCorrelation(WorkflowCorrelationBase):
    id: UUID
    analysis_date: datetime
    
    class Config:
        from_attributes = True


# Response models for workflow summaries
class WorkflowSummary(BaseModel):
    project: WorkflowProject
    design_phases: List[DesignPhase]
    build_phases: List[BuildPhase]
    test_phases: List[TestPhase]
    files: List[WorkflowFile]
    correlations: List[WorkflowCorrelation]


class WorkflowStatus(BaseModel):
    project_id: UUID
    project_name: str
    current_phase: str
    design_count: int
    build_count: int
    test_count: int
    completion_percentage: float
    next_steps: List[str] 