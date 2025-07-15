# import pandas as pd  # Temporarily disabled for Python 3.13 compatibility
# import numpy as np  # Temporarily disabled for Python 3.13 compatibility
from typing import List, Dict, Any, Optional, Tuple
from fuzzywuzzy import fuzz, process
# from sklearn.feature_extraction.text import TfidfVectorizer  # Temporarily disabled for Python 3.13 compatibility
# from sklearn.metrics.pairwise import cosine_similarity  # Temporarily disabled for Python 3.13 compatibility
from sqlalchemy.orm import Session
from ..models.workflow import Workflow, WorkflowStep
from ..models.file import File, FileMetadata
from ..models.dataset import Dataset, DatasetMatch, MatchType, DatasetStatus
from ..schemas.dataset import MatchingConfig

class MatchingService:
    def __init__(self):
        # ML-based matching is disabled due to missing sklearn
        pass
    
    def extract_identifiers(self, file_path: str, config: MatchingConfig) -> Dict[str, Any]:
        """Extract identifiers from a file for matching."""
        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    if not lines:
                        return {}
                    columns = lines[0].strip().split(',')
                    identifiers = {
                        'columns': columns,
                        'row_count': len(lines) - 1,
                        'column_count': len(columns)
                    }
                    # Extract sample data for matching
                    identifiers['sample_data'] = lines[1:11]
                    return identifiers
            elif file_path.endswith(('.xlsx', '.xls')):
                # Excel parsing requires pandas, so we skip for now
                return {'note': 'Excel parsing requires pandas, not available in this environment.'}
            else:
                return {}
        except Exception as e:
            return {'error': str(e)}
    
    def exact_match(
        self, 
        dataset_identifiers: Dict[str, Any], 
        workflow_files: List[File],
        db: Session
    ) -> List[Tuple[File, float]]:
        """Perform exact matching based on identifiers."""
        matches = []
        
        for file in workflow_files:
            if file.file_type.value in ['csv', 'excel']:
                # Get file metadata
                metadata = db.query(FileMetadata).filter(
                    FileMetadata.file_id == file.id
                ).all()
                
                file_identifiers = {m.key: m.value for m in metadata}
                
                # Check for exact column matches
                if 'columns' in dataset_identifiers and 'columns' in file_identifiers:
                    dataset_cols = set(dataset_identifiers['columns'])
                    file_cols = set(file_identifiers['columns'].split(','))
                    
                    if dataset_cols == file_cols:
                        matches.append((file, 1.0))
                
                # Check for exact value matches in identifier columns
                for key, value in dataset_identifiers.items():
                    if key.startswith('values_') and key in file_identifiers:
                        dataset_values = set(value)
                        file_values = set(file_identifiers[key].split(','))
                        
                        if dataset_values == file_values:
                            matches.append((file, 1.0))
        
        return matches
    
    def fuzzy_match(
        self, 
        dataset_identifiers: Dict[str, Any], 
        workflow_files: List[File],
        db: Session,
        threshold: float = 0.8
    ) -> List[Tuple[File, float]]:
        """Perform fuzzy matching using string similarity."""
        matches = []
        
        for file in workflow_files:
            if file.file_type.value in ['csv', 'excel']:
                metadata = db.query(FileMetadata).filter(
                    FileMetadata.file_id == file.id
                ).all()
                
                file_identifiers = {m.key: m.value for m in metadata}
                
                # Compare column names
                if 'columns' in dataset_identifiers and 'columns' in file_identifiers:
                    dataset_cols = dataset_identifiers['columns']
                    file_cols = file_identifiers['columns'].split(',')
                    
                    for dataset_col in dataset_cols:
                        for file_col in file_cols:
                            similarity = fuzz.ratio(dataset_col.lower(), file_col.lower()) / 100.0
                            if similarity >= threshold:
                                matches.append((file, similarity))
                
                # Compare identifier values
                for key, value in dataset_identifiers.items():
                    if key.startswith('values_') and key in file_identifiers:
                        dataset_values = value
                        file_values = file_identifiers[key].split(',')
                        
                        for dataset_val in dataset_values:
                            for file_val in file_values:
                                similarity = fuzz.ratio(
                                    str(dataset_val).lower(), 
                                    str(file_val).lower()
                                ) / 100.0
                                if similarity >= threshold:
                                    matches.append((file, similarity))
        
        return matches
    
    # ML-based matching is disabled due to missing sklearn
    # def ml_based_match(
    #     self, 
    #     dataset_identifiers: Dict[str, Any], 
    #     workflow_files: List[File],
    #     db: Session
    # ) -> List[Tuple[File, float]]:
    #     """Perform ML-based matching using TF-IDF and cosine similarity."""
    #     matches = []
    #     
    #     # Prepare dataset text
    #     dataset_text = self._prepare_text_for_ml(dataset_identifiers)
    #     
    #     for file in workflow_files:
    #         if file.file_type.value in ['csv', 'excel']:
    #             metadata = db.query(FileMetadata).filter(
    #                 FileMetadata.file_id == file.id
    #             ).all()
    #             
    #             file_identifiers = {m.key: m.value for m in metadata}
    #             file_text = self._prepare_text_for_ml(file_identifiers)
    #             
    #             if dataset_text and file_text:
    #                 # Calculate similarity using TF-IDF
    #                 try:
    #                     texts = [dataset_text, file_text]
    #                     tfidf_matrix = self.vectorizer.fit_transform(texts)
    #                     similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    #                     
    #                     if similarity > 0.3:  # Lower threshold for ML matching
    #                         matches.append((file, similarity))
    #                 except Exception:
    #                     continue
    #     
    #     return matches
    
    def _prepare_text_for_ml(self, identifiers: Dict[str, Any]) -> str:
        """Prepare text for ML-based matching."""
        text_parts = []
        
        for key, value in identifiers.items():
            if isinstance(value, list):
                text_parts.extend([str(v) for v in value])
            elif isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, (int, float)):
                text_parts.append(str(value))
        
        return ' '.join(text_parts)
    
    def find_matches(
        self, 
        dataset_id: int, 
        workflow_id: int,
        db: Session,
        config: MatchingConfig
    ) -> List[DatasetMatch]:
        """Find matches for a dataset in a specific workflow."""
        
        # Get dataset
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            return []
        
        # Get workflow files
        workflow_files = db.query(File).filter(
            File.workflow_id == workflow_id,
            File.status != 'deleted'
        ).all()
        
        if not workflow_files:
            return []
        
        matches = []
        
        # Perform different types of matching
        # ML-based matching is disabled due to missing sklearn
        # if config.ml_model:
        #     ml_matches = self.ml_based_match(dataset.identifiers, workflow_files, db)
        #     for file, score in ml_matches:
        #         match = DatasetMatch(
        #             dataset_id=dataset_id,
        #             workflow_id=workflow_id,
        #             file_id=file.id,
        #             match_type=MatchType.ML_BASED,
        #             confidence_score=score,
        #             matching_criteria={'method': 'ml_based', 'model': config.ml_model}
        #         )
        #         matches.append(match)
        
        # Fuzzy matching
        fuzzy_matches = self.fuzzy_match(
            dataset.identifiers, 
            workflow_files, 
            db, 
            config.fuzzy_threshold
        )
        for file, score in fuzzy_matches:
            match = DatasetMatch(
                dataset_id=dataset_id,
                workflow_id=workflow_id,
                file_id=file.id,
                match_type=MatchType.FUZZY,
                confidence_score=score,
                matching_criteria={'method': 'fuzzy', 'threshold': config.fuzzy_threshold}
            )
            matches.append(match)
        
        # Exact matching
        exact_matches = self.exact_match(dataset.identifiers, workflow_files, db)
        for file, score in exact_matches:
            match = DatasetMatch(
                dataset_id=dataset_id,
                workflow_id=workflow_id,
                file_id=file.id,
                match_type=MatchType.EXACT,
                confidence_score=score,
                matching_criteria={'method': 'exact'}
            )
            matches.append(match)
        
        # Remove duplicates and sort by confidence
        unique_matches = {}
        for match in matches:
            key = (match.dataset_id, match.workflow_id, match.file_id)
            if key not in unique_matches or match.confidence_score > unique_matches[key].confidence_score:
                unique_matches[key] = match
        
        return sorted(unique_matches.values(), key=lambda x: x.confidence_score, reverse=True)
    
    def auto_match_dataset(
        self, 
        dataset_id: int, 
        db: Session,
        config: MatchingConfig
    ) -> List[DatasetMatch]:
        """Automatically match a dataset to all workflows."""
        
        # Get all workflows
        workflows = db.query(Workflow).all()
        all_matches = []
        
        for workflow in workflows:
            matches = self.find_matches(dataset_id, workflow.id, db, config)
            all_matches.extend(matches)
        
        # Save matches to database
        for match in all_matches:
            db.add(match)
        
        db.commit()
        
        return all_matches 