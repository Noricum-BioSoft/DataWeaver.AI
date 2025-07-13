from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.workflow import Workflow, WorkflowStep
from ..schemas.workflow import (
    WorkflowCreate, 
    WorkflowUpdate, 
    WorkflowResponse,
    WorkflowStepCreate,
    WorkflowStepUpdate,
    WorkflowStepResponse
)

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Workflow endpoints
@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(
    workflow: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """Create a new workflow."""
    db_workflow = Workflow(**workflow.dict())
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@router.get("/", response_model=List[WorkflowResponse])
def get_workflows(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all workflows."""
    workflows = db.query(Workflow).offset(skip).limit(limit).all()
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Get a specific workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: int,
    workflow_update: WorkflowUpdate,
    db: Session = Depends(get_db)
):
    """Update a workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    update_data = workflow_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    db.commit()
    db.refresh(workflow)
    return workflow

@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Delete a workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    return None

# Workflow Step endpoints
@router.post("/{workflow_id}/steps", response_model=WorkflowStepResponse, status_code=status.HTTP_201_CREATED)
def create_workflow_step(
    workflow_id: int,
    step: WorkflowStepCreate,
    db: Session = Depends(get_db)
):
    """Create a new workflow step."""
    # Verify workflow exists
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db_step = WorkflowStep(**step.dict(), workflow_id=workflow_id)
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    return db_step

@router.get("/{workflow_id}/steps", response_model=List[WorkflowStepResponse])
def get_workflow_steps(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """Get all steps for a workflow."""
    # Verify workflow exists
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    steps = db.query(WorkflowStep).filter(
        WorkflowStep.workflow_id == workflow_id
    ).order_by(WorkflowStep.order_index).all()
    return steps

@router.get("/{workflow_id}/steps/{step_id}", response_model=WorkflowStepResponse)
def get_workflow_step(
    workflow_id: int,
    step_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific workflow step."""
    step = db.query(WorkflowStep).filter(
        WorkflowStep.id == step_id,
        WorkflowStep.workflow_id == workflow_id
    ).first()
    if not step:
        raise HTTPException(status_code=404, detail="Workflow step not found")
    return step

@router.put("/{workflow_id}/steps/{step_id}", response_model=WorkflowStepResponse)
def update_workflow_step(
    workflow_id: int,
    step_id: int,
    step_update: WorkflowStepUpdate,
    db: Session = Depends(get_db)
):
    """Update a workflow step."""
    step = db.query(WorkflowStep).filter(
        WorkflowStep.id == step_id,
        WorkflowStep.workflow_id == workflow_id
    ).first()
    if not step:
        raise HTTPException(status_code=404, detail="Workflow step not found")
    
    update_data = step_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(step, field, value)
    
    db.commit()
    db.refresh(step)
    return step

@router.delete("/{workflow_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow_step(
    workflow_id: int,
    step_id: int,
    db: Session = Depends(get_db)
):
    """Delete a workflow step."""
    step = db.query(WorkflowStep).filter(
        WorkflowStep.id == step_id,
        WorkflowStep.workflow_id == workflow_id
    ).first()
    if not step:
        raise HTTPException(status_code=404, detail="Workflow step not found")
    
    db.delete(step)
    db.commit()
    return None 