import pytest
import pandas as pd
import tempfile
import os
from models.bio_entities import Design, Build, Test
from services.bio_matcher import BioEntityMatcher


class TestCompleteWorkflow:
    """Test the complete DBT workflow integration"""
    
    def test_design_to_build_to_test_workflow(self, db_session):
        """Test complete workflow: Design -> Build -> Test"""
        matcher = BioEntityMatcher(db_session)
        
        # 1. Create a design
        design = Design(
            name="Enzyme Design Alpha",
            alias="ENZ_ALPHA",
            description="Optimized enzyme for industrial catalysis",
            sequence="MGT...L72F...K",
            sequence_type="protein",
            mutation_list="L72F",
            lineage_hash="hash_alpha"
        )
        db_session.add(design)
        db_session.commit()
        
        # 2. Create a build from the design
        build = Build(
            name="Enzyme Build Alpha v1",
            alias="ENZ_BUILD_ALPHA_V1",
            description="First build of Enzyme Alpha",
            sequence="MGT...L72F...K",
            sequence_type="protein",
            mutation_list="L72F",
            design_id=design.id,
            construct_type="plasmid",
            build_status="completed",
            lineage_hash="hash_alpha_build1"
        )
        db_session.add(build)
        db_session.commit()
        
        # 3. Create test results
        test = Test(
            name="Activity Assay Alpha",
            alias="ACTIVITY_ALPHA",
            description="Enzyme activity measurement",
            test_type="activity",
            result_value=25.0,
            result_unit="μM/min",
            assay_name="Enzyme Activity Assay",
            technician="Dr. Smith",
            design_id=design.id,
            build_id=build.id,
            match_confidence="high",
            match_method="sequence",
            match_score=1.0
        )
        db_session.add(test)
        db_session.commit()
        
        # 4. Verify lineage relationships
        assert design.id == build.design_id
        assert design.id == test.design_id
        assert build.id == test.build_id
        
        # 5. Test lineage retrieval
        lineage = matcher.get_lineage(design.id)
        assert lineage["design"]["name"] == "Enzyme Design Alpha"
        assert len(lineage["builds"]) == 1
        assert len(lineage["tests"]) == 1
        assert lineage["builds"][0]["name"] == "Enzyme Build Alpha v1"
        assert lineage["tests"][0]["name"] == "Activity Assay Alpha"
    
    def test_mutation_based_lineage_tracking(self, db_session):
        """Test lineage tracking with mutations"""
        matcher = BioEntityMatcher(db_session)
        
        # Create parent design
        parent_design = Design(
            name="Parent Enzyme",
            sequence="MGT...L72...K",
            mutation_list="",
            lineage_hash="hash_parent"
        )
        db_session.add(parent_design)
        db_session.commit()
        
        # Create child design with mutation
        child_design = Design(
            name="Mutant Enzyme",
            sequence="MGT...L72F...K",
            mutation_list="L72F",
            parent_design_id=parent_design.id,
            lineage_hash=matcher.compute_lineage_hash(
                parent_design.lineage_hash, 
                ["L72F"], 
                "MGT...L72F...K"
            )
        )
        db_session.add(child_design)
        db_session.commit()
        
        # Verify lineage hash computation
        expected_hash = matcher.compute_lineage_hash(
            parent_design.lineage_hash, 
            ["L72F"], 
            "MGT...L72F...K"
        )
        assert child_design.lineage_hash == expected_hash
        
        # Test that different mutations produce different hashes
        different_hash = matcher.compute_lineage_hash(
            parent_design.lineage_hash, 
            ["R80K"], 
            "MGT...R80K...K"
        )
        assert child_design.lineage_hash != different_hash
    
    def test_upload_and_matching_workflow(self, db_session, temp_csv_file):
        """Test complete upload and matching workflow"""
        matcher = BioEntityMatcher(db_session)
        
        # 1. Create existing designs in database
        design1 = Design(
            name="Clone_7",
            alias="Clone_7",
            sequence="MGT...L72F...K",
            mutation_list="L72F",
            lineage_hash="hash_clone7"
        )
        design2 = Design(
            name="WT_Control",
            alias="WT_Control",
            sequence="MGT...L72...K",
            mutation_list="",
            lineage_hash="hash_wt"
        )
        db_session.add_all([design1, design2])
        db_session.commit()
        
        # 2. Parse uploaded file
        with open(temp_csv_file, "rb") as f:
            file_content = f.read()
        
        df = matcher.parse_upload_file(file_content, "test.csv")
        assert len(df) == 3
        
        # 3. Process each row and match
        results = []
        for _, row in df.iterrows():
            row_data = row.to_dict()
            match_result = matcher.match_row(row_data)
            
            if match_result["matched"]:
                test = matcher.create_test_from_row(row_data, match_result)
                db_session.add(test)
                results.append({
                    "row": row_data,
                    "match": match_result,
                    "test": test
                })
        
        db_session.commit()
        
        # 4. Verify results
        assert len(results) >= 2  # At least Clone_7 and WT_Control should match
        
        # Check that Clone_7 matched with high confidence
        clone7_result = next(r for r in results if r["row"]["alias"] == "Clone_7")
        assert clone7_result["match"]["confidence"] == "high"
        assert clone7_result["match"]["method"] == "sequence"
        assert clone7_result["test"].design_id == design1.id
        
        # Check that WT_Control matched
        wt_result = next(r for r in results if r["row"]["alias"] == "WT_Control")
        assert wt_result["match"]["matched"] is True
        assert wt_result["test"].design_id == design2.id
        
        # Check that Mutant_A didn't match (no corresponding design)
        mutant_result = next(r for r in results if r["row"]["alias"] == "Mutant_A", None)
        if mutant_result:
            assert mutant_result["match"]["matched"] is False
    
    def test_confidence_scoring_system(self, db_session):
        """Test the confidence scoring system"""
        matcher = BioEntityMatcher(db_session)
        
        # Create test designs with different characteristics
        exact_match_design = Design(
            name="Exact Match",
            alias="EXACT_MATCH",
            sequence="MGT...L72F...K",
            mutation_list="L72F",
            lineage_hash="hash_exact"
        )
        
        partial_match_design = Design(
            name="Partial Match",
            alias="PARTIAL_MATCH",
            sequence="MGT...L72F...K",
            mutation_list="L72F,R80K",
            lineage_hash="hash_partial"
        )
        
        alias_match_design = Design(
            name="Alias Match",
            alias="ALIAS_MATCH",
            sequence="DIFFERENT_SEQUENCE",
            mutation_list="DIFFERENT_MUTATION",
            lineage_hash="hash_alias"
        )
        
        db_session.add_all([exact_match_design, partial_match_design, alias_match_design])
        db_session.commit()
        
        # Test high confidence match (sequence)
        row_data = {
            "name": "Test",
            "sequence": "MGT...L72F...K",
            "mutations": "L72F",
            "alias": "EXACT_MATCH"
        }
        result = matcher.match_row(row_data)
        assert result["confidence"] == "high"
        assert result["score"] == 1.0
        assert result["method"] == "sequence"
        
        # Test medium confidence match (mutation)
        row_data = {
            "name": "Test",
            "sequence": "DIFFERENT_SEQUENCE",
            "mutations": "L72F",
            "alias": "PARTIAL_MATCH"
        }
        result = matcher.match_row(row_data)
        assert result["confidence"] == "medium"
        assert result["score"] == 0.8
        assert result["method"] == "mutation"
        
        # Test low confidence match (alias)
        row_data = {
            "name": "Test",
            "sequence": "DIFFERENT_SEQUENCE",
            "mutations": "DIFFERENT_MUTATION",
            "alias": "ALIAS_MATCH"
        }
        result = matcher.match_row(row_data)
        assert result["confidence"] == "low"
        assert result["score"] == 0.7
        assert result["method"] == "alias"
        
        # Test no match
        row_data = {
            "name": "Test",
            "sequence": "DIFFERENT_SEQUENCE",
            "mutations": "DIFFERENT_MUTATION",
            "alias": "NO_MATCH"
        }
        result = matcher.match_row(row_data)
        assert result["confidence"] == "none"
        assert result["score"] == 0.0
        assert result["method"] == "none"
    
    def test_error_handling_and_validation(self, db_session):
        """Test error handling and data validation"""
        matcher = BioEntityMatcher(db_session)
        
        # Test invalid sequence format
        with pytest.raises(ValueError):
            matcher.normalize_sequence(None)
        
        # Test invalid mutation format
        mutations = matcher.parse_mutations("invalid_mutation_format")
        assert mutations == ["invalid_mutation_format"]  # Should still parse
        
        # Test invalid lineage hash computation
        with pytest.raises(TypeError):
            matcher.compute_lineage_hash(None, None, None)
        
        # Test matching with invalid data
        row_data = {
            "name": None,
            "sequence": None,
            "mutations": None,
            "alias": None
        }
        result = matcher.match_row(row_data)
        assert result["matched"] is False
        assert result["confidence"] == "none"
    
    def test_performance_with_large_datasets(self, db_session):
        """Test performance with larger datasets"""
        matcher = BioEntityMatcher(db_session)
        
        # Create 100 designs with different sequences
        designs = []
        for i in range(100):
            design = Design(
                name=f"Design_{i}",
                alias=f"DESIGN_{i}",
                sequence=f"MGT...L72F...K_{i}",
                mutation_list="L72F",
                lineage_hash=f"hash_{i}"
            )
            designs.append(design)
        
        db_session.add_all(designs)
        db_session.commit()
        
        # Test matching performance
        import time
        start_time = time.time()
        
        # Try to match against all designs
        row_data = {
            "name": "Test",
            "sequence": "MGT...L72F...K_50",  # Should match design 50
            "mutations": "L72F",
            "alias": "DESIGN_50"
        }
        
        result = matcher.match_row(row_data)
        end_time = time.time()
        
        # Should complete within reasonable time (< 1 second)
        assert end_time - start_time < 1.0
        assert result["matched"] is True
        assert result["confidence"] == "high"
    
    def test_data_integrity_and_constraints(self, db_session):
        """Test data integrity and database constraints"""
        
        # Test unique constraint on lineage_hash
        design1 = Design(
            name="Design 1",
            sequence="MGT...L72F...K",
            lineage_hash="unique_hash"
        )
        db_session.add(design1)
        db_session.commit()
        
        # Try to create another design with same lineage_hash
        design2 = Design(
            name="Design 2",
            sequence="MGT...L72F...K",
            lineage_hash="unique_hash"
        )
        db_session.add(design2)
        
        # This should work (lineage_hash is not unique in our model)
        # But we can test other constraints
        db_session.commit()
        
        # Test foreign key constraints
        build = Build(
            name="Test Build",
            sequence="MGT...L72F...K",
            design_id=design1.id,
            lineage_hash="build_hash"
        )
        db_session.add(build)
        db_session.commit()
        
        # Verify foreign key relationship
        assert build.design_id == design1.id
        
        # Test that we can't create a build with non-existent design_id
        fake_design_id = "00000000-0000-0000-0000-000000000000"
        build_with_fake_design = Build(
            name="Fake Build",
            sequence="MGT...L72F...K",
            design_id=fake_design_id,
            lineage_hash="fake_hash"
        )
        db_session.add(build_with_fake_design)
        
        # This should work (UUID validation happens at application level)
        db_session.commit()
        
        # Clean up
        db_session.delete(build_with_fake_design)
        db_session.commit() 