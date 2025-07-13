from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.dataset import Dataset, DatasetMatch
from ..schemas.dataset import (
    DatasetCreate, 
    DatasetResponse, 
    DatasetMatchResponse,
    DatasetProcessingRequest,
    DatasetProcessingResponse,
    MatchingConfig
)
from ..services.matching_service import MatchingService
from ..services.file_service import FileService
import os

router = APIRouter(prefix="/datasets", tags=["datasets"])

# Initialize services
matching_service = MatchingService()
file_service = FileService()

# Dataset endpoints
@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_dataset(
    dataset: DatasetCreate,
    db: Session = Depends(get_db)
):
    """Create a new dataset."""
    db_dataset = Dataset(**dataset.dict())
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

@router.get("/", response_model=List[DatasetResponse])
def get_datasets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all datasets."""
    datasets = db.query(Dataset).offset(skip).limit(limit).all()
    return datasets

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Get a specific dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Delete a dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    db.delete(dataset)
    db.commit()
    return None

# Dataset processing endpoints
@router.post("/process", response_model=DatasetProcessingResponse)
async def process_dataset(
    file: UploadFile = FastAPIFile(...),
    source_provider: Optional[str] = None,
    matching_config: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Process an uploaded dataset file and extract identifiers."""
    
    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create dataset record
        dataset = Dataset(
            name=file.filename,
            source_provider=source_provider,
            source_file_path=temp_path,
            file_type=file.filename.split('.')[-1] if '.' in file.filename else None,
            status="processing"
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        # Extract identifiers
        config = MatchingConfig(**matching_config) if matching_config else MatchingConfig()
        identifiers = matching_service.extract_identifiers(temp_path, config)
        
        # Update dataset with identifiers
        dataset.identifiers = identifiers
        dataset.matching_config = matching_config
        dataset.status = "pending"
        db.commit()
        
        return DatasetProcessingResponse(
            dataset_id=dataset.id,
            status=dataset.status,
            message="Dataset processed successfully",
            extracted_identifiers=identifiers
        )
        
    except Exception as e:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Failed to process dataset: {str(e)}")

# Dataset matching endpoints
@router.post("/{dataset_id}/match/{workflow_id}", response_model=List[DatasetMatchResponse])
def match_dataset_to_workflow(
    dataset_id: int,
    workflow_id: int,
    matching_config: Optional[MatchingConfig] = None,
    db: Session = Depends(get_db)
):
    """Match a dataset to a specific workflow."""
    
    if not matching_config:
        matching_config = MatchingConfig()
    
    matches = matching_service.find_matches(dataset_id, workflow_id, db, matching_config)
    
    # Save matches to database
    for match in matches:
        db.add(match)
    db.commit()
    
    return matches

@router.post("/{dataset_id}/auto-match", response_model=List[DatasetMatchResponse])
def auto_match_dataset(
    dataset_id: int,
    matching_config: Optional[MatchingConfig] = None,
    db: Session = Depends(get_db)
):
    """Automatically match a dataset to all workflows."""
    
    if not matching_config:
        matching_config = MatchingConfig()
    
    matches = matching_service.auto_match_dataset(dataset_id, db, matching_config)
    return matches

@router.get("/{dataset_id}/matches", response_model=List[DatasetMatchResponse])
def get_dataset_matches(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    """Get all matches for a dataset."""
    matches = db.query(DatasetMatch).filter(
        DatasetMatch.dataset_id == dataset_id
    ).all()
    return matches

# Dataset match management endpoints
@router.put("/matches/{match_id}/confirm")
def confirm_match(
    match_id: int,
    confirmed_by: str,
    db: Session = Depends(get_db)
):
    """Confirm a dataset match."""
    match = db.query(DatasetMatch).filter(DatasetMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match.is_confirmed = 1
    match.confirmed_by = confirmed_by
    db.commit()
    
    return {"message": "Match confirmed successfully"}

@router.put("/matches/{match_id}/reject")
def reject_match(
    match_id: int,
    rejected_by: str,
    db: Session = Depends(get_db)
):
    """Reject a dataset match."""
    match = db.query(DatasetMatch).filter(DatasetMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match.is_confirmed = -1
    match.confirmed_by = rejected_by
    db.commit()
    
    return {"message": "Match rejected successfully"}

# Workflow matching endpoints
@router.get("/workflow/{workflow_id}/matches", response_model=List[DatasetMatchResponse])
def get_workflow_matches(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """Get all dataset matches for a workflow."""
    matches = db.query(DatasetMatch).filter(
        DatasetMatch.workflow_id == workflow_id
    ).all()
    return matches 