from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4
from datetime import datetime

from app.database import get_db
from models.bio_entities import Design, Build, Test
from services.bio_matcher import BioEntityMatcher, parse_upload_file

router = APIRouter(prefix="/bio", tags=["biological-entities"])


# Pydantic models for API requests/responses
class DesignBase(BaseModel):
    name: str
    alias: Optional[str] = None
    description: Optional[str] = None
    sequence: str
    sequence_type: str = "protein"
    mutation_list: Optional[str] = None
    parent_design_id: Optional[UUID4] = None


class DesignCreate(DesignBase):
    pass


class DesignResponse(DesignBase):
    id: UUID4
    lineage_hash: str
    generation: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BuildBase(BaseModel):
    name: str
    alias: Optional[str] = None
    description: Optional[str] = None
    sequence: str
    sequence_type: str = "protein"
    mutation_list: Optional[str] = None
    parent_build_id: Optional[UUID4] = None
    design_id: UUID4
    construct_type: Optional[str] = None
    build_status: str = "planned"


class BuildCreate(BuildBase):
    pass


class BuildResponse(BuildBase):
    id: UUID4
    lineage_hash: str
    generation: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TestBase(BaseModel):
    name: str
    alias: Optional[str] = None
    description: Optional[str] = None
    test_type: str
    assay_name: Optional[str] = None
    protocol: Optional[str] = None
    result_value: Optional[float] = None
    result_unit: Optional[str] = None
    result_type: Optional[str] = None
    design_id: Optional[UUID4] = None
    build_id: Optional[UUID4] = None
    technician: Optional[str] = None
    lab_conditions: Optional[str] = None


class TestCreate(TestBase):
    pass


class TestResponse(TestBase):
    id: UUID4
    match_confidence: Optional[str] = None
    match_method: Optional[str] = None
    match_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    total_rows: int
    matched_rows: int
    unmatched_rows: int
    high_confidence: int
    medium_confidence: int
    low_confidence: int
    matches: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


class LineageResponse(BaseModel):
    design: DesignResponse
    builds: List[BuildResponse]
    tests: List[TestResponse]


# Design endpoints
@router.post("/designs", response_model=DesignResponse)
def create_design(design: DesignCreate, db: Session = Depends(get_db)):
    """Create a new biological design"""
    db_design = Design(**design.dict())
    db.add(db_design)
    db.commit()
    db.refresh(db_design)
    return db_design


