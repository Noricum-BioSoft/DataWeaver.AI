import pytest
import uuid
from datetime import datetime
from models.bio_entities import Design, Build, Test


class TestDesignModel:
    """Test the Design model"""
    
    def test_create_design(self, db_session):
        """Test creating a basic design"""
        design = Design(
            name="Test Design",
            alias="TEST_DESIGN",
            description="A test design",
            sequence="MGT...L72F...K",
            sequence_type="protein",
            mutation_list="L72F"
        )
        db_session.add(design)
        db_session.commit()
        
        # Verify the design was created
        assert design.id is not None
        assert design.name == "Test Design"
        assert design.alias == "TEST_DESIGN"
        assert design.sequence == "MGT...L72F...K"
        assert design.mutation_list == "L72F"
        assert design.lineage_hash is not None  # Auto-computed
        assert design.created_at is not None
        assert design.updated_at is None  # Only set on updates
    
    def test_design_defaults(self, db_session):
        """Test design model defaults"""
        design = Design(
            name="Test Design",
            sequence="MGT...L72F...K"
        )
        db_session.add(design)
        db_session.commit()
        
        # Check defaults
        assert design.alias is None
        assert design.description is None
        assert design.sequence_type == "protein"
        assert design.mutation_list is None  # Defaults to None, not empty string
        assert design.parent_design_id is None
        assert design.lineage_hash is not None  # Should be auto-generated
    
    def test_design_relationships(self, db_session):
        """Test design relationships"""
        # Create parent design
        parent = Design(
            name="Parent Design",
            sequence="MGT...L72...K"
        )
        db_session.add(parent)
        db_session.commit()
        
        # Create child design
        child = Design(
            name="Child Design",
            sequence="MGT...L72F...K",
            mutation_list="L72F",
            parent_design_id=parent.id
        )
        db_session.add(child)
        db_session.commit()
        
        # Verify relationships
        assert child.parent_design_id == parent.id
        
        # Test that we can access parent (if relationship is defined)
        # This depends on whether we've set up SQLAlchemy relationships
        if hasattr(child, 'parent_design'):
            assert child.parent_design.id == parent.id
    
    def test_design_validation(self, db_session):
        """Test design validation"""
        # Test required fields
        with pytest.raises(Exception):  # SQLAlchemy will raise an error
            design = Design()  # Missing required fields
            db_session.add(design)
            db_session.commit()
    
    def test_design_timestamps(self, db_session):
        """Test that timestamps are automatically set"""
        design = Design(
            name="Test Design",
            sequence="MGT...L72F...K"
        )
        db_session.add(design)
        db_session.commit()
        
        # Check that timestamps are set
        assert design.created_at is not None
        assert design.updated_at is None  # Only set on updates
        
        # Store original timestamps
        original_created = design.created_at
        
        # Update the design
        design.name = "Updated Design"
        db_session.commit()
        
        # Check that created_at didn't change but updated_at did
        assert design.created_at == original_created
        assert design.updated_at is not None  # Should be set after update


class TestBuildModel:
    """Test the Build model"""
    
    def test_create_build(self, db_session):
        """Test creating a basic build"""
        # First create a design
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K"
        )
        db_session.add(design)
        db_session.commit()
        
        build = Build(
            name="Test Build",
            alias="TEST_BUILD",
            description="A test build",
            sequence="MGT...L72F...K",
            sequence_type="protein",
            mutation_list="L72F",
            design_id=design.id,
            construct_type="plasmid",
            build_status="completed"
        )
        db_session.add(build)
        db_session.commit()
        
        # Verify the build was created
        assert build.id is not None
        assert build.name == "Test Build"
        assert build.alias == "TEST_BUILD"
        assert build.sequence == "MGT...L72F...K"
        assert build.design_id == design.id
        assert build.construct_type == "plasmid"
        assert build.build_status == "completed"
        assert build.lineage_hash is not None  # Auto-computed
    
    def test_build_defaults(self, db_session):
        """Test build model defaults"""
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K"
        )
        db_session.add(design)
        db_session.commit()
        
        build = Build(
            name="Test Build",
            sequence="MGT...L72F...K",
            design_id=design.id
        )
        db_session.add(build)
        db_session.commit()
        
        # Check defaults
        assert build.alias is None
        assert build.description is None
        assert build.sequence_type == "protein"
        assert build.mutation_list is None  # Defaults to None, not empty string
        assert build.parent_build_id is None
        assert build.construct_type == "plasmid"
        assert build.build_status == "planned"  # Default status
        assert build.lineage_hash is not None
    
    def test_build_relationships(self, db_session):
        """Test build relationships"""
        # Create design
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K"
        )
        db_session.add(design)
        db_session.commit()
        
        # Create parent build
        parent_build = Build(
            name="Parent Build",
            sequence="MGT...L72F...K",
            design_id=design.id
        )
        db_session.add(parent_build)
        db_session.commit()
        
        # Create child build
        child_build = Build(
            name="Child Build",
            sequence="MGT...L72F...K",
            design_id=design.id,
            parent_build_id=parent_build.id
        )
        db_session.add(child_build)
        db_session.commit()
        
        # Verify relationships
        assert child_build.design_id == design.id
        assert child_build.parent_build_id == parent_build.id
    
    def test_build_status_enum(self, db_session):
        """Test build status enum values"""
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K"
        )
        db_session.add(design)
        db_session.commit()
        
        # Test valid status values
        valid_statuses = ["in_progress", "completed", "failed", "cancelled"]
        
        for status in valid_statuses:
            build = Build(
                name=f"Build {status}",
                sequence="MGT...L72F...K",
                design_id=design.id,
                build_status=status
            )
            db_session.add(build)
            db_session.commit()
            
            # Verify status was set correctly
            assert build.build_status == status


