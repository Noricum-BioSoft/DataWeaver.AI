from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import io
import base64
import json
import csv
from ..services.intelligent_merger import IntelligentMerger
from ..services.data_context import DataContextManager, data_context_manager
from ..services.data_analyzer import DataAnalyzer
from ..services.simple_visualizer import simple_visualizer
from ..database import get_db
from services.workflow_state import workflow_state_manager

# Try to import pandas and numpy, but provide fallbacks if not available
try:
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px
    import plotly.utils
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas/numpy not available. Using fallback CSV processing.")

router = APIRouter(prefix="/bio", tags=["bio-matcher"])

@router.post("/create-workflow-session")
async def create_workflow_session():
    """Create a new workflow session for multi-step data processing"""
    session_id = workflow_state_manager.create_session()
    return {
        "session_id": session_id,
        "message": "Workflow session created successfully"
    }

@router.delete("/clear-session/{session_id}")
async def clear_workflow_session(session_id: str):
    """Clear all data from a workflow session"""
    try:
        # Clear session data
        workflow_state_manager.clear_session(session_id)
        
        # Clear data context
        data_context_manager.clear_session_data(session_id)
        
        return {
            "session_id": session_id,
            "message": "Session data cleared successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing session: {str(e)}"
        )

@router.post("/upload-single-file")
async def upload_single_file(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a single CSV file and store it in the workflow session.
    This is used for single file uploads that don't need merging.
    """
    if not PANDAS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="File processing service is temporarily unavailable. Please try again later or contact support."
        )
    
    try:
        if not file.filename or not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Please upload a valid CSV file"
            )
        
        # Read the CSV file
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Track uploaded file in context
        uploaded_file_id = None
        if session_id:
            file_id = f"file_0_{file.filename}"
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            uploaded_file_id = data_context_manager.add_uploaded_file(
                session_id=session_id,
                file_id=file_id,
                filename=file.filename,
                file_size=len(content),
                columns=df.columns.tolist(),
                row_count=len(df),
                numeric_columns=numeric_columns
            )
        
        # Convert to list format for response
        headers = df.columns.tolist()
        rows = df.values.tolist()
        
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
        
        file_data = {
            "headers": headers,
            "rows": processed_rows,
            "totalRows": len(df),
            "matchedRows": len(df),
            "unmatchedRows": 0,
            "filename": file.filename,
            "dataframe_info": {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist()
            }
        }
        
        # Store in workflow session if session_id provided
        if session_id:
            # Store individual file data
            workflow_state_manager.store_uploaded_file(session_id, file_data)
            workflow_state_manager.add_workflow_step(session_id, "upload_single_file", {
                "file_name": file.filename,
                "total_rows": len(df),
                "columns": df.columns.tolist()
            })
            
            # Track uploaded file in context
            if uploaded_file_id:
                data_context_manager.add_merged_dataset(
                    session_id=session_id,
                    merged_data=file_data,
                    parent_file_ids=[uploaded_file_id]
                )
        
        return {
            **file_data,
            "session_id": session_id,
            "workflow_step": "upload_single_file",
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@router.post("/merge-files")
async def merge_files(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Merge multiple CSV files based on matching ID columns.
    Stores the merged data in workflow session for subsequent steps.
    """
    if not PANDAS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="File merging service is temporarily unavailable. Please try again later or contact support."
        )
    
    try:
        if len(files) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 files are required for merging"
            )
        
        # Read all CSV files and track them in context
        dataframes = []
        uploaded_file_ids = []
        
        for i, file in enumerate(files):
            content = await file.read()
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            dataframes.append(df)
            
            # Track uploaded file in context
            if session_id:
                file_id = f"file_{i}_{file.filename}"
                numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                uploaded_file_id = data_context_manager.add_uploaded_file(
                    session_id=session_id,
                    file_id=file_id,
                    filename=file.filename or f"file_{i}",
                    file_size=len(content),
                    columns=df.columns.tolist(),
                    row_count=len(df),
                    numeric_columns=numeric_columns
                )
                uploaded_file_ids.append(uploaded_file_id)
        
        # Find common columns across all files
        all_columns = [set(df.columns) for df in dataframes]
        common_columns = set.intersection(*all_columns)
        
        # Look for ID-like columns (case insensitive)
        id_columns = []
        for col in common_columns:
            col_lower = col.lower()
            if any(id_pattern in col_lower for id_pattern in ['id', 'key', 'identifier', 'name']):
                id_columns.append(col)
        
        if not id_columns:
            # If no obvious ID columns, use the first common column
            if common_columns:
                merge_column = list(common_columns)[0]
                id_columns = [merge_column]
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="No common columns found for merging. Files must have at least one column in common."
                )
        
        # Use the first (or best) ID column for merging
        merge_column = id_columns[0]
        
        # Merge all dataframes on the identified column
        merged_df = dataframes[0]
        for df in dataframes[1:]:
            merged_df = pd.merge(merged_df, df, on=merge_column, how='outer')
        
        # Calculate statistics
        total_rows = len(merged_df)
        matched_rows = len(merged_df.dropna(subset=[merge_column]))
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
                "files_count": len(files),
                "file_names": [f.filename for f in files],
                "total_rows": total_rows,
                "matched_rows": matched_rows,
                "unmatched_rows": unmatched_rows
            })
            
            # Track merged dataset in context
            merged_data_id = data_context_manager.add_merged_dataset(
                session_id=session_id,
                merged_data=merged_data,
                parent_file_ids=uploaded_file_ids
            )
        
        return {
            **merged_data,
            "session_id": session_id,
            "workflow_step": "merge_files",
            "merge_column": merge_column,
            "common_columns": list(common_columns)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing files: {str(e)}"
        )

