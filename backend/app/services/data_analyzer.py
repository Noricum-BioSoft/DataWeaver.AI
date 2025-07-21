import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json


class AnalysisType(Enum):
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    OUTLIERS = "outliers"
    TRENDS = "trends"
    PATTERNS = "patterns"
    RECOMMENDATIONS = "recommendations"


@dataclass
class DataInsight:
    type: str
    title: str
    description: str
    severity: str  # "info", "warning", "critical"
    data: Dict[str, Any]
    recommendations: List[str]


class DataAnalyzer:
    def __init__(self):
        self.insights = []
    
    def analyze_dataset(self, df: pd.DataFrame, session_id: str = None) -> Dict[str, Any]:
        """
        Comprehensive analysis of a dataset with insights and recommendations
        """
        self.insights = []
        
        # Basic dataset information
        dataset_info = self._analyze_dataset_info(df)
        
        # Data quality analysis
        quality_insights = self._analyze_data_quality(df)
        
        # Statistical analysis
        statistical_insights = self._analyze_statistics(df)
        
        # Correlation analysis
        correlation_insights = self._analyze_correlations(df)
        
        # Pattern detection
        pattern_insights = self._analyze_patterns(df)
        
        # Recommendations
        recommendations = self._generate_recommendations(df)
        
        return {
            "dataset_info": dataset_info,
            "insights": self.insights,
            "quality_analysis": quality_insights,
            "statistical_analysis": statistical_insights,
            "correlation_analysis": correlation_insights,
            "pattern_analysis": pattern_insights,
            "recommendations": recommendations,
            "session_id": session_id
        }
    
    def _analyze_dataset_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze basic dataset information"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        return {
            "shape": [int(df.shape[0]), int(df.shape[1])],
            "total_rows": int(len(df)),
            "total_columns": int(len(df.columns)),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "memory_usage": int(df.memory_usage(deep=True).sum()),
            "column_types": {str(k): str(v) for k, v in df.dtypes.to_dict().items()}
        }
    
    def _analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data quality issues"""
        quality_issues = []
        
        # Missing values analysis
        missing_data = df.isnull().sum()
        missing_percentage = (missing_data / len(df)) * 100
        
        for col in df.columns:
            if missing_data[col] > 0:
                quality_issues.append({
                    "type": "missing_values",
                    "column": col,
                    "count": int(missing_data[col]),
                    "percentage": float(missing_percentage[col]),
                    "severity": "critical" if missing_percentage[col] > 50 else "warning"
                })
        
        # Duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            quality_issues.append({
                "type": "duplicate_rows",
                "count": int(duplicate_count),
                "percentage": float((duplicate_count / len(df)) * 100),
                "severity": "warning"
            })
        
        # Outliers in numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        for col in numeric_df.columns:
            outliers = self._detect_outliers(numeric_df[col])
            if len(outliers) > 0:
                quality_issues.append({
                    "type": "outliers",
                    "column": col,
                    "count": len(outliers),
                    "percentage": float((len(outliers) / len(df)) * 100),
                    "severity": "info"
                })
        
        return {
            "total_issues": len(quality_issues),
            "issues": quality_issues,
            "missing_values_summary": {str(k): int(v) for k, v in missing_data.to_dict().items()},
            "duplicate_rows": int(duplicate_count)
        }
    
    def _analyze_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze statistical properties"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "No numeric columns found for statistical analysis"}
        
        stats = {}
        for col in numeric_df.columns:
            stats[col] = {
                "mean": float(numeric_df[col].mean()),
                "median": float(numeric_df[col].median()),
                "std": float(numeric_df[col].std()),
                "min": float(numeric_df[col].min()),
                "max": float(numeric_df[col].max()),
                "skewness": float(numeric_df[col].skew()),
                "kurtosis": float(numeric_df[col].kurtosis())
            }
        
        return {
            "numeric_columns": list(numeric_df.columns),
            "statistics": stats,
            "summary": {
                "total_numeric_columns": len(numeric_df.columns),
                "total_categorical_columns": len(df.select_dtypes(include=['object']).columns)
            }
        }
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between numeric columns"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {"message": "Need at least 2 numeric columns for correlation analysis"}
        
        corr_matrix = numeric_df.corr()
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # Strong correlation threshold
                    strong_correlations.append({
                        "column1": corr_matrix.columns[i],
                        "column2": corr_matrix.columns[j],
                        "correlation": float(corr_value),
                        "strength": "strong" if abs(corr_value) > 0.8 else "moderate"
                    })
        
        return {
            "correlation_matrix": {str(k): {str(k2): float(v2) for k2, v2 in v.items()} for k, v in corr_matrix.to_dict().items()},
            "strong_correlations": strong_correlations,
            "total_correlations": len(strong_correlations)
        }
    
    def _analyze_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns in the data"""
        patterns = []
        
        # Time series patterns (if date columns exist)
        date_columns = df.select_dtypes(include=['datetime64']).columns
        if len(date_columns) > 0:
            patterns.append({
                "type": "temporal_data",
                "columns": list(date_columns),
                "description": f"Found {len(date_columns)} date/time columns for temporal analysis"
            })
        
        # Categorical patterns
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            unique_values = df[col].nunique()
            if unique_values < 20:  # Low cardinality
                value_counts = df[col].value_counts()
                patterns.append({
                    "type": "categorical_distribution",
                    "column": col,
                    "unique_values": int(unique_values),
                    "most_common": value_counts.head(3).to_dict(),
                    "description": f"Column '{col}' has {unique_values} unique values"
                })
        
        # Numeric patterns
        numeric_df = df.select_dtypes(include=[np.number])
        for col in numeric_df.columns:
            # Check for normal distribution
            skewness = numeric_df[col].skew()
            if abs(skewness) > 1:
                patterns.append({
                    "type": "skewed_distribution",
                    "column": col,
                    "skewness": float(skewness),
                    "description": f"Column '{col}' is {'right' if skewness > 0 else 'left'} skewed"
                })
        
        return {
            "total_patterns": len(patterns),
            "patterns": patterns
        }
    
    def _detect_outliers(self, series: pd.Series) -> List[int]:
        """Detect outliers using IQR method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        return outliers.index.tolist()
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate intelligent recommendations based on analysis"""
        recommendations = []
        
        # Data quality recommendations
        missing_data = df.isnull().sum()
        high_missing_cols = missing_data[missing_data > len(df) * 0.1]
        if len(high_missing_cols) > 0:
            recommendations.append({
                "type": "data_quality",
                "priority": "high",
                "title": "Missing Data Issues",
                "description": f"Columns {list(high_missing_cols.index)} have more than 10% missing values",
                "action": "Consider imputation or removal of these columns"
            })
        
        # Correlation recommendations
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) >= 2:
            corr_matrix = numeric_df.corr()
            high_corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.9:
                        high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j]))
            
            if high_corr_pairs:
                recommendations.append({
                    "type": "feature_engineering",
                    "priority": "medium",
                    "title": "Highly Correlated Features",
                    "description": f"Found {len(high_corr_pairs)} pairs of highly correlated features",
                    "action": "Consider removing one of the correlated features to reduce multicollinearity"
                })
        
        # Outlier recommendations
        outlier_cols = []
        for col in numeric_df.columns:
            outliers = self._detect_outliers(numeric_df[col])
            if len(outliers) > len(df) * 0.05:  # More than 5% outliers
                outlier_cols.append(col)
        
        if outlier_cols:
            recommendations.append({
                "type": "data_cleaning",
                "priority": "medium",
                "title": "Outlier Detection",
                "description": f"Columns {outlier_cols} have significant outliers",
                "action": "Consider outlier treatment methods (winsorization, removal, or transformation)"
            })
        
        # Visualization recommendations
        if len(numeric_df.columns) >= 2:
            recommendations.append({
                "type": "visualization",
                "priority": "low",
                "title": "Visualization Opportunities",
                "description": "Multiple numeric columns available for correlation analysis",
                "action": "Generate correlation plots and scatter plots to explore relationships"
            })
        
        # Feature engineering recommendations
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            recommendations.append({
                "type": "feature_engineering",
                "priority": "medium",
                "title": "Categorical Encoding",
                "description": f"Found {len(categorical_cols)} categorical columns",
                "action": "Consider encoding categorical variables for analysis"
            })
        
        return recommendations 