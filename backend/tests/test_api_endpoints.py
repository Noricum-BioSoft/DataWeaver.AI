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
    
    def test_get_designs(self, client):
        """Test getting all designs"""
        # Create test designs via API
        design1_data = {
            "name": "Design 1",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        design2_data = {
            "name": "Design 2", 
            "sequence": "MGT...R80K...K",
            "sequence_type": "protein",
            "mutation_list": "R80K"
        }
        
        # Create designs via API
        response1 = client.post("/api/bio/designs", json=design1_data)
        response2 = client.post("/api/bio/designs", json=design2_data)
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Get all designs
        response = client.get("/api/bio/designs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Design 1"
        assert data[1]["name"] == "Design 2"
    
    def test_get_designs_with_filter(self, client):
        """Test getting designs with name filter"""
        # Create design via API
        design_data = {
            "name": "Specific Design",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        response = client.post("/api/bio/designs", json=design_data)
        assert response.status_code == 200
        
        # Get designs with filter
        response = client.get("/api/bio/designs?name=Specific")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Specific Design"
    
    def test_get_design_by_id(self, client):
        """Test getting a specific design by ID"""
        # Create design via API
        design_data = {
            "name": "Test Design",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        create_response = client.post("/api/bio/designs", json=design_data)
        assert create_response.status_code == 200
        created_design = create_response.json()
        
        # Get design by ID
        response = client.get(f"/api/bio/designs/{created_design['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Design"
        assert data["id"] == created_design["id"]
    
    def test_get_nonexistent_design(self, client):
        """Test getting a design that doesn't exist"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/bio/designs/{fake_id}")
        assert response.status_code == 404


class TestBuildEndpoints:
    """Test build-related API endpoints"""
    
    def test_create_build(self, client, sample_build_data):
        """Test creating a new build"""
        # First create a design
        design_data = {
            "name": "Parent Design",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        design_response = client.post("/api/bio/designs", json=design_data)
        assert design_response.status_code == 200
        design = design_response.json()
        
        # Update build data with design ID
        sample_build_data["design_id"] = design["id"]
        
        response = client.post("/api/bio/builds", json=sample_build_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_build_data["name"]
        assert data["design_id"] == design["id"]
        assert "id" in data
        assert "lineage_hash" in data
    
    def test_get_builds(self, client):
        """Test getting all builds"""
        # Create design via API
        design_data = {
            "name": "Parent Design",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        design_response = client.post("/api/bio/designs", json=design_data)
        assert design_response.status_code == 200
        design = design_response.json()
        
        # Create builds via API
        build1_data = {
            "name": "Build 1",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F",
            "design_id": design["id"],
            "construct_type": "plasmid",
            "build_status": "completed"
        }
        build2_data = {
            "name": "Build 2",
            "sequence": "MGT...R80K...K",
            "sequence_type": "protein",
            "mutation_list": "R80K",
            "design_id": design["id"],
            "construct_type": "plasmid",
            "build_status": "completed"
        }
        
        build1_response = client.post("/api/bio/builds", json=build1_data)
        build2_response = client.post("/api/bio/builds", json=build2_data)
        assert build1_response.status_code == 200
        assert build2_response.status_code == 200
        
        # Get all builds
        response = client.get("/api/bio/builds")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Build 1"
        assert data[1]["name"] == "Build 2"
    
    def test_get_builds_by_design(self, client):
        """Test getting builds filtered by design ID"""
        # Create design via API
        design_data = {
            "name": "Parent Design",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        design_response = client.post("/api/bio/designs", json=design_data)
        assert design_response.status_code == 200
        design = design_response.json()
        
        # Create build via API
        build_data = {
            "name": "Test Build",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F",
            "design_id": design["id"],
            "construct_type": "plasmid",
            "build_status": "completed"
        }
        
        build_response = client.post("/api/bio/builds", json=build_data)
        assert build_response.status_code == 200
        
        # Get builds by design
        response = client.get(f"/api/bio/builds?design_id={design['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Build"
    
    def test_get_build_by_id(self, client):
        """Test getting a specific build by ID"""
        # Create design via API
        design_data = {
            "name": "Parent Design",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        design_response = client.post("/api/bio/designs", json=design_data)
        assert design_response.status_code == 200
        design = design_response.json()
        
        # Create build via API
        build_data = {
            "name": "Test Build",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F",
            "design_id": design["id"],
            "construct_type": "plasmid",
            "build_status": "completed"
        }
        
        build_response = client.post("/api/bio/builds", json=build_data)
        assert build_response.status_code == 200
        build = build_response.json()
        
        # Get build by ID
        response = client.get(f"/api/bio/builds/{build['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Build"
        assert data["id"] == build["id"]


class TestTestEndpoints:
    """Test test-related API endpoints"""
    
    def test_get_tests(self, client):
        """Test getting all tests"""
        # Create design via API
        design_data = {
            "name": "Parent Design",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        design_response = client.post("/api/bio/designs", json=design_data)
        assert design_response.status_code == 200
        design = design_response.json()
        
        # Create build via API
        build_data = {
            "name": "Test Build",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F",
            "design_id": design["id"],
            "construct_type": "plasmid",
            "build_status": "completed"
        }
        
        build_response = client.post("/api/bio/builds", json=build_data)
        assert build_response.status_code == 200
        build = build_response.json()
        
        # Create test via API
        test_data = {
            "name": "Test Activity",
            "test_type": "activity",
            "result_value": 25.0,
            "result_unit": "μM/min",
            "design_id": design["id"],
            "build_id": build["id"],
            "assay_name": "Enzyme Activity Assay",
            "technician": "Dr. Smith"
        }
        
        test_response = client.post("/api/bio/tests", json=test_data)
        assert test_response.status_code == 200
        
        # Get all tests
        response = client.get("/api/bio/tests")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Activity"
    
    def test_get_tests_by_design(self, client):
        """Test getting tests filtered by design ID"""
        # Create design via API
        design_data = {
            "name": "Parent Design",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        design_response = client.post("/api/bio/designs", json=design_data)
        assert design_response.status_code == 200
        design = design_response.json()
        
        # Create test via API
        test_data = {
            "name": "Test Activity",
            "test_type": "activity",
            "result_value": 25.0,
            "result_unit": "μM/min",
            "design_id": design["id"],
            "assay_name": "Enzyme Activity Assay",
            "technician": "Dr. Smith"
        }
        
        test_response = client.post("/api/bio/tests", json=test_data)
        assert test_response.status_code == 200
        
        # Get tests by design
        response = client.get(f"/api/bio/tests?design_id={design['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Activity"
    
    def test_get_test_by_id(self, client):
        """Test getting a specific test by ID"""
        # Create design via API
        design_data = {
            "name": "Parent Design",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        design_response = client.post("/api/bio/designs", json=design_data)
        assert design_response.status_code == 200
        design = design_response.json()
        
        # Create test via API
        test_data = {
            "name": "Test Activity",
            "test_type": "activity",
            "result_value": 25.0,
            "result_unit": "μM/min",
            "design_id": design["id"],
            "assay_name": "Enzyme Activity Assay",
            "technician": "Dr. Smith"
        }
        
        test_response = client.post("/api/bio/tests", json=test_data)
        assert test_response.status_code == 200
        test = test_response.json()
        
        # Get test by ID
        response = client.get(f"/api/bio/tests/{test['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Activity"
        assert data["id"] == test["id"]


class TestUploadEndpoints:
    """Test upload-related API endpoints"""
    
    def test_upload_test_results(self, client, temp_csv_file):
        """Test uploading test results file"""
        # Create a design to match against via API
        design_data = {
            "name": "Clone_7",
            "alias": "Clone_7",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        design_response = client.post("/api/bio/designs", json=design_data)
        assert design_response.status_code == 200
        
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
    
    def test_match_preview(self, client, temp_csv_file):
        """Test match preview without committing"""
        # Create a design to match against via API
        design_data = {
            "name": "Clone_7",
            "alias": "Clone_7",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        design_response = client.post("/api/bio/designs", json=design_data)
        assert design_response.status_code == 200
        
        # Preview matching
        with open(temp_csv_file, "rb") as f:
            response = client.post(
                "/api/bio/match-preview",
                files={"file": ("test.csv", f, "text/csv")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert "errors" in data
    
    def test_upload_invalid_file(self, client):
        """Test uploading invalid file"""
        response = client.post(
            "/api/bio/upload-test-results",
            files={"file": ("test.txt", b"invalid content", "text/plain")}
        )
        assert response.status_code == 400


class TestLineageEndpoints:
    """Test lineage-related API endpoints"""
    
    def test_get_lineage(self, client):
        """Test getting lineage information"""
        # Create design via API
        design_data = {
            "name": "Parent Design",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        design_response = client.post("/api/bio/designs", json=design_data)
        assert design_response.status_code == 200
        design = design_response.json()
        
        # Create build via API
        build_data = {
            "name": "Test Build",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F",
            "design_id": design["id"],
            "construct_type": "plasmid",
            "build_status": "completed"
        }
        
        build_response = client.post("/api/bio/builds", json=build_data)
        assert build_response.status_code == 200
        
        # Create test via API
        test_data = {
            "name": "Test Activity",
            "test_type": "activity",
            "result_value": 25.0,
            "result_unit": "μM/min",
            "design_id": design["id"],
            "assay_name": "Enzyme Activity Assay",
            "technician": "Dr. Smith"
        }
        
        test_response = client.post("/api/bio/tests", json=test_data)
        assert test_response.status_code == 200
        
        # Get lineage
        response = client.get(f"/api/bio/lineage/{design['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["design"]["name"] == "Parent Design"
        assert len(data["builds"]) == 1
        assert len(data["tests"]) == 1
    
    def test_get_nonexistent_lineage(self, client):
        """Test getting lineage for non-existent design"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/bio/lineage/{fake_id}")
        assert response.status_code == 404


class TestStatsEndpoints:
    """Test statistics endpoints"""
    
    def test_get_bio_stats(self, client):
        """Test getting biological entity statistics"""
        # Create design via API
        design_data = {
            "name": "Test Design",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F"
        }
        
        design_response = client.post("/api/bio/designs", json=design_data)
        assert design_response.status_code == 200
        design = design_response.json()
        
        # Create build via API
        build_data = {
            "name": "Test Build",
            "sequence": "MGT...L72F...K",
            "sequence_type": "protein",
            "mutation_list": "L72F",
            "design_id": design["id"],
            "construct_type": "plasmid",
            "build_status": "completed"
        }
        
        build_response = client.post("/api/bio/builds", json=build_data)
        assert build_response.status_code == 200
        build = build_response.json()
        
        # Create test via API
        test_data = {
            "name": "Test Activity",
            "test_type": "activity",
            "result_value": 25.0,
            "result_unit": "μM/min",
            "design_id": design["id"],
            "build_id": build["id"],
            "assay_name": "Enzyme Activity Assay",
            "technician": "Dr. Smith"
        }
        
        test_response = client.post("/api/bio/tests", json=test_data)
        assert test_response.status_code == 200
        
        # Get stats
        response = client.get("/api/bio/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_designs"] == 1
        assert data["total_builds"] == 1
        assert data["total_tests"] == 1 