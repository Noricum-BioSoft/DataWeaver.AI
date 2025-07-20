"""
Intelligent Data Merging API
Provides endpoints for analyzing and merging multiple files intelligently
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import tempfile
import os
import uuid
from pathlib import Path

from ..database import get_db
from ..services.intelligent_merger import IntelligentMerger, MergeSuggestion, FileAnalysis, MergeStrategy
from ..models.file import File as FileModel
from ..models.workflow import Workflow

router = APIRouter(prefix="/intelligent-merge", tags=["intelligent-merge"])

# Initialize the intelligent merger service
merger = IntelligentMerger()

@router.post("/analyze-files")
async def analyze_files_for_merge(
    files: List[UploadFile] = File(...),
    workflow_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze multiple files and suggest merge strategies
    """
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files are required for merging")
    
    # Save uploaded files temporarily
    temp_files = []
    file_infos = []
    
    try:
        for upload_file in files:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(upload_file.filename).suffix)
            temp_files.append(temp_file.name)
            
            # Write uploaded content to temp file
            content = await upload_file.read()
            temp_file.write(content)
            temp_file.close()
            
            # Create file info for analysis
            file_info = {
                'file_path': temp_file.name,
                'file_id': str(uuid.uuid4()),
                'filename': upload_file.filename,
                'content_type': upload_file.content_type,
                'size': len(content)
            }
            file_infos.append(file_info)
        
        # Analyze files
        analyses = merger.analyze_files(file_infos)
        
        if len(analyses) < 2:
            raise HTTPException(status_code=400, detail="Could not analyze at least 2 files")
        
        # Suggest merge strategies
        suggestions = merger.suggest_merge_strategies(analyses)
        
        # Prepare response
        response = {
            "files_analyzed": len(analyses),
            "file_analyses": [
                {
                    "file_id": analysis.file_id,
                    "filename": analysis.filename,
                    "file_type": analysis.file_type,
                    "columns": analysis.columns,
                    "row_count": analysis.row_count,
                    "quality_score": analysis.quality_score,
                    "sample_data": analysis.sample_data
                }
                for analysis in analyses
            ],
            "merge_suggestions": [
                {
                    "strategy": suggestion.strategy.value,
                    "confidence": suggestion.confidence,
                    "description": suggestion.description,
                    "join_keys": suggestion.join_keys,
                    "expected_rows": suggestion.expected_rows,
                    "warnings": suggestion.warnings,
                    "data_quality_score": suggestion.data_quality_score
                }
                for suggestion in suggestions
            ]
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing files: {str(e)}")
    
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

@router.post("/execute-merge")
async def execute_merge(
    files: List[UploadFile] = File(...),
    strategy_type: str = Form(...),
    join_keys: List[str] = Form(None),
    workflow_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Execute a merge based on the specified strategy
    """
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files are required for merging")
    
    if not strategy_type:
        raise HTTPException(status_code=400, detail="Strategy type is required")
    
    # Save uploaded files temporarily
    temp_files = []
    file_infos = []
    
    try:
        for upload_file in files:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(upload_file.filename).suffix)
            temp_files.append(temp_file.name)
            
            # Write uploaded content to temp file
            content = await upload_file.read()
            temp_file.write(content)
            temp_file.close()
            
            # Create file info for merge
            file_info = {
                'file_path': temp_file.name,
                'file_id': str(uuid.uuid4()),
                'filename': upload_file.filename,
                'content_type': upload_file.content_type,
                'size': len(content)
            }
            file_infos.append(file_info)
        
        # Create merge suggestion based on strategy type
        if strategy_type == "inner_join":
            if not join_keys or len(join_keys) == 0:
                raise HTTPException(status_code=400, detail="Join keys are required for join strategy")
            
            suggestion = MergeSuggestion(
                strategy=MergeStrategy.INNER_JOIN,
                confidence=0.8,
                description=f"Merge files using {join_keys[0]} as join key",
                join_keys=join_keys,
                expected_rows=0,  # Will be calculated during execution
                warnings=[],
                data_quality_score=0.8
            )
        elif strategy_type == "concatenate":
            suggestion = MergeSuggestion(
                strategy=MergeStrategy.CONCATENATE,
                confidence=0.9,
                description="Concatenate files with similar structure",
                join_keys=[],
                expected_rows=0,  # Will be calculated during execution
                warnings=[],
                data_quality_score=0.8
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported strategy type: {strategy_type}")
        
        # Execute the merge
        result = merger.execute_merge(file_infos, suggestion)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Merge failed: {result.get('error', 'Unknown error')}")
        
        # Prepare response
        response = {
            "success": True,
            "strategy_used": strategy_type,
            "result": {
                "row_count": result["row_count"],
                "column_count": result["column_count"],
                "sample_data": result["merged_data"][:5] if result["merged_data"] else [],
                "total_records": len(result["merged_data"]) if result["merged_data"] else 0
            }
        }
        
        if "join_key" in result:
            response["result"]["join_key"] = result["join_key"]
        
        if "concatenated_files" in result:
            response["result"]["concatenated_files"] = result["concatenated_files"]
        
        return JSONResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing merge: {str(e)}")
    
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

@router.post("/analyze-and-suggest")
async def analyze_and_suggest_merge(
    files: List[UploadFile] = File(...),
    workflow_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze files and return detailed merge suggestions with explanations
    """
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files are required for merging")
    
    # Save uploaded files temporarily
    temp_files = []
    file_infos = []
    
    try:
        for upload_file in files:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(upload_file.filename).suffix)
            temp_files.append(temp_file.name)
            
            # Write uploaded content to temp file
            content = await upload_file.read()
            temp_file.write(content)
            temp_file.close()
            
            # Create file info for analysis
            file_info = {
                'file_path': temp_file.name,
                'file_id': str(uuid.uuid4()),
                'filename': upload_file.filename,
                'content_type': upload_file.content_type,
                'size': len(content)
            }
            file_infos.append(file_info)
        
        # Analyze files
        analyses = merger.analyze_files(file_infos)
        
        if len(analyses) < 2:
            raise HTTPException(status_code=400, detail="Could not analyze at least 2 files")
        
        # Suggest merge strategies
        suggestions = merger.suggest_merge_strategies(analyses)
        
        # Check if any merge is possible
        merge_possible = any(s.strategy != MergeStrategy.NO_MERGE for s in suggestions)
        
        # Prepare detailed response
        response = {
            "files_analyzed": len(analyses),
            "merge_possible": merge_possible,
            "file_summaries": [
                {
                    "filename": analysis.filename,
                    "file_type": analysis.file_type,
                    "columns": analysis.columns,
                    "row_count": analysis.row_count,
                    "quality_score": analysis.quality_score
                }
                for analysis in analyses
            ],
            "merge_suggestions": []
        }
        
        for suggestion in suggestions:
            if suggestion.strategy == MergeStrategy.NO_MERGE:
                response["merge_suggestions"].append({
                    "type": "no_merge",
                    "message": "Inconsistent data - files cannot be merged",
                    "reasons": suggestion.warnings,
                    "confidence": suggestion.confidence
                })
            else:
                suggestion_data = {
                    "type": "merge_possible",
                    "strategy": suggestion.strategy.value,
                    "confidence": suggestion.confidence,
                    "description": suggestion.description,
                    "expected_rows": suggestion.expected_rows,
                    "warnings": suggestion.warnings,
                    "data_quality_score": suggestion.data_quality_score
                }
                
                if suggestion.join_keys:
                    suggestion_data["join_keys"] = suggestion.join_keys
                
                response["merge_suggestions"].append(suggestion_data)
        
        return JSONResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing files: {str(e)}")
    
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass 