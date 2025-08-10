import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import get_db, Base
from models.bio_entities import Design, Build, Test
from main import app

# Test database configuration
USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    if USE_POSTGRES:
        # PostgreSQL configuration
        try:
            engine = create_engine(TEST_DATABASE_URL)
            # Test connection
            connection = engine.connect()
            connection.close()
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")
    else:
        # SQLite configuration
        engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create database session for each test"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        expire_on_commit=False, 
        bind=test_engine
    )
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with shared database session"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client_shared_session(test_engine):
    """Create test client with truly shared database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        expire_on_commit=False, 
        bind=test_engine
    )
    session = TestingSessionLocal()
    
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    session.close()

@pytest.fixture
def sample_design_data():
    """Sample design data for testing"""
    return {
        "name": "Test Design",
        "alias": "TEST_DESIGN",
        "description": "Test design for unit testing",
        "sequence": "MGT...L72F...K",
        "sequence_type": "protein",
        "mutation_list": "L72F",
        "parent_design_id": None
    }

@pytest.fixture
def sample_build_data():
    """Sample build data for testing"""
    return {
        "name": "Test Build",
        "alias": "TEST_BUILD",
        "description": "Test build for unit testing",
        "sequence": "MGT...L72F...K",
        "sequence_type": "protein",
        "mutation_list": "L72F",
        "parent_build_id": None,
        "design_id": None,  # Will be set in test
        "construct_type": "plasmid",
        "build_status": "completed"
    }

@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing uploads"""
    return """name,alias,sequence,mutations,result_value,result_unit,test_type,assay_name,technician
Clone_7,Clone_7,MGT...L72F...K,L72F,25.0,μM/min,activity,Enzyme Activity Assay,Dr. Smith
WT_Control,WT_Control,MGT...L72...K,,15.0,μM/min,activity,Enzyme Activity Assay,Dr. Smith
Mutant_A,Mutant_A,MGT...R80K...K,R80K,8.5,μM/min,activity,Enzyme Activity Assay,Dr. Smith"""

@pytest.fixture
def temp_csv_file(sample_csv_content):
    """Create a temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_csv_content)
        temp_file_path = f.name
    yield temp_file_path
    os.unlink(temp_file_path) 