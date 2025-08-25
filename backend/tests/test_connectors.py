import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import tempfile
import shutil

from main import app
from app.database import get_db, Base
from app.models.connector import ConnectorType, ConnectorStatus, AuthenticationType
from app.services.scenario_manager import ScenarioManager

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Import all models to ensure they're registered
    from app.models.connector import Connector, DataSource, DataExtract, ConnectorSyncLog
    from app.models.workflow import Workflow, WorkflowStep
    from app.models.file import File
    from app.models.dataset import Dataset
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        expire_on_commit=False, 
        bind=engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    return TestClient(app)

class TestConnectorSystem:
    """Test the complete connector system"""
    
    def test_get_supported_connector_types(self, client):
        """Test getting supported connector types"""
        response = client.get("/api/connectors/types/supported")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "GOOGLE_WORKSPACE" in data
        assert "SLACK" in data
        assert "LIMS" in data
    
    def test_create_connector(self, client_shared_session):
        """Test creating a new connector"""
        connector_data = {
            "name": "Test Google Workspace",
            "description": "Test connector for Google Workspace",
            "connector_type": "GOOGLE_WORKSPACE",
            "auth_type": "OAUTH2",
            "auth_config": {"demo_mode": True},
            "connection_config": {"scopes": ["sheets.readonly"]},
            "sync_enabled": False
        }
        
        response = client_shared_session.post("/api/connectors/", json=connector_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == connector_data["name"]
        assert data["connector_type"] == connector_data["connector_type"]
        assert data["status"] == "disconnected"
    
    def test_get_connectors(self, client_shared_session):
        """Test getting all connectors"""
        # Create a test connector first
        connector_data = {
            "name": "Test Connector",
            "description": "Test connector",
            "connector_type": "GOOGLE_WORKSPACE",
            "auth_type": "OAUTH2",
            "auth_config": {"demo_mode": True}
        }
        client_shared_session.post("/api/connectors/", json=connector_data)
        
        response = client_shared_session.get("/api/connectors/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_test_connection(self, client_shared_session):
        """Test connection testing functionality"""
        # Create a test connector
        connector_data = {
            "name": "Test Google Workspace",
            "description": "Test connector",
            "connector_type": "GOOGLE_WORKSPACE",
            "auth_type": "OAUTH2",
            "auth_config": {"demo_mode": True}
        }
        create_response = client_shared_session.post("/api/connectors/", json=connector_data)
        connector_id = create_response.json()["id"]
        
        # Test connection
        test_request = {"connector_id": connector_id, "test_config": {}}
        response = client_shared_session.post(f"/api/connectors/{connector_id}/test", json=test_request)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Successfully connected" in data["message"]
    
    def test_discover_data_sources(self, client_shared_session):
        """Test data source discovery"""
        # Create a test connector
        connector_data = {
            "name": "Test Google Workspace",
            "description": "Test connector",
            "connector_type": "GOOGLE_WORKSPACE",
            "auth_type": "OAUTH2",
            "auth_config": {"demo_mode": True}
        }
        create_response = client_shared_session.post("/api/connectors/", json=connector_data)
        connector_id = create_response.json()["id"]
        
        # Discover data sources
        response = client_shared_session.post(f"/api/connectors/{connector_id}/discover")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]
        assert "source_type" in data[0]
    
    def test_create_data_source(self, client_shared_session):
        """Test creating a data source"""
        # Create a test connector first
        connector_data = {
            "name": "Test Google Workspace",
            "description": "Test connector",
            "connector_type": "GOOGLE_WORKSPACE",
            "auth_type": "OAUTH2",
            "auth_config": {"demo_mode": True}
        }
        create_response = client_shared_session.post("/api/connectors/", json=connector_data)
        connector_id = create_response.json()["id"]
        
        # Create data source
        data_source_data = {
            "connector_id": connector_id,
            "name": "Customer Database",
            "description": "Customer information spreadsheet",
            "source_type": "spreadsheet",
            "source_path": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
            "data_schema": {
                "columns": ["customer_id", "name", "email", "company"],
                "row_count": 1000
            }
        }
        
        response = client_shared_session.post(f"/api/connectors/{connector_id}/data-sources", json=data_source_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == data_source_data["name"]
        assert data["connector_id"] == connector_id
    
    def test_extract_data(self, client_shared_session):
        """Test data extraction"""
        # Create connector and data source
        connector_data = {
            "name": "Test Google Workspace",
            "description": "Test connector",
            "connector_type": "GOOGLE_WORKSPACE",
            "auth_type": "OAUTH2",
            "auth_config": {"demo_mode": True}
        }
        create_response = client_shared_session.post("/api/connectors/", json=connector_data)
        connector_id = create_response.json()["id"]
        
        data_source_data = {
            "connector_id": connector_id,
            "name": "Test Data Source",
            "description": "Test data source",
            "source_type": "spreadsheet",
            "source_path": "test_path"
        }
        ds_response = client_shared_session.post(f"/api/connectors/{connector_id}/data-sources", json=data_source_data)
        data_source_id = ds_response.json()["id"]
        
        # Extract data
        extract_config = {"extract_type": "full"}
        response = client_shared_session.post(f"/api/connectors/data-sources/{data_source_id}/extract", json=extract_config)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["data_source_id"] == data_source_id
    
    def test_sync_connector(self, client_shared_session):
        """Test connector synchronization"""
        # Create connector and data source
        connector_data = {
            "name": "Test Google Workspace",
            "description": "Test connector",
            "connector_type": "GOOGLE_WORKSPACE",
            "auth_type": "OAUTH2",
            "auth_config": {"demo_mode": True}
        }
        create_response = client_shared_session.post("/api/connectors/", json=connector_data)
        connector_id = create_response.json()["id"]
        
        data_source_data = {
            "connector_id": connector_id,
            "name": "Test Data Source",
            "description": "Test data source",
            "source_type": "spreadsheet",
            "source_path": "test_path"
        }
        client_shared_session.post(f"/api/connectors/{connector_id}/data-sources", json=data_source_data)
        
        # Sync connector
        response = client_shared_session.post(f"/api/connectors/{connector_id}/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data_sources_synced" in data

class TestDemoScenarios:
    """Test demo scenario functionality"""
    
    def test_get_demo_scenarios(self, client):
        """Test getting available demo scenarios"""
        response = client.get("/api/connectors/scenarios")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4  # 4 scenarios
        
        # Check scenario types
        scenario_ids = [scenario["id"] for scenario in data]
        assert "customer_intelligence" in scenario_ids
        assert "project_management" in scenario_ids
        assert "financial_consolidation" in scenario_ids
        assert "biotech_research" in scenario_ids
    
    def test_customer_intelligence_scenario(self, client_shared_session):
        """Test Customer Intelligence scenario setup"""
        response = client_shared_session.post("/api/connectors/scenarios/customer_intelligence/setup")
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "customer_intelligence"
        assert "connectors" in data
        assert "data_sources" in data
        assert len(data["connectors"]) == 2  # Google Workspace and Slack
        assert len(data["data_sources"]) > 0
    
    def test_project_management_scenario(self, client_shared_session):
        """Test Project Management scenario setup"""
        response = client_shared_session.post("/api/connectors/scenarios/project_management/setup")
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "project_management"
        assert "connectors" in data
        assert "data_sources" in data
        assert len(data["connectors"]) == 2  # Google Workspace and Slack
        assert len(data["data_sources"]) > 0
    
    def test_financial_consolidation_scenario(self, client_shared_session):
        """Test Financial Consolidation scenario setup"""
        response = client_shared_session.post("/api/connectors/scenarios/financial_consolidation/setup")
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "financial_consolidation"
        assert "connectors" in data
        assert "data_sources" in data
        assert len(data["connectors"]) == 1  # Google Workspace only
        assert len(data["data_sources"]) > 0
    
    def test_biotech_research_scenario(self, client_shared_session):
        """Test Biotech Research scenario setup"""
        response = client_shared_session.post("/api/connectors/scenarios/biotech_research/setup")
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "biotech_research"
        assert "connectors" in data
        assert "data_sources" in data
        assert len(data["connectors"]) == 1  # LIMS only
        assert len(data["data_sources"]) > 0
    
    def test_invalid_scenario(self, client):
        """Test invalid scenario setup"""
        response = client.post("/api/connectors/scenarios/invalid_scenario/setup")
        assert response.status_code == 404
        data = response.json()
        assert "Unknown scenario" in data["detail"]

class TestConnectorFactory:
    """Test the connector factory functionality"""
    
    def test_connector_factory_registration(self, db_session):
        """Test connector factory registration"""
        from app.services.connector_factory import ConnectorFactory, ConnectorType
        
        # Test supported types
        supported_types = ConnectorFactory.get_supported_types()
        assert ConnectorType.GOOGLE_WORKSPACE in supported_types
        assert ConnectorType.SLACK in supported_types
        assert ConnectorType.LIMS in supported_types
    
    def test_connector_creation(self, db_session):
        """Test connector instance creation"""
        from app.services.connector_factory import ConnectorFactory
        from app.models.connector import Connector, ConnectorType, AuthenticationType
        
        # Create a test connector
        connector = Connector(
            name="Test Connector",
            connector_type=ConnectorType.GOOGLE_WORKSPACE,
            auth_type=AuthenticationType.OAUTH2,
            auth_config={"demo_mode": True}
        )
        db_session.add(connector)
        db_session.commit()
        
        # Create connector instance
        connector_instance = ConnectorFactory.create_connector(connector, db_session)
        assert connector_instance is not None
        assert connector_instance.connector.name == "Test Connector"
    
    def test_invalid_connector_type(self, db_session):
        """Test invalid connector type handling"""
        from app.services.connector_factory import ConnectorFactory
        from app.models.connector import Connector, ConnectorType, AuthenticationType
        
        # Create a connector with unsupported type
        connector = Connector(
            name="Test Connector",
            connector_type=ConnectorType.EMAIL,  # Not registered
            auth_type=AuthenticationType.API_KEY,
            auth_config={}
        )
        db_session.add(connector)
        db_session.commit()
        
        # Should raise ValueError
        with pytest.raises(ValueError):
            ConnectorFactory.create_connector(connector, db_session)

class TestScenarioManager:
    """Test the scenario manager functionality"""
    
    def test_scenario_manager_initialization(self, db_session):
        """Test scenario manager initialization"""
        scenario_manager = ScenarioManager(db_session)
        assert scenario_manager is not None
    
    def test_get_available_scenarios(self, db_session):
        """Test getting available scenarios"""
        scenario_manager = ScenarioManager(db_session)
        scenarios = scenario_manager.get_available_scenarios()
        assert len(scenarios) == 4
        assert scenarios[0]["id"] == "customer_intelligence"
        assert scenarios[1]["id"] == "project_management"
        assert scenarios[2]["id"] == "financial_consolidation"
        assert scenarios[3]["id"] == "biotech_research"
    
    def test_customer_intelligence_scenario_details(self, db_session):
        """Test Customer Intelligence scenario details"""
        scenario_manager = ScenarioManager(db_session)
        scenario = scenario_manager._get_customer_intelligence_scenario()
        assert scenario.id == "customer_intelligence"
        assert scenario.name == "Customer Intelligence Dashboard"
        assert scenario.scenario_type == "enterprise"
        assert len(scenario.sample_queries) > 0
        assert len(scenario.expected_outcomes) > 0
    
    def test_biotech_research_scenario_details(self, db_session):
        """Test Biotech Research scenario details"""
        scenario_manager = ScenarioManager(db_session)
        scenario = scenario_manager._get_biotech_research_scenario()
        assert scenario.id == "biotech_research"
        assert scenario.name == "Multi-Omics Research Intelligence"
        assert scenario.scenario_type == "biotech"
        assert len(scenario.sample_queries) > 0
        assert len(scenario.expected_outcomes) > 0

class TestEndToEndWorkflows:
    """Test complete end-to-end workflows"""
    
    def test_complete_customer_intelligence_workflow(self, client_shared_session):
        """Test complete Customer Intelligence workflow"""
        # 1. Setup scenario
        setup_response = client_shared_session.post("/api/connectors/scenarios/customer_intelligence/setup")
        assert setup_response.status_code == 200
        setup_data = setup_response.json()
        
        # Verify scenario setup created connectors and data sources
        assert setup_data["scenario_id"] == "customer_intelligence"
        assert len(setup_data["connectors"]) >= 2
        assert len(setup_data["data_sources"]) > 0
        
        # 2. Get connectors
        connectors_response = client_shared_session.get("/api/connectors/")
        assert connectors_response.status_code == 200
        connectors = connectors_response.json()
        assert len(connectors) >= 2
        
        # 3. Test connections (basic functionality)
        for connector in connectors:
            test_request = {"connector_id": connector["id"], "test_config": {}}
            test_response = client_shared_session.post(f"/api/connectors/{connector['id']}/test", json=test_request)
            assert test_response.status_code == 200
            test_data = test_response.json()
            assert test_data["success"] == True
    
    def test_complete_biotech_research_workflow(self, client_shared_session):
        """Test complete Biotech Research workflow"""
        # 1. Setup scenario
        setup_response = client_shared_session.post("/api/connectors/scenarios/biotech_research/setup")
        assert setup_response.status_code == 200
        setup_data = setup_response.json()
        
        # Verify scenario setup created connectors and data sources
        assert setup_data["scenario_id"] == "biotech_research"
        assert len(setup_data["connectors"]) >= 1
        assert len(setup_data["data_sources"]) > 0
        
        # 2. Get connectors
        connectors_response = client_shared_session.get("/api/connectors/")
        assert connectors_response.status_code == 200
        connectors = connectors_response.json()
        assert len(connectors) >= 1
        
        # 3. Test LIMS connection
        lims_connector = next((c for c in connectors if c["connector_type"] == "LIMS"), None)
        assert lims_connector is not None
        
        test_request = {"connector_id": lims_connector["id"], "test_config": {}}
        test_response = client_shared_session.post(f"/api/connectors/{lims_connector['id']}/test", json=test_request)
        assert test_response.status_code == 200
        test_data = test_response.json()
        assert test_data["success"] == True
