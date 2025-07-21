from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import json
from dataclasses import dataclass, asdict
from enum import Enum

class DataType(Enum):
    UPLOADED_FILE = "uploaded_file"
    MERGED_DATASET = "merged_dataset"
    VISUALIZATION = "visualization"
    ANALYSIS_RESULT = "analysis_result"

@dataclass
class DataContext:
    """Represents a piece of data in the workflow context"""
    id: str
    name: str
    data_type: DataType
    description: str
    metadata: Dict[str, Any]
    created_at: datetime
    parent_ids: List[str]  # IDs of parent data that this was derived from
    
    def __post_init__(self):
        pass

class DataContextManager:
    """Manages data context throughout the workflow"""
    
    def __init__(self):
        self.contexts: Dict[str, Dict[str, DataContext]] = {}  # session_id -> {data_id -> DataContext}
    
    def create_session(self, session_id: str) -> None:
        """Create a new session for data context tracking"""
        if session_id not in self.contexts:
            self.contexts[session_id] = {}
    
    def add_uploaded_file(self, session_id: str, file_id: str, filename: str, 
                          file_size: int, columns: List[str], row_count: int,
                          numeric_columns: List[str] = None) -> str:
        """Add an uploaded file to the context"""
        self.create_session(session_id)
        
        data_id = str(uuid.uuid4())
        context = DataContext(
            id=data_id,
            name=filename,
            data_type=DataType.UPLOADED_FILE,
            description=f"Uploaded CSV file: {filename}",
            metadata={
                "file_id": file_id,
                "filename": filename,
                "file_size": file_size,
                "columns": columns,
                "row_count": row_count,
                "numeric_columns": numeric_columns if numeric_columns is not None else [],
                "data_shape": [row_count, len(columns)]
            },
            created_at=datetime.now(),
            parent_ids=[]
        )
        
        self.contexts[session_id][data_id] = context
        return data_id
    
    def add_merged_dataset(self, session_id: str, merged_data: Dict[str, Any], 
                          parent_file_ids: Optional[List[str]] = None) -> str:
        """Add a merged dataset to the context"""
        self.create_session(session_id)
        
        data_id = str(uuid.uuid4())
        context = DataContext(
            id=data_id,
            name="Merged Dataset",
            data_type=DataType.MERGED_DATASET,
            description="Dataset created by merging multiple files",
            metadata={
                "total_rows": merged_data.get("totalRows", 0),
                "matched_rows": merged_data.get("matchedRows", 0),
                "unmatched_rows": merged_data.get("unmatchedRows", 0),
                "columns": merged_data.get("headers", []),
                "merge_column": merged_data.get("merge_column", ""),
                "common_columns": merged_data.get("common_columns", []),
                "data_shape": merged_data.get("dataframe_info", {}).get("shape", [0, 0]),
                "numeric_columns": merged_data.get("dataframe_info", {}).get("numeric_columns", [])
            },
            created_at=datetime.now(),
            parent_ids=parent_file_ids or []
        )
        
        self.contexts[session_id][data_id] = context
        return data_id
    
    def add_visualization(self, session_id: str, viz_data: Dict[str, Any], 
                         parent_data_id: str) -> str:
        """Add a visualization to the context"""
        self.create_session(session_id)
        
        data_id = str(uuid.uuid4())
        context = DataContext(
            id=data_id,
            name=f"{viz_data.get('plot_type', 'Visualization').title()}",
            data_type=DataType.VISUALIZATION,
            description=f"Generated {viz_data.get('plot_type', 'visualization')}",
            metadata={
                "plot_type": viz_data.get("plot_type", ""),
                "data_shape": viz_data.get("data_shape", [0, 0]),
                "columns": viz_data.get("columns", []),
                "numeric_columns": viz_data.get("numeric_columns", []),
                "x_column": viz_data.get("x_column"),
                "y_column": viz_data.get("y_column")
            },
            created_at=datetime.now(),
            parent_ids=[parent_data_id]
        )
        
        self.contexts[session_id][data_id] = context
        return data_id
    
    def get_session_context(self, session_id: str) -> Dict[str, DataContext]:
        """Get all data contexts for a session"""
        return self.contexts.get(session_id, {})
    
    def get_data_context(self, session_id: str, data_id: str) -> Optional[DataContext]:
        """Get a specific data context"""
        return self.contexts.get(session_id, {}).get(data_id)
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of all data in a session"""
        contexts = self.get_session_context(session_id)
        
        summary = {
            "session_id": session_id,
            "total_data_items": len(contexts),
            "uploaded_files": [],
            "merged_datasets": [],
            "visualizations": [],
            "data_lineage": {}
        }
        
        for data_id, context in contexts.items():
            item_summary = {
                "id": data_id,
                "name": context.name,
                "description": context.description,
                "created_at": context.created_at.isoformat(),
                "metadata": context.metadata
            }
            
            if context.data_type == DataType.UPLOADED_FILE:
                summary["uploaded_files"].append(item_summary)
            elif context.data_type == DataType.MERGED_DATASET:
                summary["merged_datasets"].append(item_summary)
            elif context.data_type == DataType.VISUALIZATION:
                summary["visualizations"].append(item_summary)
            
            # Build lineage
            summary["data_lineage"][data_id] = {
                "parents": context.parent_ids,
                "children": []
            }
        
        # Find children for each item
        for data_id, context in contexts.items():
            for parent_id in context.parent_ids:
                if parent_id in summary["data_lineage"]:
                    summary["data_lineage"][parent_id]["children"].append(data_id)
        
        return summary
    
    def clear_session(self, session_id: str) -> None:
        """Clear all data contexts for a session"""
        if session_id in self.contexts:
            del self.contexts[session_id]
    
    def clear_session_data(self, session_id: str) -> None:
        """Clear all data contexts for a session (alias for clear_session)"""
        self.clear_session(session_id)
    
    def get_session_data(self, session_id: str) -> Optional[str]:
        """Get the merged dataset data for a session"""
        contexts = self.get_session_context(session_id)
        for data_id, context in contexts.items():
            if context.data_type == DataType.MERGED_DATASET:
                # Return the data from the merged dataset
                # This would typically be stored in a file or database
                # For now, we'll return None and handle this in the calling code
                return None
        return None
    
    def add_analysis(self, session_id: str, analysis_type: str, analysis_data: Dict[str, Any],
                    columns: List[str], data_shape: List[int]) -> str:
        """Add an analysis result to the context"""
        self.create_session(session_id)
        
        data_id = str(uuid.uuid4())
        context = DataContext(
            id=data_id,
            name=f"{analysis_type.title()} Analysis",
            data_type=DataType.ANALYSIS_RESULT,
            description=f"Comprehensive data analysis with insights and recommendations",
            metadata={
                "analysis_type": analysis_type,
                "columns": columns,
                "data_shape": data_shape,
                "insights_count": len(analysis_data.get("insights", [])),
                "recommendations_count": len(analysis_data.get("recommendations", [])),
                "quality_issues": analysis_data.get("quality_analysis", {}).get("total_issues", 0)
            },
            created_at=datetime.now(),
            parent_ids=[]
        )
        
        self.contexts[session_id][data_id] = context
        return data_id

# Global instance
data_context_manager = DataContextManager() 