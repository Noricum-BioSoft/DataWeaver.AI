from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class ConnectorType(enum.Enum):
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

class ConnectorStatus(enum.Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    SYNCING = "syncing"

class AuthenticationType(enum.Enum):
    OAUTH2 = "OAUTH2"
    API_KEY = "API_KEY"
    USERNAME_PASSWORD = "USERNAME_PASSWORD"
    TOKEN = "TOKEN"
    NONE = "NONE"

class Connector(Base):
    __tablename__ = "connectors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    connector_type = Column(Enum(ConnectorType), nullable=False)
    status = Column(Enum(ConnectorStatus), default=ConnectorStatus.DISCONNECTED)
    
    # Authentication and configuration
    auth_type = Column(Enum(AuthenticationType), nullable=False)
    auth_config = Column(JSON)  # OAuth2 tokens, API keys, etc.
    connection_config = Column(JSON)  # URLs, endpoints, settings
    
    # Sync configuration
    sync_enabled = Column(Boolean, default=False)
    sync_schedule = Column(String(100))  # Cron expression
    last_sync = Column(DateTime(timezone=True))
    next_sync = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    data_sources = relationship("DataSource", back_populates="connector")
    sync_logs = relationship("ConnectorSyncLog", back_populates="connector")

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    connector_id = Column(Integer, ForeignKey("connectors.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    source_type = Column(String(100))  # "spreadsheet", "document", "email", "message", etc.
    source_path = Column(String(500))  # File path, URL, query, etc.
    
    # Data schema and metadata
    schema = Column(JSON)  # Data structure definition
    source_metadata = Column(JSON)  # Additional metadata
    last_updated = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True)
    sync_enabled = Column(Boolean, default=True)
    
    # Relationships
    connector = relationship("Connector", back_populates="data_sources")
    data_extracts = relationship("DataExtract", back_populates="data_source")

class DataExtract(Base):
    __tablename__ = "data_extracts"
    
    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    
    # Extract metadata
    extract_type = Column(String(100))  # "full", "incremental", "delta"
    extract_config = Column(JSON)  # Extraction parameters
    status = Column(String(50))  # "pending", "running", "completed", "failed"
    
    # Data storage
    data_file_path = Column(String(500))  # Path to extracted data file
    data_format = Column(String(50))  # "csv", "json", "parquet", etc.
    row_count = Column(Integer)
    column_count = Column(Integer)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    data_source = relationship("DataSource", back_populates="data_extracts")
    workflow = relationship("Workflow")

class ConnectorSyncLog(Base):
    __tablename__ = "connector_sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    connector_id = Column(Integer, ForeignKey("connectors.id"), nullable=False)
    
    # Sync details
    sync_type = Column(String(50))  # "full", "incremental", "manual"
    status = Column(String(50))  # "success", "failed", "partial"
    records_processed = Column(Integer)
    records_added = Column(Integer)
    records_updated = Column(Integer)
    records_deleted = Column(Integer)
    
    # Error information
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    connector = relationship("Connector", back_populates="sync_logs")