@router.post("/merge-session-files")
async def merge_session_files(
    session_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Merge files that are already uploaded to a session.
    This allows users to upload files individually and then merge them.
    """
    if not PANDAS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="File merging service is temporarily unavailable. Please try again later or contact support."
        )
    
    try:
        # Get session data to see what files are available
        session_data = workflow_state_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )
        
        # Get all uploaded files from session
        uploaded_files = workflow_state_manager.get_uploaded_files(session_id)
        if len(uploaded_files) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 files are required for merging. Please upload more files first."
            )
        
        # Convert stored file data back to pandas DataFrames
        dataframes = []
        for file_data in uploaded_files:
            # Convert rows back to DataFrame
            df = pd.DataFrame(file_data['rows'], columns=file_data['headers'])
            dataframes.append(df)
        
        # Find common columns across all files
        all_columns = [set(df.columns) for df in dataframes]
        common_columns = set.intersection(*all_columns)
        
        # Look for ID-like columns (case insensitive)
        id_columns = []
        for col in common_columns:
            col_lower = col.lower()
            if any(id_pattern in col_lower for id_pattern in ['id', 'key', 'identifier', 'name']):
                id_columns.append(col)
        
        if not id_columns:
            # If no obvious ID columns, use the first common column
            if common_columns:
                merge_column = list(common_columns)[0]
                id_columns = [merge_column]
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="No common columns found for merging. Files must have at least one column in common."
                )
        
        # Use the first (or best) ID column for merging
        merge_column = id_columns[0]
        
        # Merge all dataframes on the identified column
        merged_df = dataframes[0]
        for df in dataframes[1:]:
            merged_df = pd.merge(merged_df, df, on=merge_column, how='outer')
        
        # Calculate statistics
        total_rows = len(merged_df)
        matched_rows = len(merged_df.dropna(subset=[merge_column]))
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
        
        # Store the merged result
        workflow_state_manager.store_merged_data(session_id, merged_data)
        workflow_state_manager.add_workflow_step(session_id, "merge_session_files", {
            "files_count": len(uploaded_files),
            "file_names": [f.get('filename', 'unknown') for f in uploaded_files],
            "total_rows": total_rows,
            "matched_rows": matched_rows,
            "unmatched_rows": unmatched_rows
        })
        
        return {
            **merged_data,
            "session_id": session_id,
            "workflow_step": "merge_session_files",
            "merge_column": merge_column,
            "common_columns": list(common_columns),
            "message": "Successfully merged session files"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error merging session files: {str(e)}"
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
    if not PANDAS_AVAILABLE:
        # Use simple visualizer instead of raising error
        try:
            if file:
                content = await file.read()
                data = simple_visualizer.parse_csv(content)
            elif use_session_data and session_id:
                merged_data = workflow_state_manager.get_merged_data(session_id)
                if merged_data:
                    data = {
                        'headers': merged_data['headers'],
                        'rows': merged_data['rows'],
                        'total_rows': len(merged_data['rows']),
                        'total_columns': len(merged_data['headers'])
                    }
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="No merged data found in session. Please merge files first."
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Either provide a file or use session data with use_session_data=true"
                )
            
            # Create simple visualization
            viz_data = simple_visualizer.create_simple_plot(data, plot_type)
            
            # Store visualization data in session if session_id provided
            if session_id:
                workflow_state_manager.store_visualization_data(session_id, viz_data)
                workflow_state_manager.add_workflow_step(session_id, "generate_visualization", {
                    "plot_type": plot_type,
                    "data_shape": data['data_shape'],
                    "columns": data['headers']
                })
            
            return viz_data
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating simple visualization: {str(e)}"
            )
    
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
        
        # Generate different types of plots using Plotly
        if plot_type == "scatter":
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                fig = px.scatter(df, x=x_column, y=y_column, 
                               title=f'Scatter Plot: {x_column} vs {y_column}',
                               opacity=0.6)
            else:
                # Default scatter plot for biological data
                if 'Activity_Score' in df.columns and 'Stability_Index' in df.columns:
                    fig = px.scatter(df, x='Activity_Score', y='Stability_Index',
                                   title='Activity Score vs Stability Index',
                                   opacity=0.6)
                else:
                    # Use first two numeric columns
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) >= 2:
                        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                                       title=f'Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}',
                                       opacity=0.6)
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail="Not enough numeric columns for scatter plot"
                        )
        
        elif plot_type == "histogram":
            if x_column and x_column in df.columns:
                fig = px.histogram(df, x=x_column, 
                                 title=f'Histogram of {x_column}',
                                 nbins=20)
            else:
                # Default histogram for biological data
                if 'Activity_Score' in df.columns:
                    fig = px.histogram(df, x='Activity_Score',
                                     title='Distribution of Activity Scores',
                                     nbins=20)
                else:
                    # Use first numeric column
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        fig = px.histogram(df, x=numeric_cols[0],
                                         title=f'Histogram of {numeric_cols[0]}',
                                         nbins=20)
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail="No numeric columns found for histogram"
                        )
        
        elif plot_type == "correlation":
            # Create correlation heatmap
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) >= 2:
                correlation_matrix = numeric_df.corr()
                fig = go.Figure(data=go.Heatmap(
                    z=correlation_matrix.values,
                    x=correlation_matrix.columns,
                    y=correlation_matrix.columns,
                    colorscale='RdBu',
                    zmid=0,
                    text=correlation_matrix.round(2).values,
                    texttemplate="%{text}",
                    textfont={"size": 10},
                    hoverongaps=False
                ))
                fig.update_layout(
                    title='Correlation Heatmap',
                    xaxis_title='Variables',
                    yaxis_title='Variables',
                    width=800,
                    height=600
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough numeric columns for correlation (found {len(numeric_df.columns)}, need at least 2)"
                )
        
        elif plot_type == "boxplot":
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                fig = px.box(df, x=x_column, y=y_column,
                           title=f'Box Plot: {y_column} by {x_column}')
            else:
                # Default box plot for biological data
                if 'Activity_Score' in df.columns and 'Mutation' in df.columns:
                    fig = px.box(df, x='Mutation', y='Activity_Score',
                               title='Activity Score Distribution by Mutation')
                else:
                    # Use first numeric column
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        fig = px.box(df, y=numeric_cols[0],
                                   title=f'Box Plot of {numeric_cols[0]}')
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail="No numeric columns found for box plot"
                        )
        
        else:
            # Default to scatter plot
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                               title=f'Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}',
                               opacity=0.6)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Not enough numeric columns for scatter plot"
                )
        
        # Convert Plotly figure to JSON
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Get column information
        columns = df.columns.tolist()
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        viz_data = {
            "plot_type": plot_type,
            "plot_json": plot_json,
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
            
            # Track visualization in context
            # Find the parent data (merged dataset or uploaded file)
            parent_data_id = None
            if use_session_data:
                # Use the merged dataset as parent
                contexts = data_context_manager.get_session_context(session_id)
                for data_id, context in contexts.items():
                    if context.data_type.value == "merged_dataset":
                        parent_data_id = data_id
                        break
            
            if parent_data_id:
                viz_data_id = data_context_manager.add_visualization(
                    session_id=session_id,
                    viz_data=viz_data,
                    parent_data_id=parent_data_id
                )
        
        return viz_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating visualization: {str(e)}"
        )

@router.post("/explain-visualization")
async def explain_visualization(
    session_id: str = Form(...),
    plot_type: str = Form("scatter"),
    x_column: Optional[str] = Form(None),
    y_column: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Analyze and explain the trends and patterns in the visualized data
    """
    if not PANDAS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Visualization explanation service is temporarily unavailable. Please try again later or contact support."
        )
    
    try:
        # Get the data from session
        merged_data = workflow_state_manager.get_merged_data(session_id)
        if not merged_data:
            raise HTTPException(
                status_code=400,
                detail="No data found in session. Please upload or merge data first."
            )
        
        # Convert stored data back to DataFrame
        df = pd.DataFrame(merged_data['rows'], columns=merged_data['headers'])
        
        # Perform statistical analysis based on plot type
        analysis = {}
        
        if plot_type == "scatter":
            analysis = analyze_scatter_plot(df, x_column, y_column)
        elif plot_type == "correlation":
            analysis = analyze_correlation_matrix(df)
        elif plot_type == "histogram":
            analysis = analyze_histogram(df, x_column)
        elif plot_type == "boxplot":
            analysis = analyze_boxplot(df, x_column, y_column)
        else:
            analysis = analyze_general_trends(df)
        
        return {
            "plot_type": plot_type,
            "data_shape": list(df.shape),
            "analysis": analysis,
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error explaining visualization: {str(e)}"
        )

