import json
import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path
import openai
from sqlalchemy.orm import Session
from ..models.file import File, FileMetadata
from ..models.workflow import Workflow
import os
import logging

logger = logging.getLogger(__name__)

class DataQAService:
    """Service for answering questions about data using LLM integration"""
    
    def __init__(self, db: Session, openai_api_key: Optional[str] = None):
        self.db = db
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def analyze_data_context(self, session_id: str, question: str) -> Dict[str, Any]:
        """Analyze data context and answer questions about the data"""
        try:
            # Get files associated with the session
            files = self._get_session_files(session_id)
            if not files:
                return {
                    "success": False,
                    "error": "No data files found for this session",
                    "suggestion": "Please upload some data files first"
                }
            
            # Read and analyze the data
            data_summary = self._analyze_files(files)
            
            # Generate LLM response
            response = self._generate_llm_response(question, data_summary)
            
            return {
                "success": True,
                "answer": response["answer"],
                "insights": response["insights"],
                "data_summary": data_summary,
                "confidence": response["confidence"],
                "suggestions": response["suggestions"]
            }
            
        except Exception as e:
            logger.error(f"Error in data QA: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to analyze data: {str(e)}"
            }
    
    def _get_session_files(self, session_id: str) -> List[Dict[str, Any]]:
        """Get files associated with a workflow session"""
        # Import the workflow state manager
        from services.workflow_state import workflow_state_manager
        from app.services.data_context import data_context_manager
        
        files = []
        
        # Get session data
        session = workflow_state_manager.get_session(session_id)
        if not session:
            return files
        
        # Get uploaded files from data context first (prioritize individual files)
        try:
            context_summary = data_context_manager.get_session_summary(session_id)
            if context_summary and isinstance(context_summary, dict):
                uploaded_files = context_summary.get('uploaded_files', [])
                for file_info in uploaded_files:
                    if isinstance(file_info, dict):
                        files.append({
                            "path": "session_data",  # Virtual path
                            "name": file_info.get('name', 'unknown.csv'),
                            "size": file_info.get('metadata', {}).get('file_size', 0),
                            "data": file_info,
                            "is_virtual": True,
                            "is_individual_file": True
                        })
        except Exception as e:
            logger.error(f"Error getting data context: {str(e)}")
        
        # If no individual files found, check for merged data
        if not files:
            merged_data = session.get('data', {}).get('merged_data')
            if merged_data:
                # Create a virtual file from merged data
                files.append({
                    "path": "session_data",  # Virtual path
                    "name": f"merged_data_{session_id}.csv",
                    "size": len(str(merged_data)),
                    "data": merged_data,
                    "is_virtual": True,
                    "is_merged_data": True
                })
        
        return files
    
    def _analyze_files(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze uploaded files and extract key information"""
        analysis = {
            "total_files": len(files),
            "file_types": {},
            "total_rows": 0,
            "total_columns": 0,
            "columns": [],
            "data_types": {},
            "missing_values": {},
            "numeric_columns": [],
            "categorical_columns": [],
            "sample_data": {},
            "statistics": {}
        }
        
        for file_info in files:
            try:
                file_name = file_info["name"]
                
                # Handle virtual files (session data)
                if file_info.get("is_virtual", False):
                    if "data" in file_info and isinstance(file_info["data"], dict):
                        # Check if this is individual file data or merged data
                        if file_info.get("is_individual_file", False):
                            # This is individual file info from context
                            file_data = file_info["data"]
                            metadata = file_data.get("metadata", {})
                            row_count = metadata.get("row_count", 0)
                            columns = metadata.get("columns", [])
                            numeric_columns = metadata.get("numeric_columns", [])
                            
                            # Create a dummy DataFrame for analysis
                            # Since we don't have the actual data, we'll use metadata
                            if row_count > 0 and columns:
                                # Create a simple DataFrame with the structure we know
                                df_data = {}
                                for col in columns:
                                    if col in numeric_columns:
                                        # Create numeric dummy data
                                        df_data[col] = [i + 1 for i in range(row_count)]
                                    else:
                                        # Create string dummy data
                                        df_data[col] = [f"data_{i}" for i in range(row_count)]
                                
                                df = pd.DataFrame(df_data)
                            else:
                                continue
                        elif file_info.get("is_merged_data", False):
                            # This is merged data from session
                            merged_data = file_info["data"]
                            if "headers" in merged_data and "rows" in merged_data:
                                df = pd.DataFrame(merged_data["rows"], columns=merged_data["headers"])
                            else:
                                # Skip files without proper data structure
                                continue
                        else:
                            # This is uploaded file info from context
                            # We don't have the actual data, so skip
                            continue
                else:
                    # Regular file on disk
                    df = pd.read_csv(file_info["path"])
                
                # Basic file info
                analysis["total_rows"] += len(df)
                analysis["total_columns"] += len(df.columns)
                analysis["file_types"][file_name] = "csv"
                
                # Column analysis
                for col in df.columns:
                    if col not in analysis["columns"]:
                        analysis["columns"].append(col)
                    
                    # Data type analysis
                    dtype = str(df[col].dtype)
                    if dtype not in analysis["data_types"]:
                        analysis["data_types"][dtype] = []
                    analysis["data_types"][dtype].append(col)
                    
                    # Missing values
                    missing_count = df[col].isnull().sum()
                    if missing_count > 0:
                        if col not in analysis["missing_values"]:
                            analysis["missing_values"][col] = 0
                        analysis["missing_values"][col] += missing_count
                    
                    # Numeric vs categorical
                    if pd.api.types.is_numeric_dtype(df[col]):
                        if col not in analysis["numeric_columns"]:
                            analysis["numeric_columns"].append(col)
                    else:
                        if col not in analysis["categorical_columns"]:
                            analysis["categorical_columns"].append(col)
                
                # Sample data
                analysis["sample_data"][file_name] = df.head(3).to_dict('records')
                
                # Basic statistics for numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    stats = df[numeric_cols].describe()
                    analysis["statistics"][file_name] = stats.to_dict()
                
            except Exception as e:
                logger.error(f"Error analyzing file {file_info['name']}: {str(e)}")
                continue
        
        return analysis
    
    def _generate_llm_response(self, question: str, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate LLM response based on question and data analysis"""
        
        # Create context for the LLM
        context = self._create_llm_context(question, data_summary)
        
        if not self.openai_api_key:
            # Fallback to rule-based responses
            return self._generate_fallback_response(question, data_summary)
        
        try:
            # Prepare the prompt
            system_prompt = """You are a data analysis assistant. You help users understand their data by answering questions and providing insights. 
            Be concise, accurate, and helpful. If you don't have enough information to answer a question, say so.
            Always provide actionable insights when possible."""
            
            user_prompt = f"""
            Data Context:
            {json.dumps(data_summary, indent=2)}
            
            User Question: {question}
            
            Please provide:
            1. A direct answer to the question
            2. Key insights about the data
            3. Confidence level (high/medium/low)
            4. Suggestions for further analysis
            """
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            llm_response = response.choices[0].message.content
            
            # Parse the response
            return self._parse_llm_response(llm_response or "", data_summary)
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return self._generate_fallback_response(question, data_summary)
    
    def _create_llm_context(self, question: str, data_summary: Dict[str, Any]) -> str:
        """Create context string for LLM"""
        context_parts = []
        
        # Basic data info
        context_parts.append(f"Dataset contains {data_summary['total_files']} files with {data_summary['total_rows']} total rows and {data_summary['total_columns']} total columns.")
        
        # Column information
        if data_summary['columns']:
            context_parts.append(f"Columns: {', '.join(data_summary['columns'])}")
        
        # Data types
        if data_summary['data_types']:
            type_info = []
            for dtype, cols in data_summary['data_types'].items():
                type_info.append(f"{dtype}: {', '.join(cols[:5])}")  # Limit to first 5 columns
            context_parts.append(f"Data types: {'; '.join(type_info)}")
        
        # Numeric columns
        if data_summary['numeric_columns']:
            context_parts.append(f"Numeric columns: {', '.join(data_summary['numeric_columns'])}")
        
        # Missing values
        if data_summary['missing_values']:
            missing_info = []
            for col, count in data_summary['missing_values'].items():
                missing_info.append(f"{col}: {count} missing")
            context_parts.append(f"Missing values: {'; '.join(missing_info)}")
        
        return "\n".join(context_parts)
    
    def _parse_llm_response(self, response: str, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        # Simple parsing - in production you might want more sophisticated parsing
        return {
            "answer": response,
            "insights": self._extract_insights(response),
            "confidence": self._extract_confidence(response),
            "suggestions": self._extract_suggestions(response)
        }
    
    def _extract_insights(self, response: str) -> List[str]:
        """Extract insights from LLM response"""
        insights = []
        lines = response.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['insight', 'finding', 'pattern', 'trend']):
                insights.append(line.strip())
        return insights[:3]  # Limit to 3 insights
    
    def _extract_confidence(self, response: str) -> str:
        """Extract confidence level from response"""
        response_lower = response.lower()
        if 'high confidence' in response_lower or 'very confident' in response_lower:
            return "high"
        elif 'medium confidence' in response_lower or 'somewhat confident' in response_lower:
            return "medium"
        else:
            return "low"
    
    def _extract_suggestions(self, response: str) -> List[str]:
        """Extract suggestions from LLM response"""
        suggestions = []
        lines = response.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['suggest', 'recommend', 'consider', 'try']):
                suggestions.append(line.strip())
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _generate_fallback_response(self, question: str, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback response when LLM is not available"""
        question_lower = question.lower()
        
        # Enhanced rule-based responses
        if 'how many' in question_lower:
            answer = f"The dataset contains {data_summary['total_rows']} total rows across {data_summary['total_files']} files."
        elif 'columns' in question_lower:
            answer = f"The dataset has {len(data_summary['columns'])} unique columns: {', '.join(data_summary['columns'])}"
        elif 'missing' in question_lower:
            if data_summary['missing_values']:
                missing_info = []
                for col, count in data_summary['missing_values'].items():
                    missing_info.append(f"{col}: {count} missing")
                answer = f"Missing values found: {'; '.join(missing_info)}"
            else:
                answer = "No missing values detected in the dataset."
        elif 'numeric' in question_lower:
            if data_summary['numeric_columns']:
                answer = f"Numeric columns: {', '.join(data_summary['numeric_columns'])}"
            else:
                answer = "No numeric columns found in the dataset."
        elif 'outlier' in question_lower:
            if data_summary['numeric_columns']:
                answer = "I can help identify outliers in numeric columns. To detect outliers, I would need to analyze the statistical distribution of your numeric data. Consider asking about specific numeric columns or use the visualization features to create box plots for outlier detection."
            else:
                answer = "No numeric columns found in the dataset, so outlier analysis is not applicable."
        elif 'average' in question_lower or 'mean' in question_lower:
            if data_summary['numeric_columns']:
                answer = f"I can calculate averages for numeric columns: {', '.join(data_summary['numeric_columns'])}. Please specify which column you'd like to analyze."
            else:
                answer = "No numeric columns found in the dataset for calculating averages."
        elif 'correlation' in question_lower:
            if len(data_summary['numeric_columns']) >= 2:
                answer = f"I can analyze correlations between numeric columns: {', '.join(data_summary['numeric_columns'])}. Consider using the visualization features to create correlation plots."
            else:
                answer = "Need at least 2 numeric columns for correlation analysis."
        elif 'unique' in question_lower or 'distinct' in question_lower:
            answer = f"I can analyze unique values in columns: {', '.join(data_summary['columns'])}. Please specify which column you'd like to analyze."
        elif 'data type' in question_lower or 'dtype' in question_lower:
            type_info = []
            for dtype, cols in data_summary['data_types'].items():
                type_info.append(f"{dtype}: {', '.join(cols[:5])}")
            answer = f"Data types: {'; '.join(type_info)}"
        elif 'file' in question_lower and 'name' in question_lower:
            answer = f"You have {data_summary['total_files']} files in your dataset."
        else:
            answer = f"I can see you have {data_summary['total_files']} files with {data_summary['total_rows']} total rows. What specific aspect would you like to know more about?"
        
        return {
            "answer": answer,
            "insights": ["Data analysis requires more context for detailed insights"],
            "confidence": "medium",
            "suggestions": [
                "Ask about specific columns or data types",
                "Use visualization features for deeper analysis",
                "Upload more data files for comprehensive analysis"
            ]
        }
    
    def get_data_preview(self, session_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get a preview of the data for the chat interface"""
        try:
            files = self._get_session_files(session_id)
            if not files:
                return {"error": "No data files found"}
            
            preview_data = {}
            for file_info in files[:3]:  # Limit to first 3 files
                try:
                    file_name = file_info["name"]
                    
                    # Handle virtual files (session data)
                    if file_info.get("is_virtual", False):
                        if "data" in file_info and isinstance(file_info["data"], dict):
                            # This is merged data from session
                            merged_data = file_info["data"]
                            if "headers" in merged_data and "rows" in merged_data:
                                df = pd.DataFrame(merged_data["rows"], columns=merged_data["headers"])
                                preview_data[file_name] = {
                                    "rows": len(df),
                                    "columns": list(df.columns),
                                    "sample": df.head(limit).to_dict('records'),
                                    "dtypes": df.dtypes.to_dict()
                                }
                            else:
                                preview_data[file_name] = {"error": "Invalid data structure"}
                        else:
                            # This is uploaded file info from context
                            preview_data[file_name] = {"error": "No data available"}
                    else:
                        # Regular file on disk
                        df = pd.read_csv(file_info["path"])
                        preview_data[file_name] = {
                            "rows": len(df),
                            "columns": list(df.columns),
                            "sample": df.head(limit).to_dict('records'),
                            "dtypes": df.dtypes.to_dict()
                        }
                except Exception as e:
                    preview_data[file_info["name"]] = {"error": str(e)}
            
            return {"success": True, "preview": preview_data}
            
        except Exception as e:
            return {"error": f"Failed to get data preview: {str(e)}"} 