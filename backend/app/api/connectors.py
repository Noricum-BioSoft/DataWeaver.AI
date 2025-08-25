from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from ..models.connector import Connector, DataSource, DataExtract, ConnectorSyncLog
from ..schemas.connector import (
    ConnectorCreate, ConnectorUpdate, ConnectorResponse,
    DataSourceCreate, DataSourceUpdate, DataSourceResponse,
    DataExtractCreate, DataExtractUpdate, DataExtractResponse,
    ConnectorSyncLogResponse, DemoScenario, ConnectionTestRequest, ConnectionTestResponse
)
from ..services.connector_factory import ConnectorFactory
from ..services.scenario_manager import ScenarioManager
import logging

router = APIRouter(prefix="/connectors", tags=["connectors"])
logger = logging.getLogger(__name__)

# Demo scenarios
@router.get("/scenarios", response_model=List[Dict[str, Any]])
def get_demo_scenarios(db: Session = Depends(get_db)):
    """Get available demo scenarios"""
    scenario_manager = ScenarioManager(db)
    return scenario_manager.get_available_scenarios()

@router.post("/scenarios/{scenario_id}/setup", response_model=Dict[str, Any])
async def setup_demo_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Setup a demo scenario"""
    scenario_manager = ScenarioManager(db)
    try:
        result = await scenario_manager.setup_scenario(scenario_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Scenario setup failed for {scenario_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

# Supported connector types
@router.get("/types/supported", response_model=List[str])
def get_supported_connector_types():
    """Get list of supported connector types"""
    supported_types = ConnectorFactory.get_supported_types()
    return [connector_type.value for connector_type in supported_types]

# Connector management endpoints
@router.get("/", response_model=List[ConnectorResponse])
def get_connectors(db: Session = Depends(get_db)):
    """Get all connectors"""
    connectors = db.query(Connector).all()
    return connectors

@router.post("/", response_model=ConnectorResponse)
def create_connector(connector: ConnectorCreate, db: Session = Depends(get_db)):
    """Create a new connector"""
    db_connector = Connector(
        name=connector.name,
        description=connector.description,
        connector_type=connector.connector_type,
        auth_type=connector.auth_type,
        config=connector.config,
        sync_enabled=connector.sync_enabled,
        sync_schedule=connector.sync_schedule
    )
    db.add(db_connector)
    db.commit()
    db.refresh(db_connector)
    return db_connector

@router.get("/{connector_id}", response_model=ConnectorResponse)
def get_connector(connector_id: int, db: Session = Depends(get_db)):
    """Get a specific connector"""
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector

@router.put("/{connector_id}", response_model=ConnectorResponse)
def update_connector(connector_id: int, connector: ConnectorUpdate, db: Session = Depends(get_db)):
    """Update a connector"""
    db_connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not db_connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    update_data = connector.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_connector, field, value)
    
    db.commit()
    db.refresh(db_connector)
    return db_connector

@router.delete("/{connector_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connector(connector_id: int, db: Session = Depends(get_db)):
    """Delete a connector"""
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    db.delete(connector)
    db.commit()
    return None

# Connection testing
@router.post("/{connector_id}/test", response_model=ConnectionTestResponse)
async def test_connection(connector_id: int, test_request: ConnectionTestRequest, db: Session = Depends(get_db)):
    """Test connection to a data source"""
    # Use connector_id from URL path if not provided in request body
    if test_request.connector_id is None:
        test_request.connector_id = connector_id
    
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    try:
        connector_instance = ConnectorFactory.create_connector(connector, db)
        result = await connector_instance.test_connection()
        return ConnectionTestResponse(
            success=result.get("success", False),
            message=result.get("message", "Connection test completed"),
            details=result.get("details")
        )
    except Exception as e:
        logger.error(f"Connection test failed for connector {connector_id}: {str(e)}")
        return ConnectionTestResponse(
            success=False,
            message=f"Connection test failed: {str(e)}",
            details={"error": str(e)}
        )

# Data source management
@router.get("/{connector_id}/data-sources", response_model=List[DataSourceResponse])
def get_connector_data_sources(connector_id: int, db: Session = Depends(get_db)):
    """Get data sources for a connector"""
    data_sources = db.query(DataSource).filter(DataSource.connector_id == connector_id).all()
    return data_sources

@router.post("/{connector_id}/data-sources", response_model=DataSourceResponse)
def create_data_source(connector_id: int, data_source: DataSourceCreate, db: Session = Depends(get_db)):
    """Create a new data source for a connector"""
    # Verify connector exists
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    db_data_source = DataSource(
        connector_id=connector_id,
        name=data_source.name,
        description=data_source.description,
        source_type=data_source.source_type,
        source_path=data_source.source_path,
        schema=data_source.data_schema,
        source_metadata=data_source.source_metadata,
        is_active=data_source.is_active,
        sync_enabled=data_source.sync_enabled
    )
    db.add(db_data_source)
    db.commit()
    db.refresh(db_data_source)
    return db_data_source

@router.post("/{connector_id}/discover", response_model=List[Dict[str, Any]])
async def discover_data_sources(connector_id: int, db: Session = Depends(get_db)):
    """Discover data sources for a connector"""
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    try:
        connector_instance = ConnectorFactory.create_connector(connector, db)
        discovered_sources = await connector_instance.discover_data_sources()
        return discovered_sources
    except Exception as e:
        logger.error(f"Data source discovery failed for connector {connector_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")

# Data extraction
@router.post("/data-sources/{data_source_id}/extract", response_model=DataExtractResponse)
async def extract_data(data_source_id: int, extract_config: Dict[str, Any], db: Session = Depends(get_db)):
    """Extract data from a data source"""
    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    connector = db.query(Connector).filter(Connector.id == data_source.connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    try:
        connector_instance = ConnectorFactory.create_connector(connector, db)
        result = await connector_instance.extract_data(data_source, extract_config)
        
        # Create data extract record
        data_extract = DataExtract(
            data_source_id=data_source_id,
            extract_type=extract_config.get("extract_type", "full"),
            extract_config=extract_config,
            status="completed",
            data_file_path=result.get("data_file_path"),
            data_format=result.get("data_format", "csv"),
            row_count=result.get("row_count"),
            column_count=result.get("column_count")
        )
        db.add(data_extract)
        db.commit()
        db.refresh(data_extract)
        
        return data_extract
    except Exception as e:
        logger.error(f"Data extraction failed for data source {data_source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

# Sync operations
@router.post("/{connector_id}/sync", response_model=Dict[str, Any])
async def sync_connector(connector_id: int, db: Session = Depends(get_db)):
    """Sync all data sources for a connector"""
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    data_sources = db.query(DataSource).filter(DataSource.connector_id == connector_id).all()
    if not data_sources:
        raise HTTPException(status_code=404, detail="No data sources found for connector")
    
    try:
        connector_instance = ConnectorFactory.create_connector(connector, db)
        result = await connector_instance.sync_data(data_sources)
        
        # Create sync log
        sync_log = ConnectorSyncLog(
            connector_id=connector_id,
            sync_type="full",
            status="success",
            records_processed=result.get("data_sources_synced", 0),
            records_added=result.get("data_sources_synced", 0)
        )
        db.add(sync_log)
        db.commit()
        
        return result
    except Exception as e:
        logger.error(f"Sync failed for connector {connector_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

# Demo scenarios
@router.get("/scenarios", response_model=List[Dict[str, Any]])
def get_demo_scenarios(db: Session = Depends(get_db)):
    """Get available demo scenarios"""
    scenario_manager = ScenarioManager(db)
    return scenario_manager.get_available_scenarios()

@router.post("/scenarios/{scenario_id}/setup", response_model=Dict[str, Any])
async def setup_demo_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Setup a demo scenario"""
    scenario_manager = ScenarioManager(db)
    try:
        result = await scenario_manager.setup_scenario(scenario_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Scenario setup failed for {scenario_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

# Supported connector types
@router.get("/types/supported", response_model=List[str])
def get_supported_connector_types():
    """Get list of supported connector types"""
    supported_types = ConnectorFactory.get_supported_types()
    return [connector_type.value for connector_type in supported_types]