def analyze_scatter_plot(df, x_column, y_column):
    """Analyze scatter plot trends and patterns"""
    analysis = {
        "trends": [],
        "correlations": [],
        "outliers": [],
        "insights": []
    }
    
    # Auto-detect columns if not specified
    if not x_column or not y_column:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            x_column = numeric_cols[0]
            y_column = numeric_cols[1]
        else:
            return {"error": "Not enough numeric columns for scatter analysis"}
    
    if x_column not in df.columns or y_column not in df.columns:
        return {"error": f"Columns {x_column} and {y_column} not found in data"}
    
    # Calculate correlation
    correlation = df[x_column].corr(df[y_column])
    analysis["correlations"].append({
        "columns": [x_column, y_column],
        "correlation": correlation,
        "strength": "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.3 else "weak"
    })
    
    # Detect trends
    if correlation > 0.5:
        analysis["trends"].append(f"Strong positive relationship between {x_column} and {y_column}")
    elif correlation < -0.5:
        analysis["trends"].append(f"Strong negative relationship between {x_column} and {y_column}")
    elif abs(correlation) < 0.2:
        analysis["trends"].append(f"Little to no linear relationship between {x_column} and {y_column}")
    else:
        analysis["trends"].append(f"Moderate relationship between {x_column} and {y_column}")
    
    # Detect outliers using IQR method
    Q1_x, Q3_x = df[x_column].quantile([0.25, 0.75])
    Q1_y, Q3_y = df[y_column].quantile([0.25, 0.75])
    IQR_x = Q3_x - Q1_x
    IQR_y = Q3_y - Q1_y
    
    outliers_x = df[(df[x_column] < Q1_x - 1.5 * IQR_x) | (df[x_column] > Q3_x + 1.5 * IQR_x)]
    outliers_y = df[(df[y_column] < Q1_y - 1.5 * IQR_y) | (df[y_column] > Q3_y + 1.5 * IQR_y)]
    
    if len(outliers_x) > 0:
        analysis["outliers"].append(f"{len(outliers_x)} outliers detected in {x_column}")
    if len(outliers_y) > 0:
        analysis["outliers"].append(f"{len(outliers_y)} outliers detected in {y_column}")
    
    # Generate insights
    x_mean, y_mean = df[x_column].mean(), df[y_column].mean()
    x_std, y_std = df[x_column].std(), df[y_column].std()
    
    analysis["insights"].extend([
        f"Mean {x_column}: {x_mean:.2f} (std: {x_std:.2f})",
        f"Mean {y_column}: {y_mean:.2f} (std: {y_std:.2f})",
        f"Data range: {df[x_column].min():.2f} to {df[x_column].max():.2f} for {x_column}",
        f"Data range: {df[y_column].min():.2f} to {df[y_column].max():.2f} for {y_column}"
    ])
    
    return analysis

def analyze_correlation_matrix(df):
    """Analyze correlation matrix patterns"""
    analysis = {
        "strong_correlations": [],
        "moderate_correlations": [],
        "weak_correlations": [],
        "insights": []
    }
    
    numeric_df = df.select_dtypes(include=[np.number])
    if len(numeric_df.columns) < 2:
        return {"error": "Not enough numeric columns for correlation analysis"}
    
    correlation_matrix = numeric_df.corr()
    
    # Find strong correlations (|r| > 0.7)
    strong_pairs = []
    moderate_pairs = []
    weak_pairs = []
    
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            col1 = correlation_matrix.columns[i]
            col2 = correlation_matrix.columns[j]
            corr = correlation_matrix.iloc[i, j]
            
            if abs(corr) > 0.7:
                strong_pairs.append((col1, col2, corr))
            elif abs(corr) > 0.3:
                moderate_pairs.append((col1, col2, corr))
            else:
                weak_pairs.append((col1, col2, corr))
    
    analysis["strong_correlations"] = [f"{col1} ↔ {col2} (r={corr:.3f})" for col1, col2, corr in strong_pairs[:5]]
    analysis["moderate_correlations"] = [f"{col1} ↔ {col2} (r={corr:.3f})" for col1, col2, corr in moderate_pairs[:5]]
    
    analysis["insights"].extend([
        f"Found {len(strong_pairs)} strong correlations (|r| > 0.7)",
        f"Found {len(moderate_pairs)} moderate correlations (0.3 < |r| < 0.7)",
        f"Found {len(weak_pairs)} weak correlations (|r| < 0.3)"
    ])
    
    return analysis

def analyze_histogram(df, x_column):
    """Analyze histogram distribution patterns"""
    try:
        analysis = {
            "distribution": "",
            "central_tendency": {},
            "spread": {},
            "outliers": [],
            "insights": []
        }
        
        if not x_column:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                x_column = numeric_cols[0]
            else:
                return {"error": "No numeric columns found for histogram analysis"}
        
        if x_column not in df.columns:
            return {"error": f"Column {x_column} not found in data"}
        
        # Basic statistics
        mean_val = float(df[x_column].mean())
        median_val = float(df[x_column].median())
        std_val = float(df[x_column].std())
        min_val = float(df[x_column].min())
        max_val = float(df[x_column].max())
        
        analysis["central_tendency"] = {
            "mean": mean_val,
            "median": median_val,
            "mode": None  # Skip mode for now
        }
        
        analysis["spread"] = {
            "std": std_val,
            "range": max_val - min_val,
            "iqr": float(df[x_column].quantile(0.75) - df[x_column].quantile(0.25))
        }
        
        # Simple distribution analysis
        if mean_val > median_val:
            analysis["distribution"] = "right-skewed"
        elif mean_val < median_val:
            analysis["distribution"] = "left-skewed"
        else:
            analysis["distribution"] = "approximately symmetric"
        
        # Detect outliers using IQR method
        Q1 = float(df[x_column].quantile(0.25))
        Q3 = float(df[x_column].quantile(0.75))
        IQR = Q3 - Q1
        outliers = df[(df[x_column] < Q1 - 1.5 * IQR) | (df[x_column] > Q3 + 1.5 * IQR)]
        
        if len(outliers) > 0:
            analysis["outliers"].append(f"{len(outliers)} outliers detected ({len(outliers)/len(df)*100:.1f}% of data)")
        
        analysis["insights"].extend([
            f"Distribution is {analysis['distribution']}",
            f"Mean: {mean_val:.2f}, Median: {median_val:.2f}",
            f"Standard deviation: {std_val:.2f}",
            f"Data spans from {min_val:.2f} to {max_val:.2f}"
        ])
        
        return analysis
    except Exception as e:
        return {"error": f"Error analyzing histogram: {str(e)}"}

def analyze_boxplot(df, x_column, y_column):
    """Analyze boxplot patterns and group differences"""
    analysis = {
        "group_comparisons": [],
        "outliers": [],
        "insights": []
    }
    
    if not x_column or not y_column:
        return {"error": "Both x_column and y_column required for boxplot analysis"}
    
    if x_column not in df.columns or y_column not in df.columns:
        return {"error": f"Columns {x_column} and {y_column} not found in data"}
    
    # Analyze group differences
    groups = df[x_column].unique()
    group_stats = {}
    
    for group in groups:
        group_data = df[df[x_column] == group][y_column]
        group_stats[group] = {
            "mean": group_data.mean(),
            "median": group_data.median(),
            "std": group_data.std(),
            "count": len(group_data)
        }
    
    # Find groups with highest/lowest means
    sorted_groups = sorted(group_stats.items(), key=lambda x: x[1]["mean"], reverse=True)
    
    if len(sorted_groups) > 1:
        highest_group = sorted_groups[0]
        lowest_group = sorted_groups[-1]
        mean_diff = highest_group[1]["mean"] - lowest_group[1]["mean"]
        
        analysis["group_comparisons"].extend([
            f"Highest mean: {highest_group[0]} ({highest_group[1]['mean']:.2f})",
            f"Lowest mean: {lowest_group[0]} ({lowest_group[1]['mean']:.2f})",
            f"Difference: {mean_diff:.2f}"
        ])
    
    # Detect outliers in each group
    for group in groups:
        group_data = df[df[x_column] == group][y_column]
        Q1, Q3 = group_data.quantile([0.25, 0.75])
        IQR = Q3 - Q1
        outliers = group_data[(group_data < Q1 - 1.5 * IQR) | (group_data > Q3 + 1.5 * IQR)]
        
        if len(outliers) > 0:
            analysis["outliers"].append(f"Group '{group}': {len(outliers)} outliers")
    
    analysis["insights"].extend([
        f"Comparing {len(groups)} groups across {y_column}",
        f"Total data points: {len(df)}"
    ])
    
    return analysis

