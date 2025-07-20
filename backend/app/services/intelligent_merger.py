"""
Intelligent Data Merging Service
Analyzes multiple files and suggests merge strategies
"""

import pandas as pd
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import io
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MergeStrategy(Enum):
    INNER_JOIN = "inner_join"
    LEFT_JOIN = "left_join"
    RIGHT_JOIN = "right_join"
    OUTER_JOIN = "outer_join"
    CONCATENATE = "concatenate"
    NO_MERGE = "no_merge"

@dataclass
class MergeSuggestion:
    strategy: MergeStrategy
    confidence: float  # 0.0 to 1.0
    description: str
    join_keys: List[str]
    expected_rows: int
    warnings: List[str]
    data_quality_score: float

@dataclass
class FileAnalysis:
    file_id: str
    filename: str
    file_type: str
    columns: List[str]
    data_types: Dict[str, str]
    row_count: int
    sample_data: List[Dict[str, Any]]
    quality_score: float

class IntelligentMerger:
    """Analyzes multiple files and suggests intelligent merge strategies"""
    
    def __init__(self):
        self.supported_formats = {'.csv', '.json', '.xlsx', '.xls', '.parquet'}
    
    def analyze_files(self, files: List[Dict[str, Any]]) -> List[FileAnalysis]:
        """Analyze multiple files and return their characteristics"""
        analyses = []
        
        for file_info in files:
            try:
                file_path = file_info['file_path']
                file_id = file_info['file_id']
                filename = file_info['filename']
                
                analysis = self._analyze_single_file(file_path, file_id, filename)
                analyses.append(analysis)
                
            except Exception as e:
                logger.error(f"Error analyzing file {file_info.get('filename', 'unknown')}: {e}")
                continue
        
        return analyses
    
    def _analyze_single_file(self, file_path: str, file_id: str, filename: str) -> FileAnalysis:
        """Analyze a single file and return its characteristics"""
        file_type = Path(filename).suffix.lower()
        
        if file_type == '.csv':
            return self._analyze_csv(file_path, file_id, filename)
        elif file_type == '.json':
            return self._analyze_json(file_path, file_id, filename)
        elif file_type in {'.xlsx', '.xls'}:
            return self._analyze_excel(file_path, file_id, filename)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _analyze_csv(self, file_path: str, file_id: str, filename: str) -> FileAnalysis:
        """Analyze a CSV file"""
        df = pd.read_csv(file_path)
        
        # Analyze data types
        data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(df)
        
        # Get sample data
        sample_data = df.head(3).to_dict('records')
        
        return FileAnalysis(
            file_id=file_id,
            filename=filename,
            file_type='csv',
            columns=list(df.columns),
            data_types=data_types,
            row_count=len(df),
            sample_data=sample_data,
            quality_score=quality_score
        )
    
    def _analyze_json(self, file_path: str, file_id: str, filename: str) -> FileAnalysis:
        """Analyze a JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Convert to DataFrame for analysis
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Handle nested JSON
            df = pd.json_normalize(data)
        else:
            raise ValueError("Unsupported JSON structure")
        
        data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
        quality_score = self._calculate_quality_score(df)
        sample_data = df.head(3).to_dict('records')
        
        return FileAnalysis(
            file_id=file_id,
            filename=filename,
            file_type='json',
            columns=list(df.columns),
            data_types=data_types,
            row_count=len(df),
            sample_data=sample_data,
            quality_score=quality_score
        )
    
    def _analyze_excel(self, file_path: str, file_id: str, filename: str) -> FileAnalysis:
        """Analyze an Excel file"""
        df = pd.read_excel(file_path)
        
        data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
        quality_score = self._calculate_quality_score(df)
        sample_data = df.head(3).to_dict('records')
        
        return FileAnalysis(
            file_id=file_id,
            filename=filename,
            file_type='excel',
            columns=list(df.columns),
            data_types=data_types,
            row_count=len(df),
            sample_data=sample_data,
            quality_score=quality_score
        )
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate data quality score (0.0 to 1.0)"""
        if df.empty:
            return 0.0
        
        # Check for missing values
        missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        
        # Check for duplicate rows
        duplicate_ratio = df.duplicated().sum() / len(df)
        
        # Check for consistent data types
        type_consistency = 1.0 - (df.dtypes.nunique() / len(df.columns))
        
        # Overall quality score
        quality = 1.0 - (missing_ratio + duplicate_ratio) / 2
        quality = max(0.0, min(1.0, quality))
        
        return quality
    
    def suggest_merge_strategies(self, analyses: List[FileAnalysis]) -> List[MergeSuggestion]:
        """Analyze multiple files and suggest merge strategies"""
        if len(analyses) < 2:
            return []
        
        suggestions = []
        
        # Strategy 1: Look for common columns (join strategy)
        join_suggestion = self._suggest_join_strategy(analyses)
        if join_suggestion:
            suggestions.append(join_suggestion)
        
        # Strategy 2: Check if files can be concatenated
        concat_suggestion = self._suggest_concatenate_strategy(analyses)
        if concat_suggestion:
            suggestions.append(concat_suggestion)
        
        # Strategy 3: No merge possible
        if not suggestions:
            suggestions.append(MergeSuggestion(
                strategy=MergeStrategy.NO_MERGE,
                confidence=1.0,
                description="Files have incompatible structures and cannot be merged",
                join_keys=[],
                expected_rows=0,
                warnings=["No common columns found", "Data structures are incompatible"],
                data_quality_score=0.0
            ))
        
        return suggestions
    
    def _suggest_join_strategy(self, analyses: List[FileAnalysis]) -> Optional[MergeSuggestion]:
        """Suggest join-based merge strategies"""
        if len(analyses) < 2:
            return None
        
        # Find common columns across all files
        all_columns = [set(analysis.columns) for analysis in analyses]
        common_columns = set.intersection(*all_columns)
        
        if not common_columns:
            return None
        
        # Find potential join keys (columns with good data quality)
        potential_keys = []
        for col in common_columns:
            key_quality = self._assess_column_as_key(analyses, col)
            if key_quality > 0.3:  # Lower threshold to be more inclusive
                potential_keys.append((col, key_quality))
        
        # If no keys meet the threshold, try all common columns
        if not potential_keys:
            for col in common_columns:
                key_quality = self._assess_column_as_key(analyses, col)
                potential_keys.append((col, key_quality))
        
        if not potential_keys:
            return None
        
        # Sort by quality and take the best key
        potential_keys.sort(key=lambda x: x[1], reverse=True)
        best_key, key_quality = potential_keys[0]
        
        # Calculate expected rows and confidence
        min_rows = min(analysis.row_count for analysis in analyses)
        max_rows = max(analysis.row_count for analysis in analyses)
        
        # Estimate join result size
        if len(analyses) == 2:
            # Simple estimation for 2 files
            expected_rows = min_rows  # Conservative estimate
        else:
            # More complex estimation for multiple files
            expected_rows = min_rows
        
        confidence = key_quality * 0.8  # Reduce confidence for estimation uncertainty
        
        warnings = []
        if key_quality < 0.8:
            warnings.append(f"Join key '{best_key}' has some data quality issues")
        
        if expected_rows < min_rows * 0.5:
            warnings.append("Expected result size is significantly smaller than input files")
        
        return MergeSuggestion(
            strategy=MergeStrategy.INNER_JOIN,
            confidence=confidence,
            description=f"Merge files using '{best_key}' as join key",
            join_keys=[best_key],
            expected_rows=expected_rows,
            warnings=warnings,
            data_quality_score=key_quality
        )
    
    def _suggest_concatenate_strategy(self, analyses: List[FileAnalysis]) -> Optional[MergeSuggestion]:
        """Suggest concatenation-based merge strategies"""
        if len(analyses) < 2:
            return None
        
        # Check if files have similar structure (same columns)
        first_columns = set(analyses[0].columns)
        all_similar = all(set(analysis.columns) == first_columns for analysis in analyses[1:])
        
        if not all_similar:
            return None
        
        # Check data type compatibility
        type_compatibility = self._check_type_compatibility(analyses)
        if not type_compatibility:
            return None
        
        # Calculate expected rows
        expected_rows = sum(analysis.row_count for analysis in analyses)
        
        # Calculate confidence based on structure similarity
        confidence = 0.9 if all_similar else 0.6
        
        warnings = []
        if len(set(analysis.row_count for analysis in analyses)) > 1:
            warnings.append("Files have different numbers of rows")
        
        return MergeSuggestion(
            strategy=MergeStrategy.CONCATENATE,
            confidence=confidence,
            description="Concatenate files with similar structure",
            join_keys=[],
            expected_rows=expected_rows,
            warnings=warnings,
            data_quality_score=0.8
        )
    
    def _assess_column_as_key(self, analyses: List[FileAnalysis], column: str) -> float:
        """Assess how well a column can serve as a join key"""
        scores = []
        
        # Check if column name suggests it's an ID/key
        column_lower = column.lower()
        id_patterns = ['id', 'key', 'identifier', 'name', 'code']
        is_id_like = any(pattern in column_lower for pattern in id_patterns)
        
        for analysis in analyses:
            # Check if column exists
            if column not in analysis.columns:
                return 0.0
            
            # Check data type (prefer string/numeric)
            dtype = analysis.data_types.get(column, '')
            if 'object' in dtype or 'int' in dtype or 'float' in dtype:
                scores.append(0.8)
            else:
                scores.append(0.4)
            
            # Bonus for ID-like column names
            if is_id_like:
                scores.append(0.2)
            
            # Check for nulls (lower score for more nulls)
            # This would require loading the actual data, so we estimate
            scores.append(0.9)  # Assume good quality for now
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _check_type_compatibility(self, analyses: List[FileAnalysis]) -> bool:
        """Check if data types are compatible for concatenation"""
        if not analyses:
            return False
        
        first_types = analyses[0].data_types
        
        for analysis in analyses[1:]:
            for col in first_types:
                if col in analysis.data_types:
                    # Simple compatibility check
                    if first_types[col] != analysis.data_types[col]:
                        # Check if they're both numeric or both string
                        first_numeric = any(num_type in first_types[col] for num_type in ['int', 'float'])
                        second_numeric = any(num_type in analysis.data_types[col] for num_type in ['int', 'float'])
                        
                        if first_numeric != second_numeric:
                            return False
        
        return True
    
    def execute_merge(self, files: List[Dict[str, Any]], strategy: MergeSuggestion) -> Dict[str, Any]:
        """Execute the merge based on the suggested strategy"""
        try:
            if strategy.strategy == MergeStrategy.INNER_JOIN:
                return self._execute_join_merge(files, strategy)
            elif strategy.strategy == MergeStrategy.CONCATENATE:
                return self._execute_concatenate_merge(files, strategy)
            else:
                raise ValueError(f"Cannot execute merge strategy: {strategy.strategy}")
                
        except Exception as e:
            logger.error(f"Error executing merge: {e}")
            return {
                "success": False,
                "error": str(e),
                "merged_data": None
            }
    
    def _execute_join_merge(self, files: List[Dict[str, Any]], strategy: MergeSuggestion) -> Dict[str, Any]:
        """Execute a join-based merge"""
        dataframes = []
        
        for file_info in files:
            file_path = file_info['file_path']
            file_type = Path(file_info['filename']).suffix.lower()
            
            if file_type == '.csv':
                df = pd.read_csv(file_path)
            elif file_type == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.json_normalize(data)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            dataframes.append(df)
        
        # Perform the join
        result_df = dataframes[0]
        join_key = strategy.join_keys[0]
        
        for df in dataframes[1:]:
            result_df = result_df.merge(df, on=join_key, how='inner')
        
        # Convert to records for JSON serialization and handle NaN values
        merged_data = result_df.replace({pd.NA: None, pd.NaT: None}).to_dict('records')
        
        return {
            "success": True,
            "merged_data": merged_data,
            "row_count": len(result_df),
            "column_count": len(result_df.columns),
            "join_key": join_key
        }
    
    def _execute_concatenate_merge(self, files: List[Dict[str, Any]], strategy: MergeSuggestion) -> Dict[str, Any]:
        """Execute a concatenation-based merge"""
        dataframes = []
        
        for file_info in files:
            file_path = file_info['file_path']
            file_type = Path(file_info['filename']).suffix.lower()
            
            if file_type == '.csv':
                df = pd.read_csv(file_path)
            elif file_type == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.json_normalize(data)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            dataframes.append(df)
        
        # Concatenate all dataframes
        result_df = pd.concat(dataframes, ignore_index=True)
        
        # Convert to records for JSON serialization and handle NaN values
        merged_data = result_df.replace({pd.NA: None, pd.NaT: None}).to_dict('records')
        
        return {
            "success": True,
            "merged_data": merged_data,
            "row_count": len(result_df),
            "column_count": len(result_df.columns),
            "concatenated_files": len(files)
        } 