from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from fastapi import File as FastAPIFile
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4
from datetime import datetime

from app.database import get_db
from models.bio_entities import Design, Build, Test
from services.bio_matcher import BioEntityMatcher, parse_upload_file
from app.models.file import File

router = APIRouter(tags=["biological-entities"])


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
    print("DEBUG: get_designs endpoint called")
    
    query = db.query(Design).filter(Design.is_active == True)
    
    if name:
        query = query.filter(Design.name.ilike(f"%{name}%"))
    if sequence:
        query = query.filter(Design.sequence.ilike(f"%{sequence}%"))
    
    results = query.offset(skip).limit(limit).all()
    print(f"DEBUG: Found {len(results)} designs in database")
    for r in results:
        print(f"DEBUG: Design {r.id}: {r.name}, is_active: {r.is_active}")
    
    # Return plain dicts instead of Pydantic models for testing
    plain_results = []
    for r in results:
        plain_dict = {
            "id": str(r.id),
            "name": r.name,
            "alias": r.alias,
            "description": r.description,
            "sequence": r.sequence,
            "sequence_type": r.sequence_type,
            "mutation_list": r.mutation_list,
            "parent_design_id": str(r.parent_design_id) if r.parent_design_id is not None else None,
            "lineage_hash": r.lineage_hash,
            "generation": r.generation,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        }
        plain_results.append(plain_dict)
    
    print(f"DEBUG: Returning {len(plain_results)} plain dicts")
    return plain_results


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
    
    results = query.offset(skip).limit(limit).all()
    # Explicitly convert to Pydantic models
    return [BuildResponse.model_validate(r) for r in results]


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
@router.post("/tests", response_model=TestResponse)
def create_test(test: TestCreate, db: Session = Depends(get_db)):
    """Create a new biological test"""
    db_test = Test(**test.dict())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


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
    
    results = query.offset(skip).limit(limit).all()
    # Explicitly convert to Pydantic models
    return [TestResponse.model_validate(r) for r in results]


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
    file: UploadFile = FastAPIFile(...),
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
    file: UploadFile = FastAPIFile(...),
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
    total_designs = db.query(Design).filter(Design.is_active == True).count()
    total_builds = db.query(Build).filter(Build.is_active == True).count()
    total_tests = db.query(Test).filter(Test.is_active == True).count()
    
    return {
        "total_designs": total_designs,
        "total_builds": total_builds,
        "total_tests": total_tests
    }

@router.post("/process-file/{file_id}")
def process_file(
    file_id: str,
    process_type: str = "assay_results",
    enable_matching: bool = False,
    db: Session = Depends(get_db)
):
    """Process a file for bio entities"""
    try:
        # Get the file record
        file_record = db.query(File).filter(File.id == int(file_id)).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Read and parse the CSV file
        import pandas as pd
        from pathlib import Path
        
        file_path = Path(file_record.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        # Read CSV
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")
        
        processed_rows = 0
        created_designs = 0
        created_tests = 0
        matched_entities = 0
        
        # Process each row
        for index, row in df.iterrows():
            try:
                row_data = row.to_dict()
                
                # Extract data from CSV
                name = row_data.get('name', f'Design_{index}')
                alias = row_data.get('alias', name)
                sequence = row_data.get('sequence', '')
                mutations = row_data.get('mutations', '')
                result_value = row_data.get('result_value')
                result_unit = row_data.get('result_unit', '')
                test_type = row_data.get('test_type', 'activity')
                assay_name = row_data.get('assay_name', '')
                technician = row_data.get('technician', '')
                
                # Create or find design
                design = db.query(Design).filter(
                    Design.alias == alias,
                    Design.is_active == True
                ).first()
                
                if not design:
                    # Create new design
                    design = Design(
                        name=name,
                        alias=alias,
                        description=f"Design from {file_record.original_filename}",
                        sequence=sequence,
                        sequence_type="protein",
                        mutation_list=mutations,
                        lineage_hash=f"hash_{alias}_{index}"
                    )
                    db.add(design)
                    db.flush()  # Get the ID
                    created_designs += 1
                
                # Create test record
                test = Test(
                    name=f"Test_{name}_{index}",
                    alias=f"TEST_{alias}_{index}",
                    description=f"Test from {file_record.original_filename}",
                    test_type=test_type,
                    result_value=float(result_value) if result_value is not None else None,
                    result_unit=result_unit,
                    assay_name=assay_name,
                    technician=technician,
                    design_id=design.id,
                    match_confidence="high" if design else "low",
                    match_method="sequence" if design else "none",
                    match_score=1.0 if design else 0.0
                )
                db.add(test)
                created_tests += 1
                
                if design:
                    matched_entities += 1
                
                processed_rows += 1
                
            except Exception as e:
                # Log error but continue processing
                continue
        
        # Commit all changes
        db.commit()
        
        return {
            "processed_rows": processed_rows,
            "matched_entities": matched_entities,
            "created_tests": created_tests,
            "created_designs": created_designs,
            "file_id": file_id,
            "process_type": process_type
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/designs/{design_id}/export")
def export_design(design_id: UUID4, db: Session = Depends(get_db)):
    """Export a design with all its data"""
    design = db.query(Design).filter(
        Design.id == design_id,
        Design.is_active == True
    ).first()
    
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    
    return {
        "id": str(design.id),
        "name": design.name,
        "alias": design.alias,
        "description": design.description,
        "sequence": design.sequence,
        "sequence_type": design.sequence_type,
        "mutation_list": design.mutation_list,
        "lineage_hash": design.lineage_hash,
        "generation": design.generation,
        "created_at": design.created_at,
        "updated_at": design.updated_at
    }

@router.get("/lineage/{design_id}/export")
def export_lineage(design_id: UUID4, db: Session = Depends(get_db)):
    """Export a complete lineage (design, builds, tests)"""
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
    
    return {
        "design": {
            "id": str(design.id),
            "name": design.name,
            "alias": design.alias,
            "description": design.description,
            "sequence": design.sequence,
            "sequence_type": design.sequence_type,
            "mutation_list": design.mutation_list,
            "lineage_hash": design.lineage_hash,
            "generation": design.generation,
            "created_at": design.created_at,
            "updated_at": design.updated_at
        },
        "builds": [
            {
                "id": str(build.id),
                "name": build.name,
                "alias": build.alias,
                "description": build.description,
                "sequence": build.sequence,
                "sequence_type": build.sequence_type,
                "mutation_list": build.mutation_list,
                "design_id": str(build.design_id),
                "construct_type": build.construct_type,
                "build_status": build.build_status,
                "lineage_hash": build.lineage_hash,
                "generation": build.generation,
                "created_at": build.created_at,
                "updated_at": build.updated_at
            }
            for build in builds
        ],
        "tests": [
            {
                "id": str(test.id),
                "name": test.name,
                "alias": test.alias,
                "description": test.description,
                "test_type": test.test_type,
                "assay_name": test.assay_name,
                "protocol": test.protocol,
                "result_value": test.result_value,
                "result_unit": test.result_unit,
                "result_type": test.result_type,
                "design_id": str(test.design_id) if test.design_id else None,
                "build_id": str(test.build_id) if test.build_id else None,
                "technician": test.technician,
                "lab_conditions": test.lab_conditions,
                "match_confidence": test.match_confidence,
                "match_method": test.match_method,
                "match_score": test.match_score,
                "created_at": test.created_at,
                "updated_at": test.updated_at
            }
            for test in tests
        ]
    } 