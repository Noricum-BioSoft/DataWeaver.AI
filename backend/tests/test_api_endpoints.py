import pytest
import uuid
from models.bio_entities import Design, Build, Test


class TestDesignEndpoints:
    """Test design-related API endpoints"""
    
    def test_create_design(self, client, sample_design_data):
        """Test creating a new design"""
        response = client.post("/api/bio/designs", json=sample_design_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_design_data["name"]
        assert data["sequence"] == sample_design_data["sequence"]
        assert "id" in data
        assert "lineage_hash" in data
    
    def test_get_designs(self, client, db_session):
        """Test getting all designs"""
        # Create test designs
        design1 = Design(
            name="Design 1",
            sequence="MGT...L72F...K",
            lineage_hash="hash1"
        )
        design2 = Design(
            name="Design 2",
            sequence="MGT...R80K...K",
            lineage_hash="hash2"
        )
        db_session.add_all([design1, design2])
        db_session.commit()
        
        response = client.get("/api/bio/designs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Design 1"
        assert data[1]["name"] == "Design 2"
    
    def test_get_designs_with_filter(self, client, db_session):
        """Test getting designs with name filter"""
        design = Design(
            name="Specific Design",
            sequence="MGT...L72F...K",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        response = client.get("/api/bio/designs?name=Specific")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Specific Design"
    
    def test_get_design_by_id(self, client, db_session):
        """Test getting a specific design by ID"""
        design = Design(
            name="Test Design",
            sequence="MGT...L72F...K",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        response = client.get(f"/api/bio/designs/{design.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Design"
        assert data["id"] == str(design.id)
    
    def test_get_nonexistent_design(self, client):
        """Test getting a design that doesn't exist"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/bio/designs/{fake_id}")
        assert response.status_code == 404


class TestBuildEndpoints:
    """Test build-related API endpoints"""
    
    def test_create_build(self, client, db_session, sample_build_data):
        """Test creating a new build"""
        # First create a design
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        # Update build data with design ID
        sample_build_data["design_id"] = str(design.id)
        
        response = client.post("/api/bio/builds", json=sample_build_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_build_data["name"]
        assert data["design_id"] == str(design.id)
        assert "id" in data
        assert "lineage_hash" in data
    
    def test_get_builds(self, client, db_session):
        """Test getting all builds"""
        # Create design and builds
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        build1 = Build(
            name="Build 1",
            sequence="MGT...L72F...K",
            design_id=design.id,
            lineage_hash="hash1"
        )
        build2 = Build(
            name="Build 2",
            sequence="MGT...R80K...K",
            design_id=design.id,
            lineage_hash="hash2"
        )
        db_session.add_all([build1, build2])
        db_session.commit()
        
        response = client.get("/api/bio/builds")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Build 1"
        assert data[1]["name"] == "Build 2"
    
    def test_get_builds_by_design(self, client, db_session):
        """Test getting builds filtered by design ID"""
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        build = Build(
            name="Test Build",
            sequence="MGT...L72F...K",
            design_id=design.id,
            lineage_hash="hash1"
        )
        db_session.add(build)
        db_session.commit()
        
        response = client.get(f"/api/bio/builds?design_id={design.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Build"
    
    def test_get_build_by_id(self, client, db_session):
        """Test getting a specific build by ID"""
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        build = Build(
            name="Test Build",
            sequence="MGT...L72F...K",
            design_id=design.id,
            lineage_hash="hash1"
        )
        db_session.add(build)
        db_session.commit()
        
        response = client.get(f"/api/bio/builds/{build.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Build"
        assert data["id"] == str(build.id)


class TestTestEndpoints:
    """Test test-related API endpoints"""
    
    def test_get_tests(self, client, db_session):
        """Test getting all tests"""
        # Create design, build, and test
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        build = Build(
            name="Test Build",
            sequence="MGT...L72F...K",
            design_id=design.id,
            lineage_hash="hash1"
        )
        db_session.add(build)
        db_session.commit()
        
        test = Test(
            name="Test Activity",
            test_type="activity",
            result_value=25.0,
            design_id=design.id,
            build_id=build.id
        )
        db_session.add(test)
        db_session.commit()
        
        response = client.get("/api/bio/tests")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Activity"
        assert data[0]["result_value"] == 25.0
    
    def test_get_tests_by_design(self, client, db_session):
        """Test getting tests filtered by design ID"""
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        test = Test(
            name="Test Activity",
            test_type="activity",
            result_value=25.0,
            design_id=design.id
        )
        db_session.add(test)
        db_session.commit()
        
        response = client.get(f"/api/bio/tests?design_id={design.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Activity"
    
    def test_get_test_by_id(self, client, db_session):
        """Test getting a specific test by ID"""
        test = Test(
            name="Test Activity",
            test_type="activity",
            result_value=25.0
        )
        db_session.add(test)
        db_session.commit()
        
        response = client.get(f"/api/bio/tests/{test.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Activity"
        assert data["id"] == str(test.id)


class TestUploadEndpoints:
    """Test upload-related API endpoints"""
    
    def test_upload_test_results(self, client, db_session, temp_csv_file):
        """Test uploading test results file"""
        # Create a design to match against
        design = Design(
            name="Clone_7",
            alias="Clone_7",
            sequence="MGT...L72F...K",
            mutation_list="L72F",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        # Upload CSV file
        with open(temp_csv_file, "rb") as f:
            response = client.post(
                "/api/bio/upload-test-results",
                files={"file": ("test.csv", f, "text/csv")},
                data={"test_type": "activity"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_rows"] == 3
        assert data["matched_rows"] >= 1  # At least Clone_7 should match
        assert "matches" in data
        assert "errors" in data
    
    def test_match_preview(self, client, db_session, temp_csv_file):
        """Test match preview without committing"""
        # Create a design to match against
        design = Design(
            name="Clone_7",
            alias="Clone_7",
            sequence="MGT...L72F...K",
            mutation_list="L72F",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        # Preview matching
        with open(temp_csv_file, "rb") as f:
            response = client.post(
                "/api/bio/match-preview",
                files={"file": ("test.csv", f, "text/csv")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_rows"] == 3
        assert data["matched_rows"] >= 1
        assert "matches" in data
        assert "errors" in data
        
        # Verify no tests were actually created (preview mode)
        tests = db_session.query(Test).all()
        assert len(tests) == 0
    
    def test_upload_invalid_file(self, client):
        """Test uploading invalid file"""
        response = client.post(
            "/api/bio/upload-test-results",
            files={"file": ("test.txt", b"invalid content", "text/plain")}
        )
        assert response.status_code == 400


class TestLineageEndpoints:
    """Test lineage-related API endpoints"""
    
    def test_get_lineage(self, client, db_session):
        """Test getting complete lineage for a design"""
        # Create design with builds and tests
        design = Design(
            name="Parent Design",
            sequence="MGT...L72F...K",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        build = Build(
            name="Test Build",
            sequence="MGT...L72F...K",
            design_id=design.id,
            lineage_hash="hash1"
        )
        db_session.add(build)
        db_session.commit()
        
        test = Test(
            name="Test Activity",
            test_type="activity",
            result_value=25.0,
            design_id=design.id,
            build_id=build.id
        )
        db_session.add(test)
        db_session.commit()
        
        response = client.get(f"/api/bio/lineage/{design.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["design"]["name"] == "Parent Design"
        assert len(data["builds"]) == 1
        assert len(data["tests"]) == 1
        assert data["builds"][0]["name"] == "Test Build"
        assert data["tests"][0]["name"] == "Test Activity"
    
    def test_get_nonexistent_lineage(self, client):
        """Test getting lineage for non-existent design"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/bio/lineage/{fake_id}")
        assert response.status_code == 404


class TestStatsEndpoints:
    """Test statistics endpoints"""
    
    def test_get_bio_stats(self, client, db_session):
        """Test getting biological entity statistics"""
        # Create some test data
        design = Design(
            name="Test Design",
            sequence="MGT...L72F...K",
            lineage_hash="hash1"
        )
        db_session.add(design)
        db_session.commit()
        
        build = Build(
            name="Test Build",
            sequence="MGT...L72F...K",
            design_id=design.id,
            lineage_hash="hash1"
        )
        db_session.add(build)
        db_session.commit()
        
        test = Test(
            name="Test Activity",
            test_type="activity",
            result_value=25.0,
            design_id=design.id,
            build_id=build.id,
            match_confidence="high"
        )
        db_session.add(test)
        db_session.commit()
        
        response = client.get("/api/bio/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_designs"] == 1
        assert data["total_builds"] == 1
        assert data["total_tests"] == 1
        assert data["high_confidence_matches"] == 1 