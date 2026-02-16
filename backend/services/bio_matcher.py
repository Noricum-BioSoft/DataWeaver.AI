import hashlib
import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from models.bio_entities import Design, Build, Test
import csv
import io


class BioEntityMatcher:
    """Service for matching biological entities based on sequences, mutations, and aliases"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def parse_mutations(self, mutation_string: str) -> List[str]:
        """Parse mutation string into list of mutations"""
        if not mutation_string or not isinstance(mutation_string, str):
            return []
        # Split on comma, semicolon, or space
        mutations = re.split(r'[;,\s]+', mutation_string.strip())
        return [m.strip() for m in mutations if m.strip()]
    
    def normalize_sequence(self, sequence: str) -> str:
        """Normalize sequence for comparison"""
        if not sequence:
            return ""
        
        # Convert to uppercase and normalize separators
        normalized = sequence.upper()
        # Replace multiple spaces/dashes with single dots
        normalized = re.sub(r'[-\s]+', '...', normalized)
        # Ensure consistent dot spacing
        normalized = re.sub(r'\.{2,}', '...', normalized)
        return normalized
    
    def compute_lineage_hash(self, parent_hash: str, mutations: List[str], sequence: str) -> str:
        """Compute lineage hash based on parent and mutations"""
        mutation_str = ",".join(mutations) if mutations else ""
        content = f"{parent_hash}:{mutation_str}:{sequence}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def match_by_sequence(self, sequence: str) -> Tuple[Optional[Design], Optional[Build], float]:
        """Match by exact sequence"""
        normalized_sequence = self.normalize_sequence(sequence)
        
        # Try to match design first
        design = self.db.query(Design).filter(
            Design.sequence == normalized_sequence,
            Design.is_active == True
        ).first()
        
        if design:
            return design, None, 1.0
        
        # Try to match build
        build = self.db.query(Build).filter(
            Build.sequence == normalized_sequence,
            Build.is_active == True
        ).first()
        
        if build:
            return None, build, 1.0
        
        return None, None, 0.0
    
    def match_by_mutations(self, mutations: List[str]) -> Tuple[Optional[Design], Optional[Build], float]:
        """Match by mutations"""
        if not mutations:
            return None, None, 0.0
        
        # Find designs/builds with matching mutations
        mutation_pattern = "%" + "%".join(mutations) + "%"
        
        # Try designs first
        design = self.db.query(Design).filter(
            Design.mutation_list.ilike(mutation_pattern),
            Design.is_active == True
        ).first()
        
        if design:
            design_mutations = self.parse_mutations(design.mutation_list or "")
            overlap = len(set(mutations) & set(design_mutations))
            if overlap == len(mutations) == len(design_mutations):
                return design, None, 0.8
            elif overlap > 0:
                return design, None, 0.6
            return design, None, 0.4  # Lower score for pattern match but no overlap
        
        # Try builds
        build = self.db.query(Build).filter(
            Build.mutation_list.ilike(mutation_pattern),
            Build.is_active == True
        ).first()
        
        if build:
            build_mutations = self.parse_mutations(build.mutation_list or "")
            overlap = len(set(mutations) & set(build_mutations))
            if overlap == len(mutations) == len(build_mutations):
                return None, build, 0.8
            elif overlap > 0:
                return None, build, 0.6
            return None, build, 0.4  # Lower score for pattern match but no overlap
        
        return None, None, 0.0
    
    def match_by_alias(self, alias: str) -> Tuple[Optional[Design], Optional[Build], float]:
        """Match by alias"""
        if not alias:
            return None, None, 0.0
        
        # Try exact alias match
        design = self.db.query(Design).filter(
            Design.alias == alias,
            Design.is_active == True
        ).first()
        
        if design:
            return design, None, 0.7
        
        build = self.db.query(Build).filter(
            Build.alias == alias,
            Build.is_active == True
        ).first()
        
        if build:
            return None, build, 0.7
        
        # Try partial alias match
        alias_pattern = f"%{alias}%"
        
        design = self.db.query(Design).filter(
            Design.alias.ilike(alias_pattern),
            Design.is_active == True
        ).first()
        
        if design:
            return design, None, 0.7
        
        build = self.db.query(Build).filter(
            Build.alias.ilike(alias_pattern),
            Build.is_active == True
        ).first()
        
        if build:
            return None, build, 0.7
        
        return None, None, 0.0
    
    def match_row(self, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """Match a single row of data to existing entities"""
        sequence = row_data.get("sequence", "")
        mutations = self.parse_mutations(row_data.get("mutations", ""))
        alias = row_data.get("alias", "")
        
        # Try sequence match first (highest confidence)
        design, build, score = self.match_by_sequence(sequence)
        if score > 0.9:
            return {
                "matched": True,
                "design_id": design.id if design else None,
                "build_id": build.id if build else None,
                "confidence": "high",
                "method": "sequence",
                "score": score
            }
        
        # Try mutation match
        design, build, score = self.match_by_mutations(mutations)
        if score > 0.5:
            return {
                "matched": True,
                "design_id": design.id if design else None,
                "build_id": build.id if build else None,
                "confidence": "medium",
                "method": "mutation",
                "score": score
            }
        
        # Try alias match
        design, build, score = self.match_by_alias(alias)
        if score > 0.0:
            return {
                "matched": True,
                "design_id": design.id if design else None,
                "build_id": build.id if build else None,
                "confidence": "low",
                "method": "alias",
                "score": score
            }
        
        # No match found
        return {
            "matched": False,
            "design_id": None,
            "build_id": None,
            "confidence": "none",
            "method": "none",
            "score": 0.0
        }
    
    def create_test_from_row(self, row_data: Dict[str, Any], match_result: Dict[str, Any]) -> Test:
        """Create a test entity from row data and match result"""
        test = Test(
            name=row_data.get("name", ""),
            alias=row_data.get("alias", ""),
            description=row_data.get("description", ""),
            test_type=row_data.get("test_type", "activity"),
            result_value=float(row_data.get("result_value", 0)) if row_data.get("result_value") else None,
            result_unit=row_data.get("result_unit", ""),
            assay_name=row_data.get("assay_name", ""),
            technician=row_data.get("technician", ""),
            design_id=match_result.get("design_id"),
            build_id=match_result.get("build_id"),
            match_confidence=match_result.get("confidence", "none"),
            match_method=match_result.get("method", "none"),
            match_score=match_result.get("score", 0.0)
        )
        
        self.db.add(test)
        return test
    
    def process_upload(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process uploaded data and match to existing entities"""
        results = {
            "total_rows": len(df),
            "matched_rows": 0,
            "unmatched_rows": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "matches": [],
            "errors": []
        }
        
        for i, row in enumerate(df):
            try:
                match_result = self.match_row(row)
                
                if match_result["matched"]:
                    results["matched_rows"] += 1
                    
                    # Create test entity
                    test = self.create_test_from_row(row, match_result)
                    
                    # Count by confidence
                    confidence = match_result["confidence"]
                    if confidence == "high":
                        results["high_confidence"] += 1
                    elif confidence == "medium":
                        results["medium_confidence"] += 1
                    elif confidence == "low":
                        results["low_confidence"] += 1
                    
                    results["matches"].append({
                        "row": i + 1,
                        "name": row.get("name", ""),
                        "alias": row.get("alias", ""),
                        "confidence": confidence,
                        "method": match_result["method"],
                        "score": match_result["score"],
                        "test_id": str(test.id)
                    })
                else:
                    results["unmatched_rows"] += 1
                    results["errors"].append({
                        "row": i + 1,
                        "name": row.get("name", ""),
                        "alias": row.get("alias", ""),
                        "error": "No matching entity found"
                    })
                    
            except Exception as e:
                results["unmatched_rows"] += 1
                results["errors"].append({
                    "row": i + 1,
                    "name": row.get("name", ""),
                    "alias": row.get("alias", ""),
                    "error": str(e)
                })
        
        self.db.commit()
        return results
    
    def get_lineage(self, design_id: str) -> Dict[str, Any]:
        """Get lineage information for a design"""
        design = self.db.query(Design).filter(
            Design.id == design_id,
            Design.is_active == True
        ).first()
        
        if not design:
            return {"error": "Design not found"}
        
        builds = self.db.query(Build).filter(
            Build.design_id == design_id,
            Build.is_active == True
        ).all()
        
        tests = self.db.query(Test).filter(
            Test.design_id == design_id,
            Test.is_active == True
        ).all()
        
        return {
            "design": design,
            "builds": builds,
            "tests": tests
        }


def parse_upload_file(file_content: bytes, filename: str) -> List[Dict[str, Any]]:
    """Parse uploaded file content into list of dictionaries"""
    try:
        # Try CSV first
        if filename.lower().endswith('.csv'):
            content = file_content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(content))
            return [dict(row) for row in reader]
        
        # Try Excel (would need openpyxl)
        elif filename.lower().endswith(('.xlsx', '.xls')):
            # For now, return empty list - would need openpyxl
            return []
        
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    
    except Exception as e:
        raise ValueError(f"Error parsing file: {str(e)}") 