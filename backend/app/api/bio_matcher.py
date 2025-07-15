from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import pandas as pd
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import BytesIO
from ..database import get_db
from services.workflow_state import workflow_state_manager

router = APIRouter(prefix="/bio", tags=["bio-matcher"])

@router.post("/create-workflow-session")
async def create_workflow_session():
    """Create a new workflow session for multi-step data processing"""
    session_id = workflow_state_manager.create_session()
    return {
        "session_id": session_id,
        "message": "Workflow session created successfully"
    }

@router.post("/merge-files")
async def merge_files(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Merge two CSV files based on matching ID columns.
    Stores the merged data in workflow session for subsequent steps.
    """
    try:
        # Read first CSV file
        content1 = await file1.read()
        df1 = pd.read_csv(io.StringIO(content1.decode('utf-8')))
        
        # Read second CSV file
        content2 = await file2.read()
        df2 = pd.read_csv(io.StringIO(content2.decode('utf-8')))
        
        # Check if both files have ID columns
        if 'ID' not in df1.columns or 'ID' not in df2.columns:
            raise HTTPException(
                status_code=400, 
                detail="Both files must contain an 'ID' column"
            )
        
        # Merge dataframes on ID column
        merged_df = pd.merge(df1, df2, on='ID', how='outer')
        
        # Calculate statistics
        total_rows = len(merged_df)
        matched_rows = len(merged_df.dropna(subset=['ID']))
        unmatched_rows = total_rows - matched_rows
        
        # Convert to list format for response
        headers = merged_df.columns.tolist()
        rows = merged_df.values.tolist()
        
        # Convert numpy types to Python types for JSON serialization
        processed_rows = []
        for row in rows:
            processed_row = []
            for cell in row:
                if pd.isna(cell):
                    processed_row.append(None)
                elif isinstance(cell, (int, float)):
                    processed_row.append(float(cell) if isinstance(cell, float) else int(cell))
                else:
                    processed_row.append(str(cell))
            processed_rows.append(processed_row)
        
        merged_data = {
            "headers": headers,
            "rows": processed_rows,
            "totalRows": total_rows,
            "matchedRows": matched_rows,
            "unmatchedRows": unmatched_rows,
            "dataframe_info": {
                "shape": merged_df.shape,
                "columns": merged_df.columns.tolist(),
                "numeric_columns": merged_df.select_dtypes(include=[np.number]).columns.tolist()
            }
        }
        
        # Store in workflow session if session_id provided
        if session_id:
            workflow_state_manager.store_merged_data(session_id, merged_data)
            workflow_state_manager.add_workflow_step(session_id, "merge_files", {
                "file1_name": file1.filename,
                "file2_name": file2.filename,
                "total_rows": total_rows,
                "matched_rows": matched_rows,
                "unmatched_rows": unmatched_rows
            })
        
        return {
            **merged_data,
            "session_id": session_id,
            "workflow_step": "merge_files"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing files: {str(e)}"
        )

@router.post("/generate-visualization")
async def generate_visualization(
    file: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form(None),
    plot_type: str = Form("scatter"),
    x_column: Optional[str] = Form(None),
    y_column: Optional[str] = Form(None),
    use_session_data: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Generate visualizations from CSV data.
    Can use uploaded file or data from workflow session.
    """
    try:
        df = None
        
        # Try to get data from session first if requested
        if use_session_data and session_id:
            merged_data = workflow_state_manager.get_merged_data(session_id)
            if merged_data:
                # Convert stored data back to DataFrame
                df = pd.DataFrame(merged_data['rows'], columns=merged_data['headers'])
                print(f"Using session data with shape: {df.shape}")
            else:
                raise HTTPException(
                    status_code=400,
                    detail="No merged data found in session. Please merge files first."
                )
        elif file:
            # Use uploaded file
            content = await file.read()
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            print(f"Using uploaded file with shape: {df.shape}")
        else:
            raise HTTPException(
                status_code=400,
                detail="Either provide a file or use session data with use_session_data=true"
            )
        
        # Set up matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate different types of plots
        if plot_type == "scatter":
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                ax.scatter(df[x_column], df[y_column], alpha=0.6)
                ax.set_xlabel(str(x_column))
                ax.set_ylabel(str(y_column))
                ax.set_title(f'Scatter Plot: {x_column} vs {y_column}')
            else:
                # Default scatter plot for biological data
                if 'Activity_Score' in df.columns and 'Stability_Index' in df.columns:
                    ax.scatter(df['Activity_Score'], df['Stability_Index'], alpha=0.6)
                    ax.set_xlabel('Activity Score')
                    ax.set_ylabel('Stability Index')
                    ax.set_title('Activity Score vs Stability Index')
                else:
                    # Use first two numeric columns
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) >= 2:
                        ax.scatter(df[numeric_cols[0]], df[numeric_cols[1]], alpha=0.6)
                        ax.set_xlabel(str(numeric_cols[0]))
                        ax.set_ylabel(str(numeric_cols[1]))
                        ax.set_title(f'Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}')
        
        elif plot_type == "histogram":
            if x_column and x_column in df.columns:
                ax.hist(df[x_column].dropna(), bins=20, alpha=0.7, edgecolor='black')
                ax.set_xlabel(str(x_column))
                ax.set_ylabel('Frequency')
                ax.set_title(f'Histogram of {x_column}')
            else:
                # Default histogram for biological data
                if 'Activity_Score' in df.columns:
                    ax.hist(df['Activity_Score'].dropna(), bins=20, alpha=0.7, edgecolor='black')
                    ax.set_xlabel('Activity Score')
                    ax.set_ylabel('Frequency')
                    ax.set_title('Distribution of Activity Scores')
                else:
                    # Use first numeric column
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        ax.hist(df[numeric_cols[0]].dropna(), bins=20, alpha=0.7, edgecolor='black')
                        ax.set_xlabel(str(numeric_cols[0]))
                        ax.set_ylabel('Frequency')
                        ax.set_title(f'Histogram of {numeric_cols[0]}')
        
        elif plot_type == "correlation":
            # Create correlation heatmap
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) > 1:
                correlation_matrix = numeric_df.corr()
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
                ax.set_title('Correlation Heatmap')
            else:
                ax.text(0.5, 0.5, 'Not enough numeric columns for correlation', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Correlation Heatmap')
        
        elif plot_type == "boxplot":
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                df.boxplot(column=y_column, by=x_column, ax=ax)
                ax.set_xlabel(str(x_column))
                ax.set_ylabel(str(y_column))
                ax.set_title(f'Box Plot: {y_column} by {x_column}')
            else:
                # Default box plot for biological data
                if 'Activity_Score' in df.columns and 'Mutation' in df.columns:
                    df.boxplot(column='Activity_Score', by='Mutation', ax=ax)
                    ax.set_xlabel('Mutation')
                    ax.set_ylabel('Activity Score')
                    ax.set_title('Activity Score Distribution by Mutation')
                else:
                    # Use first numeric column
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        ax.text(0.5, 0.5, 'Select columns for box plot', 
                               ha='center', va='center', transform=ax.transAxes)
                        ax.set_title('Box Plot')
        
        else:
            # Default to scatter plot
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                ax.scatter(df[numeric_cols[0]], df[numeric_cols[1]], alpha=0.6)
                ax.set_xlabel(str(numeric_cols[0]))
                ax.set_ylabel(str(numeric_cols[1]))
                ax.set_title(f'Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}')
        
        # Save plot to base64 string
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plot_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        # Get column information
        columns = df.columns.tolist()
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        viz_data = {
            "plot_type": plot_type,
            "plot_data": plot_data,
            "columns": columns,
            "data_shape": list(df.shape),
            "numeric_columns": numeric_columns,
            "session_id": session_id,
            "workflow_step": "visualization"
        }
        
        # Store visualization data in session if session_id provided
        if session_id:
            workflow_state_manager.store_visualization_data(session_id, viz_data)
            workflow_state_manager.add_workflow_step(session_id, "generate_visualization", {
                "plot_type": plot_type,
                "x_column": x_column,
                "y_column": y_column,
                "data_shape": list(df.shape),
                "columns": columns
            })
        
        return viz_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating visualization: {str(e)}"
        )