class TestTestModel:
    """Test the Test model"""
    
    def test_create_test(self, db_session):
        """Test creating a basic test"""
        # Create design and build
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K"
        )
        db_session.add(design)
        db_session.commit()
        
        build = Build(
            name="Test Build",
            sequence="MGT...L72F...K",
            design_id=design.id
        )
        db_session.add(build)
        db_session.commit()
        
        test = Test(
            name="Test Activity",
            alias="TEST_ACTIVITY",
            description="A test activity measurement",
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
        
        # Verify the test was created
        assert test.id is not None
        assert test.name == "Test Activity"
        assert test.alias == "TEST_ACTIVITY"
        assert test.test_type == "activity"
        assert test.result_value == 25.0
        assert test.result_unit == "μM/min"
        assert test.assay_name == "Enzyme Activity Assay"
        assert test.technician == "Dr. Smith"
        assert test.design_id == design.id
        assert test.build_id == build.id
        assert test.match_confidence == "high"
        assert test.match_method == "sequence"
        assert test.match_score == 1.0
    
    def test_test_defaults(self, db_session):
        """Test test model defaults"""
        test = Test(
            name="Test Activity",
            test_type="activity",
            result_value=25.0
        )
        db_session.add(test)
        db_session.commit()
        
        # Check defaults
        assert test.alias is None
        assert test.description is None
        assert test.result_unit is None  # Defaults to None, not empty string
        assert test.assay_name is None
        assert test.technician is None
        assert test.design_id is None
        assert test.build_id is None
        assert test.match_confidence == "none"
        assert test.match_method == "none"
        assert test.match_score == 0.0
    
    def test_test_relationships(self, db_session):
        """Test test relationships"""
        # Create design and build
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K"
        )
        db_session.add(design)
        db_session.commit()
        
        build = Build(
            name="Test Build",
            sequence="MGT...L72F...K",
            design_id=design.id
        )
        db_session.add(build)
        db_session.commit()
        
        # Create test with both design and build
        test = Test(
            name="Test Activity",
            test_type="activity",
            result_value=25.0,
            design_id=design.id,
            build_id=build.id
        )
        db_session.add(test)
        db_session.commit()
        
        # Verify relationships
        assert test.design_id == design.id
        assert test.build_id == build.id
        
        # Create test with only design (no build)
        test_no_build = Test(
            name="Test Activity 2",
            test_type="activity",
            result_value=30.0,
            design_id=design.id
        )
        db_session.add(test_no_build)
        db_session.commit()
        
        assert test_no_build.design_id == design.id
        assert test_no_build.build_id is None
    
    def test_test_confidence_enum(self, db_session):
        """Test test confidence enum values"""
        valid_confidences = ["none", "low", "medium", "high"]
        
        for confidence in valid_confidences:
            test = Test(
                name=f"Test {confidence}",
                test_type="activity",
                result_value=25.0,
                match_confidence=confidence
            )
            db_session.add(test)
            db_session.commit()
            
            # Verify confidence was set correctly
            assert test.match_confidence == confidence
    
    def test_test_method_enum(self, db_session):
        """Test test method enum values"""
        valid_methods = ["none", "sequence", "mutation", "alias"]
        
        for method in valid_methods:
            test = Test(
                name=f"Test {method}",
                test_type="activity",
                result_value=25.0,
                match_method=method
            )
            db_session.add(test)
            db_session.commit()
            
            # Verify method was set correctly
            assert test.match_method == method


class TestModelRelationships:
    """Test relationships between models"""
    
    def test_design_build_relationship(self, db_session):
        """Test design-build relationship"""
        # Create design
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K"
        )
        db_session.add(design)
        db_session.commit()
        
        # Create multiple builds for the design
        build1 = Build(
            name="Build 1",
            sequence="MGT...L72F...K",
            design_id=design.id
        )
        build2 = Build(
            name="Build 2",
            sequence="MGT...L72F...K",
            design_id=design.id
        )
        db_session.add_all([build1, build2])
        db_session.commit()
        
        # Verify all builds belong to the same design
        assert build1.design_id == design.id
        assert build2.design_id == design.id
    
    def test_design_test_relationship(self, db_session):
        """Test design-test relationship"""
        # Create design
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K"
        )
        db_session.add(design)
        db_session.commit()
        
        # Create multiple tests for the design
        test1 = Test(
            name="Test 1",
            test_type="activity",
            result_value=25.0,
            design_id=design.id
        )
        test2 = Test(
            name="Test 2",
            test_type="stability",
            result_value=0.95,
            design_id=design.id
        )
        db_session.add_all([test1, test2])
        db_session.commit()
        
        # Verify all tests belong to the same design
        assert test1.design_id == design.id
        assert test2.design_id == design.id
    
    def test_build_test_relationship(self, db_session):
        """Test build-test relationship"""
        # Create design and build
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K"
        )
        db_session.add(design)
        db_session.commit()
        
        build = Build(
            name="Test Build",
            sequence="MGT...L72F...K",
            design_id=design.id
        )
        db_session.add(build)
        db_session.commit()
        
        # Create multiple tests for the build
        test1 = Test(
            name="Test 1",
            test_type="activity",
            result_value=25.0,
            design_id=design.id,
            build_id=build.id
        )
        test2 = Test(
            name="Test 2",
            test_type="stability",
            result_value=0.95,
            design_id=design.id,
            build_id=build.id
        )
        db_session.add_all([test1, test2])
        db_session.commit()
        
        # Verify all tests belong to the same build
        assert test1.build_id == build.id
        assert test2.build_id == build.id
        assert test1.design_id == design.id
        assert test2.design_id == design.id 