def analyze_general_trends(df):
    """Analyze general data trends and patterns"""
    analysis = {
        "summary_stats": {},
        "data_quality": {},
        "trends": [],
        "insights": []
    }
    
    # Summary statistics
    numeric_df = df.select_dtypes(include=[np.number])
    if len(numeric_df.columns) > 0:
        analysis["summary_stats"] = {
            "numeric_columns": len(numeric_df.columns),
            "total_rows": len(df),
            "missing_values": df.isnull().sum().sum()
        }
    
    # Data quality check
    missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
    analysis["data_quality"]["missing_data_pct"] = missing_pct
    
    if missing_pct > 10:
        analysis["trends"].append("High missing data rate - consider data cleaning")
    elif missing_pct > 5:
        analysis["trends"].append("Moderate missing data - some cleaning may be needed")
    else:
        analysis["trends"].append("Good data quality - low missing data rate")
    
    # Column type analysis
    categorical_cols = df.select_dtypes(include=['object']).columns
    analysis["insights"].extend([
        f"Dataset has {len(df.columns)} columns ({len(numeric_df.columns)} numeric, {len(categorical_cols)} categorical)",
        f"Data spans {len(df)} observations"
    ])
    
    return analysis

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

@router.get("/data-context/{session_id}")
async def get_data_context(session_id: str):
    """Get the data context summary for a session"""
    summary = data_context_manager.get_session_summary(session_id)
    return summary

@router.get("/data-context/{session_id}/detailed")
async def get_detailed_data_context(session_id: str):
    """Get detailed data context information for a session"""
    contexts = data_context_manager.get_session_context(session_id)
    if not contexts:
        raise HTTPException(status_code=404, detail="No data context found for session")
    
    detailed_contexts = {}
    for data_id, context in contexts.items():
        detailed_contexts[data_id] = {
            "id": context.id,
            "name": context.name,
            "data_type": context.data_type.value,
            "description": context.description,
            "metadata": context.metadata,
            "created_at": context.created_at.isoformat(),
            "parent_ids": context.parent_ids
        }
    
    return {
        "session_id": session_id,
        "contexts": detailed_contexts
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
    if not PANDAS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Test results processing service is temporarily unavailable. Please try again later or contact support."
        )
    
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


@router.post("/analyze-data")
async def analyze_data(
    session_id: str = Form(...),
    use_session_data: bool = Form(True),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Comprehensive data analysis with insights and recommendations
    """
    if not PANDAS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Data analysis service is temporarily unavailable. Please try again later or contact support."
        )
    
    try:
        # Initialize analyzer
        analyzer = DataAnalyzer()
        
        # Get data for analysis
        if use_session_data and session_id:
            # Use session data (merged data)
            session_data = data_context_manager.get_session_data(session_id)
            if not session_data:
                raise HTTPException(status_code=404, detail="No session data found")
            
            df = pd.read_csv(io.StringIO(session_data))
            print(f"Analyzing session data with shape: {df.shape}")
        elif file:
            # Use uploaded file
            df = pd.read_csv(file.file)
            print(f"Analyzing uploaded file with shape: {df.shape}")
        else:
            raise HTTPException(status_code=400, detail="No data provided")
        
        # Perform comprehensive analysis
        analysis_result = analyzer.analyze_dataset(df, session_id)
        
        # Track analysis in data context
        if session_id:
            data_context_manager.add_analysis(
                session_id=session_id,
                analysis_type="comprehensive",
                analysis_data=analysis_result,
                columns=list(df.columns),
                data_shape=list(df.shape)
            )
        
        return analysis_result
        
    except Exception as e:
        print(f"Error analyzing data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing data: {str(e)}") 