from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from ..database import get_db
from ..services.data_qa_service import DataQAService
from pydantic import BaseModel

router = APIRouter()

class DataQuestionRequest(BaseModel):
    session_id: str
    question: str

class DataQuestionResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    insights: Optional[list] = None
    confidence: Optional[str] = None
    suggestions: Optional[list] = None
    data_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class DataPreviewResponse(BaseModel):
    success: bool
    preview: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/ask", response_model=DataQuestionResponse)
async def ask_data_question(
    request: DataQuestionRequest,
    db: Session = Depends(get_db)
):
    """Ask a question about the data in a session"""
    try:
        qa_service = DataQAService(db)
        result = qa_service.analyze_data_context(request.session_id, request.question)
        
        return DataQuestionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

@router.get("/preview/{session_id}", response_model=DataPreviewResponse)
async def get_data_preview(
    session_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get a preview of the data in a session"""
    try:
        qa_service = DataQAService(db)
        result = qa_service.get_data_preview(session_id, limit)
        
        return DataPreviewResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data preview: {str(e)}")

@router.get("/suggestions/{session_id}")
async def get_question_suggestions(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get suggested questions based on the data in the session"""
    try:
        qa_service = DataQAService(db)
        preview = qa_service.get_data_preview(session_id, 5)
        
        if not preview.get("success"):
            return {"suggestions": []}
        
        suggestions = []
        preview_data = preview.get("preview", {})
        
        # Generate suggestions based on data characteristics
        for file_name, file_data in preview_data.items():
            if "error" in file_data:
                continue
                
            columns = file_data.get("columns", [])
            rows = file_data.get("rows", 0)
            
            # Basic suggestions
            suggestions.append(f"How many rows are in {file_name}?")
            suggestions.append(f"What columns are available in {file_name}?")
            
            # Numeric column suggestions
            numeric_cols = [col for col in columns if any(keyword in col.lower() for keyword in ['price', 'amount', 'count', 'number', 'value'])]
            if numeric_cols:
                suggestions.append(f"What are the statistics for {numeric_cols[0]} in {file_name}?")
            
            # Categorical column suggestions
            categorical_cols = [col for col in columns if any(keyword in col.lower() for keyword in ['category', 'type', 'status', 'name', 'id'])]
            if categorical_cols:
                suggestions.append(f"What are the unique values in {categorical_cols[0]}?")
            
            # Missing data suggestions
            if rows > 0:
                suggestions.append(f"Are there any missing values in {file_name}?")
        
        # Add general suggestions that the system can actually answer
        suggestions.extend([
            "What are the data types of the columns?",
            "How many files do I have?",
            "What are the file names?",
            "Are there any missing values?",
            "What numeric columns are available?",
            "Show me a summary of the data"
        ])
        
        return {"suggestions": suggestions[:10]}  # Limit to 10 suggestions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.get("/health")
async def qa_health_check():
    """Health check for the QA service"""
    return {
        "status": "healthy",
        "service": "data_qa",
        "llm_available": True  # This would check if OpenAI API key is available
    } 