@router.get("/designs", response_model=List[DesignResponse])
def get_designs(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    sequence: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all designs with optional filtering"""
    query = db.query(Design).filter(Design.is_active == True)
    
    if name:
        query = query.filter(Design.name.ilike(f"%{name}%"))
    if sequence:
        query = query.filter(Design.sequence.ilike(f"%{sequence}%"))
    
    return query.offset(skip).limit(limit).all()


@router.get("/designs/{design_id}", response_model=DesignResponse)
def get_design(design_id: UUID4, db: Session = Depends(get_db)):
    """Get a specific design by ID"""
    design = db.query(Design).filter(
        Design.id == design_id,
        Design.is_active == True
    ).first()
    
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    
    return design


# Build endpoints
@router.post("/builds", response_model=BuildResponse)
def create_build(build: BuildCreate, db: Session = Depends(get_db)):
    """Create a new biological build"""
    db_build = Build(**build.dict())
    db.add(db_build)
    db.commit()
    db.refresh(db_build)
    return db_build


@router.get("/builds", response_model=List[BuildResponse])
def get_builds(
    skip: int = 0,
    limit: int = 100,
    design_id: Optional[UUID4] = None,
    build_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all builds with optional filtering"""
    query = db.query(Build).filter(Build.is_active == True)
    
    if design_id:
        query = query.filter(Build.design_id == design_id)
    if build_status:
        query = query.filter(Build.build_status == build_status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/builds/{build_id}", response_model=BuildResponse)
def get_build(build_id: UUID4, db: Session = Depends(get_db)):
    """Get a specific build by ID"""
    build = db.query(Build).filter(
        Build.id == build_id,
        Build.is_active == True
    ).first()
    
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    return build


# Test endpoints
@router.get("/tests", response_model=List[TestResponse])
def get_tests(
    skip: int = 0,
    limit: int = 100,
    design_id: Optional[UUID4] = None,
    build_id: Optional[UUID4] = None,
    test_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all tests with optional filtering"""
    query = db.query(Test).filter(Test.is_active == True)
    
    if design_id:
        query = query.filter(Test.design_id == design_id)
    if build_id:
        query = query.filter(Test.build_id == build_id)
    if test_type:
        query = query.filter(Test.test_type == test_type)
    
    return query.offset(skip).limit(limit).all()


@router.get("/tests/{test_id}", response_model=TestResponse)
def get_test(test_id: UUID4, db: Session = Depends(get_db)):
    """Get a specific test by ID"""
    test = db.query(Test).filter(
        Test.id == test_id,
        Test.is_active == True
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    return test


# Upload and matching endpoints
@router.post("/upload-test-results", response_model=UploadResponse)
async def upload_test_results(
    file: UploadFile = File(...),
    test_type: str = Form("activity"),
    assay_name: Optional[str] = Form(None),
    protocol: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload test results file and automatically match to biological entities"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse file
        df = parse_upload_file(file_content, file.filename)
        
        # Add default columns if missing
        if 'test_type' not in df.columns:
            df['test_type'] = test_type
        if 'assay_name' not in df.columns:
            df['assay_name'] = assay_name
        if 'protocol' not in df.columns:
            df['protocol'] = protocol
        
        # Process upload with matching
        matcher = BioEntityMatcher(db)
        results = matcher.process_upload(df)
        
        return UploadResponse(**results)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@router.post("/match-preview")
async def match_preview(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Preview matching results without committing to database"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse file
        df = parse_upload_file(file_content, file.filename)
        
        # Preview matching without committing
        matcher = BioEntityMatcher(db)
        preview_results = {
            'total_rows': len(df),
            'matched_rows': 0,
            'unmatched_rows': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'matches': [],
            'errors': []
        }
        
        for index, row in df.iterrows():
            try:
                row_data = row.to_dict()
                match_result = matcher.match_row(row_data)
                
                if match_result['matched']:
                    preview_results['matched_rows'] += 1
                    confidence = match_result['confidence']
                    if confidence == 'high':
                        preview_results['high_confidence'] += 1
                    elif confidence == 'medium':
                        preview_results['medium_confidence'] += 1
                    elif confidence == 'low':
                        preview_results['low_confidence'] += 1
                    
                    preview_results['matches'].append({
                        'row_index': index,
                        'match_result': match_result,
                        'row_data': row_data
                    })
                else:
                    preview_results['unmatched_rows'] += 1
                    preview_results['errors'].append({
                        'row_index': index,
                        'error': 'No match found',
                        'data': row_data
                    })
                    
            except Exception as e:
                preview_results['unmatched_rows'] += 1
                preview_results['errors'].append({
                    'row_index': index,
                    'error': str(e),
                    'data': row.to_dict()
                })
        
        return preview_results
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


# Lineage tracking endpoints
@router.get("/lineage/{design_id}", response_model=LineageResponse)
def get_lineage(design_id: UUID4, db: Session = Depends(get_db)):
    """Get complete lineage for a design including all builds and tests"""
    
    design = db.query(Design).filter(
        Design.id == design_id,
        Design.is_active == True
    ).first()
    
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    
    builds = db.query(Build).filter(
        Build.design_id == design_id,
        Build.is_active == True
    ).all()
    
    tests = db.query(Test).filter(
        Test.design_id == design_id,
        Test.is_active == True
    ).all()
    
    return LineageResponse(
        design=design,
        builds=builds,
        tests=tests
    )


# Statistics endpoints
@router.get("/stats")
def get_bio_stats(db: Session = Depends(get_db)):
    """Get statistics about biological entities"""
    
    design_count = db.query(Design).filter(Design.is_active == True).count()
    build_count = db.query(Build).filter(Build.is_active == True).count()
    test_count = db.query(Test).filter(Test.is_active == True).count()
    
    # Match confidence statistics
    high_confidence_tests = db.query(Test).filter(
        Test.match_confidence == 'high',
        Test.is_active == True
    ).count()
    
    medium_confidence_tests = db.query(Test).filter(
        Test.match_confidence == 'medium',
        Test.is_active == True
    ).count()
    
    low_confidence_tests = db.query(Test).filter(
        Test.match_confidence == 'low',
        Test.is_active == True
    ).count()
    
    return {
        'total_designs': design_count,
        'total_builds': build_count,
        'total_tests': test_count,
        'high_confidence_matches': high_confidence_tests,
        'medium_confidence_matches': medium_confidence_tests,
        'low_confidence_matches': low_confidence_tests
    } 