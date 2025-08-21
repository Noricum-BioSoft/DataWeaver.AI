from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ConnectorType(str, Enum):
    GOOGLE_WORKSPACE = "GOOGLE_WORKSPACE"
    MICROSOFT_365 = "MICROSOFT_365"
    SLACK = "SLACK"
    EMAIL = "EMAIL"
    DATABASE = "DATABASE"
    API = "API"
    FILE_SYSTEM = "FILE_SYSTEM"
    LIMS = "LIMS"
    OMICS = "OMICS"
    LITERATURE = "LITERATURE"
    CLINICAL = "CLINICAL"

class ConnectorStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    SYNCING = "syncing"

class AuthenticationType(str, Enum):
    OAUTH2 = "OAUTH2"
    API_KEY = "API_KEY"
    USERNAME_PASSWORD = "USERNAME_PASSWORD"
    TOKEN = "TOKEN"
    NONE = "NONE"

# Base schemas
class ConnectorBase(BaseModel):
    name: str = Field(..., description="Connector name")
    description: Optional[str] = Field(None, description="Connector description")
    connector_type: ConnectorType = Field(..., description="Type of connector")
    auth_type: AuthenticationType = Field(..., description="Authentication type")
    auth_config: Optional[Dict[str, Any]] = Field(None, description="Authentication configuration")
    connection_config: Optional[Dict[str, Any]] = Field(None, description="Connection configuration")
    sync_enabled: bool = Field(False, description="Enable automatic sync")
    sync_schedule: Optional[str] = Field(None, description="Cron expression for sync schedule")

class ConnectorCreate(ConnectorBase):
    pass

class ConnectorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None
    connection_config: Optional[Dict[str, Any]] = None
    sync_enabled: Optional[bool] = None
    sync_schedule: Optional[str] = None

class ConnectorResponse(ConnectorBase):
    id: int
    status: ConnectorStatus
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Data Source schemas
class DataSourceBase(BaseModel):
    name: str = Field(..., description="Data source name")
    description: Optional[str] = Field(None, description="Data source description")
    source_type: str = Field(..., description="Type of data source")
    source_path: str = Field(..., description="Path or identifier for the data source")
    data_schema: Optional[Dict[str, Any]] = Field(None, description="Data schema definition")
    source_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    is_active: bool = Field(True, description="Whether the data source is active")
    sync_enabled: bool = Field(True, description="Enable sync for this data source")

class DataSourceCreate(DataSourceBase):
    connector_id: int = Field(..., description="ID of the parent connector")

class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source_path: Optional[str] = None
    data_schema: Optional[Dict[str, Any]] = None
    source_metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    sync_enabled: Optional[bool] = None

class DataSourceResponse(DataSourceBase):
    id: int
    connector_id: int
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True

# Data Extract schemas
class DataExtractBase(BaseModel):
    extract_type: str = Field(..., description="Type of extraction")
    extract_config: Optional[Dict[str, Any]] = Field(None, description="Extraction configuration")
    workflow_id: Optional[int] = Field(None, description="Associated workflow ID")

class DataExtractCreate(DataExtractBase):
    data_source_id: int = Field(..., description="ID of the data source")

class DataExtractUpdate(BaseModel):
    extract_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class DataExtractResponse(DataExtractBase):
    id: int
    data_source_id: int
    status: str
    data_file_path: Optional[str] = None
    data_format: Optional[str] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Sync Log schemas
class ConnectorSyncLogBase(BaseModel):
    sync_type: str = Field(..., description="Type of sync operation")
    status: str = Field(..., description="Sync status")
    records_processed: Optional[int] = Field(None, description="Number of records processed")
    records_added: Optional[int] = Field(None, description="Number of records added")
    records_updated: Optional[int] = Field(None, description="Number of records updated")
    records_deleted: Optional[int] = Field(None, description="Number of records deleted")
    error_message: Optional[str] = Field(None, description="Error message if sync failed")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detailed error information")

class ConnectorSyncLogCreate(ConnectorSyncLogBase):
    connector_id: int = Field(..., description="ID of the connector")

class ConnectorSyncLogResponse(ConnectorSyncLogBase):
    id: int
    connector_id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Scenario-specific schemas
class ScenarioConfig(BaseModel):
    """Configuration for different demo scenarios"""
    scenario_type: str = Field(..., description="Type of scenario")
    connectors: List[ConnectorCreate] = Field(..., description="Connectors for this scenario")
    data_sources: List[DataSourceCreate] = Field(..., description="Data sources for this scenario")
    workflow_config: Optional[Dict[str, Any]] = Field(None, description="Workflow configuration")

class DemoScenario(BaseModel):
    """Demo scenario definition"""
    id: str
    name: str
    description: str
    scenario_type: str
    connectors: List[ConnectorResponse]
    data_sources: List[DataSourceResponse]
    sample_queries: List[str]
    expected_outcomes: List[str]

# Authentication schemas
class OAuth2Config(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: List[str]
    auth_url: str
    token_url: str

class ApiKeyConfig(BaseModel):
    api_key: str
    api_secret: Optional[str] = None
    base_url: str

class ConnectionTestRequest(BaseModel):
    connector_id: int
    test_config: Optional[Dict[str, Any]] = None

class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