@router.get("/workflow-status/{session_id}")
async def get_workflow_status(session_id: str):
    """Get the current status and history of a workflow session"""
    session = workflow_state_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return {
        "session_id": session_id,
        "created_at": session['created_at'].isoformat(),
        "last_updated": session['last_updated'].isoformat(),
        "steps": session['steps'],
        "has_merged_data": 'merged_data' in session['data'],
        "has_visualization_data": 'visualization_data' in session['data']
    }

@router.get("/workflow-history/{session_id}")
async def get_workflow_history(session_id: str):
    """Get the complete workflow history for a session"""
    history = workflow_state_manager.get_workflow_history(session_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return {
        "session_id": session_id,
        "history": history
    }

@router.post("/upload-test-results")
async def upload_test_results(
    file: UploadFile = File(...),
    test_type: str = Form("activity"),
    assay_name: str = Form(None),
    protocol: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload test results CSV file and process it.
    """
    try:
        # Read the uploaded file
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Basic validation
        if len(df) == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Process the data (you can add more processing logic here)
        processed_rows = len(df)
        
        return {
            "message": "Test results uploaded successfully",
            "processed_rows": processed_rows,
            "test_type": test_type,
            "assay_name": assay_name,
            "protocol": protocol
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing test results: {str(e)}"
        )

@router.get("/designs")
async def get_designs(db: Session = Depends(get_db)):
    """
    Get all biological designs.
    """
    # This would typically query the database
    # For now, return empty list
    return []

@router.get("/builds")
async def get_builds(db: Session = Depends(get_db)):
    """
    Get all biological builds.
    """
    # This would typically query the database
    # For now, return empty list
    return []

@router.get("/tests")
async def get_tests(db: Session = Depends(get_db)):
    """
    Get all biological tests.
    """
    # This would typically query the database
    # For now, return empty list
    return [] 