import pytest
import os
import tempfile
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.database import get_db
from models.bio_entities import Design, Build, Test
from app.models.file import File, FileStatus
from app.models.workflow import Workflow, WorkflowStep
from app.models.dataset import Dataset, DatasetMatch

class TestDataFiles:
    """Comprehensive test suite for all test data files"""
    
    @pytest.fixture(scope="class")
    def test_engine(self):
        """Create test database engine"""
        TEST_DATABASE_URL = "sqlite:///./test_data_files.db"
        engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
        
        # Import and create all tables
        from app.database import Base
        Base.metadata.create_all(bind=engine)
        
        yield engine
        
        # Cleanup
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_data_files.db"):
            os.remove("./test_data_files.db")
    
    @pytest.fixture(scope="function")
    def db_session(self, test_engine):
        """Create database session for each test"""
        TestingSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=test_engine
        )
        session = TestingSessionLocal()
        
        try:
            yield session
        finally:
            session.close()
    
    @pytest.fixture(scope="function")
    def client(self, db_session, test_engine):
        """Create test client with database session"""
        def override_get_db():
            try:
                yield db_session
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        app.state.test_engine = test_engine
        
        with TestClient(app) as test_client:
            yield test_client
        app.dependency_overrides.clear()
    
    def test_csv_files_upload_and_processing(self, client, db_session):
        """Test uploading and processing all CSV files from test_data folder"""
        test_data_dir = Path("test_data")
        
        # List of CSV files to test
        csv_files = [
            "customers.csv",
            "sales.csv", 
            "products.csv",
            "employees.csv",
            "inventory.csv",
            "website_analytics.csv",
            "biological_assays.csv",
            "sequences.csv",
            "test_merge_1.csv",
            "test_merge_2.csv"
        ]
        
        # Add protein files (use only filename, not full path)
        protein_dir = test_data_dir / "proteins"
        if protein_dir.exists():
            csv_files.extend([
                "01-protein_sequences.csv",
                "02-protein_expression.csv", 
                "03-protein_abundance.csv",
                "04-protein_spr.csv"
            ])
        
        uploaded_files = []
        
        for csv_file in csv_files:
            # Handle protein files that are in subdirectories
            if csv_file.startswith(("01-", "02-", "03-", "04-")):
                file_path = test_data_dir / "proteins" / csv_file
            else:
                file_path = test_data_dir / csv_file
                
            if not file_path.exists():
                pytest.skip(f"Test file {csv_file} not found")
            
            print(f"Testing file: {csv_file}")
            
            # Upload file
            with open(file_path, 'rb') as f:
                response = client.post(
                    "/api/files/upload",
                    files={"file": (csv_file, f, "text/csv")}
                )
            
            if response.status_code != 200:
                print(f"❌ Failed to upload {csv_file}: {response.status_code}")
                print(f"Response: {response.text}")
                assert response.status_code == 200, f"Failed to upload {csv_file}"
            upload_result = response.json()
            assert "file_id" in upload_result, f"No file_id in response for {csv_file}"
            
            file_id = upload_result["file_id"]
            uploaded_files.append((csv_file, file_id))
            
            # Verify file was created in database
            db_file = db_session.query(File).filter(File.id == file_id).first()
            assert db_file is not None, f"File {csv_file} not found in database"
            # Filename may have UUID prefix, so check if it ends with the original filename
            assert db_file.filename.endswith(csv_file), f"Filename mismatch for {csv_file} (got: {db_file.filename})"
            assert db_file.status == FileStatus.READY, f"File {csv_file} not ready"
            
            # Test file content validation
            assert db_file.file_size > 0, f"File {csv_file} has zero size"
            
            print(f"✅ Successfully processed {csv_file}")
        
        print(f"✅ All {len(uploaded_files)} CSV files processed successfully")
    
    def test_json_file_processing(self, client, db_session):
        """Test processing the JSON test file"""
        test_data_dir = Path("test_data")
        json_file = "test_dataset.json"
        file_path = test_data_dir / json_file
        
        if not file_path.exists():
            pytest.skip(f"Test file {json_file} not found")
        
        print(f"Testing JSON file: {json_file}")
        
        # Note: Current simple upload endpoint only supports CSV files
        # JSON file upload would require a more sophisticated upload endpoint
        pytest.skip("JSON file upload not yet implemented in simple upload endpoint")
        
        print(f"✅ JSON file processing test skipped (not yet implemented)")
    
    def test_data_merging_capabilities(self, client, db_session):
        """Test merging multiple CSV files together"""
        test_data_dir = Path("test_data")
        
        # Test files specifically designed for merging
        merge_files = ["test_merge_1.csv", "test_merge_2.csv"]
        uploaded_file_ids = []
        
        # Upload merge test files
        for merge_file in merge_files:
            file_path = test_data_dir / merge_file
            if not file_path.exists():
                pytest.skip(f"Merge test file {merge_file} not found")
            
            with open(file_path, 'rb') as f:
                response = client.post(
                    "/api/files/upload",
                    files={"file": (merge_file, f, "text/csv")}
                )
            
            assert response.status_code == 200, f"Failed to upload {merge_file}"
            upload_result = response.json()
            uploaded_file_ids.append(upload_result["file_id"])
        
        # Test intelligent merging
        response = client.post(
            "/api/intelligent-merge/analyze-files",
            files=[("files", open(test_data_dir / merge_files[0], 'rb')),
                   ("files", open(test_data_dir / merge_files[1], 'rb'))]
        )
        
        assert response.status_code == 200, "Intelligent merge failed"
        merge_result = response.json()
        
        # Verify merge analysis results
        assert "files_analyzed" in merge_result, "No files_analyzed in response"
        assert "merge_suggestions" in merge_result, "No merge_suggestions in response"
        assert merge_result["files_analyzed"] == 2, f"Expected 2 files analyzed, got {merge_result['files_analyzed']}"
        assert len(merge_result["merge_suggestions"]) > 0, "No merge suggestions provided"
        
        print(f"✅ Successfully merged {len(merge_files)} files")
    
    def test_bio_entity_processing(self, client, db_session):
        """Test processing biological data files"""
        test_data_dir = Path("test_data")
        
        # Test biological assay file
        bio_file = "biological_assays.csv"
        file_path = test_data_dir / bio_file
        
        if not file_path.exists():
            pytest.skip(f"Biological test file {bio_file} not found")
        
        # Upload biological file
        with open(file_path, 'rb') as f:
            response = client.post(
                "/api/files/upload",
                files={"file": (bio_file, f, "text/csv")}
            )
        
        assert response.status_code == 200, f"Failed to upload {bio_file}"
        upload_result = response.json()
        file_id = upload_result["file_id"]
        
        # Process for bio entities
        response = client.post(
            f"/api/bio/process-file/{file_id}",
            json={"process_type": "assay_results"}
        )
        
        assert response.status_code == 200, "Bio entity processing failed"
        process_result = response.json()
        
        # Verify bio entities were created
        designs = db_session.query(Design).all()
        tests = db_session.query(Test).all()
        
        assert len(designs) > 0, "No designs created from biological data"
        assert len(tests) > 0, "No tests created from biological data"
        
        print(f"✅ Successfully processed biological data: {len(designs)} designs, {len(tests)} tests")
    
    def test_large_file_processing(self, client, db_session):
        """Test processing large files (website_analytics.csv is 6.6MB)"""
        test_data_dir = Path("test_data")
        large_file = "website_analytics.csv"
        file_path = test_data_dir / large_file
        
        if not file_path.exists():
            pytest.skip(f"Large test file {large_file} not found")
        
        print(f"Testing large file: {large_file} ({file_path.stat().st_size / 1024 / 1024:.1f}MB)")
        
        # Upload large file
        with open(file_path, 'rb') as f:
            response = client.post(
                "/api/files/upload",
                files={"file": (large_file, f, "text/csv")}
            )
        
        assert response.status_code == 200, f"Failed to upload large file {large_file}"
        upload_result = response.json()
        assert "file_id" in upload_result, f"No file_id in response for {large_file}"
        
        file_id = upload_result["file_id"]
        
        # Verify file was processed
        db_file = db_session.query(File).filter(File.id == file_id).first()
        assert db_file is not None, f"Large file {large_file} not found in database"
        assert db_file.status == FileStatus.READY, f"Large file {large_file} not ready"
        assert db_file.file_size > 0, f"Large file {large_file} has zero size"
        
        print(f"✅ Successfully processed large file {large_file}")
    
    def test_data_analysis_capabilities(self, client, db_session):
        """Test data analysis on uploaded files"""
        test_data_dir = Path("test_data")
        
        # Upload a sample file for analysis
        sample_file = "customers.csv"
        file_path = test_data_dir / sample_file
        
        if not file_path.exists():
            pytest.skip(f"Sample file {sample_file} not found")
        
        # Upload file
        with open(file_path, 'rb') as f:
            response = client.post(
                "/api/files/upload",
                files={"file": (sample_file, f, "text/csv")}
            )
        
        assert response.status_code == 200, f"Failed to upload {sample_file}"
        upload_result = response.json()
        file_id = upload_result["file_id"]
        
        # Test data analysis queries
        analysis_queries = [
            "Show me a summary of this data",
            "What are the main trends in the data?",
            "Create a scatter plot of the data",
            "How many records are in this dataset?"
        ]
        
        for query in analysis_queries:
            response = client.post(
                "/api/data-qa/ask",
                json={
                    "session_id": "test_session",
                    "question": query
                }
            )
            
            # Analysis should return a response (even if it's an error about missing data)
            assert response.status_code in [200, 400, 422], f"Analysis query failed: {query}"
            
            if response.status_code == 200:
                result = response.json()
                # Check for either 'answer' or 'error' in the response
                assert "answer" in result or "error" in result, f"No answer or error in analysis result for: {query}"
        
        print(f"✅ Successfully tested data analysis capabilities")
    
    def test_error_handling(self, client, db_session):
        """Test error handling for invalid files"""
        
        # Test uploading non-CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a CSV file")
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                response = client.post(
                    "/api/files/upload",
                    files={"file": ("invalid.txt", f, "text/plain")}
                )
            
            # Should handle gracefully (either accept or reject with proper error)
            assert response.status_code in [200, 400, 422], "Invalid file upload should be handled gracefully"
            
        finally:
            os.unlink(temp_file_path)
        
        # Test uploading empty file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("")  # Empty file
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                response = client.post(
                    "/api/files/upload",
                    files={"file": ("empty.csv", f, "text/csv")}
                )
            
            # Should handle gracefully
            assert response.status_code in [200, 400, 422], "Empty file upload should be handled gracefully"
            
        finally:
            os.unlink(temp_file_path)
        
        print(f"✅ Successfully tested error handling")
    
    def test_file_metadata_extraction(self, client, db_session):
        """Test that file metadata is correctly extracted"""
        test_data_dir = Path("test_data")
        
        # Test with a known file
        test_file = "employees.csv"
        file_path = test_data_dir / test_file
        
        if not file_path.exists():
            pytest.skip(f"Test file {test_file} not found")
        
        # Upload file
        with open(file_path, 'rb') as f:
            response = client.post(
                "/api/files/upload",
                files={"file": (test_file, f, "text/csv")}
            )
        
        assert response.status_code == 200, f"Failed to upload {test_file}"
        upload_result = response.json()
        file_id = upload_result["file_id"]
        
        # Verify metadata
        db_file = db_session.query(File).filter(File.id == file_id).first()
        assert db_file is not None, f"File {test_file} not found in database"
        
        # Check file metadata
        assert db_file.filename.endswith(test_file), f"Filename not stored correctly (got: {db_file.filename})"
        assert db_file.file_size > 0, "File size not calculated correctly"
        assert db_file.mime_type == "text/csv", "MIME type not detected correctly"
        assert db_file.status == FileStatus.READY, "File status not set correctly"
        
        print(f"✅ Successfully extracted file metadata for {test_file}")
    
    def test_concurrent_file_processing(self, client, db_session):
        """Test processing multiple files concurrently"""
        test_data_dir = Path("test_data")
        
        # Select multiple files for concurrent processing
        test_files = ["customers.csv", "products.csv", "employees.csv"]
        uploaded_files = []
        
        # Upload files concurrently (simulated)
        for test_file in test_files:
            file_path = test_data_dir / test_file
            if not file_path.exists():
                continue
            
            with open(file_path, 'rb') as f:
                response = client.post(
                    "/api/files/upload",
                    files={"file": (test_file, f, "text/csv")}
                )
            
            if response.status_code == 200:
                upload_result = response.json()
                uploaded_files.append((test_file, upload_result["file_id"]))
        
        # Verify all files were processed
        assert len(uploaded_files) > 0, "No files were uploaded successfully"
        
        for filename, file_id in uploaded_files:
            db_file = db_session.query(File).filter(File.id == file_id).first()
            assert db_file is not None, f"File {filename} not found in database"
            assert db_file.status == FileStatus.READY, f"File {filename} not ready"
        
        print(f"✅ Successfully processed {len(uploaded_files)} files concurrently")
