from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models.connector import Connector, DataSource, DataExtract, ConnectorType, ConnectorStatus
from ..schemas.connector import ConnectorCreate, DataSourceCreate, DataExtractCreate
import logging

logger = logging.getLogger(__name__)

class BaseConnector(ABC):
    """Abstract base class for all connectors"""
    
    def __init__(self, connector: Connector, db: Session):
        self.connector = connector
        self.db = db
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection to the data source"""
        pass
    
    @abstractmethod
    async def discover_data_sources(self) -> List[Dict[str, Any]]:
        """Discover available data sources"""
        pass
    
    @abstractmethod
    async def extract_data(self, data_source: DataSource, extract_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from a specific data source"""
        pass
    
    @abstractmethod
    async def sync_data(self, data_sources: List[DataSource]) -> Dict[str, Any]:
        """Sync data from multiple data sources"""
        pass
    
    def update_status(self, status: ConnectorStatus):
        """Update connector status"""
        self.connector.status = status
        self.db.commit()
        self.logger.info(f"Connector {self.connector.name} status updated to {status}")

class ConnectorFactory:
    """Factory for creating connector instances"""
    
    _connectors: Dict[ConnectorType, type] = {}
    
    @classmethod
    def register_connector(cls, connector_type: ConnectorType, connector_class: type):
        """Register a connector class for a specific type"""
        cls._connectors[connector_type] = connector_class
    
    @classmethod
    def create_connector(cls, connector: Connector, db: Session) -> BaseConnector:
        """Create a connector instance based on type"""
        if connector.connector_type not in cls._connectors:
            raise ValueError(f"No connector registered for type: {connector.connector_type}")
        
        connector_class = cls._connectors[connector.connector_type]
        return connector_class(connector, db)
    
    @classmethod
    def get_supported_types(cls) -> List[ConnectorType]:
        """Get list of supported connector types"""
        return list(cls._connectors.keys())

# Mock connectors for demo scenarios
class MockGoogleWorkspaceConnector(BaseConnector):
    """Mock Google Workspace connector for demo purposes"""
    
    async def test_connection(self) -> Dict[str, Any]:
        self.logger.info("Testing Google Workspace connection")
        return {
            "success": True,
            "message": "Successfully connected to Google Workspace",
            "details": {
                "scopes": ["drive.readonly", "sheets.readonly", "docs.readonly"],
                "user_email": "demo@example.com"
            }
        }
    
    async def discover_data_sources(self) -> List[Dict[str, Any]]:
        self.logger.info("Discovering Google Workspace data sources")
        return [
            {
                "name": "Customer Database",
                "description": "Customer information spreadsheet",
                "source_type": "spreadsheet",
                "source_path": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
                "schema": {
                    "columns": ["customer_id", "name", "email", "company", "status"],
                    "row_count": 1000
                }
            },
            {
                "name": "Sales Report Q4",
                "description": "Quarterly sales performance data",
                "source_type": "spreadsheet",
                "source_path": "1abc123def456ghi789jkl012mno345pqr678stu901vwx234",
                "schema": {
                    "columns": ["date", "product", "sales_amount", "region", "sales_rep"],
                    "row_count": 500
                }
            }
        ]
    
    async def extract_data(self, data_source: DataSource, extract_config: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Extracting data from {data_source.name}")
        # Mock data extraction
        return {
            "success": True,
            "data_file_path": f"extracts/google_workspace_{data_source.id}.csv",
            "row_count": 1000,
            "column_count": 5,
            "extract_type": extract_config.get("extract_type", "full")
        }
    
    async def sync_data(self, data_sources: List[DataSource]) -> Dict[str, Any]:
        self.logger.info(f"Syncing {len(data_sources)} data sources")
        results = []
        for data_source in data_sources:
            result = await self.extract_data(data_source, {"extract_type": "incremental"})
            results.append(result)
        
        return {
            "success": True,
            "data_sources_synced": len(data_sources),
            "results": results
        }

class MockSlackConnector(BaseConnector):
    """Mock Slack connector for demo purposes"""
    
    async def test_connection(self) -> Dict[str, Any]:
        self.logger.info("Testing Slack connection")
        return {
            "success": True,
            "message": "Successfully connected to Slack",
            "details": {
                "workspace": "demo-workspace",
                "channels": ["general", "customer-support", "sales"]
            }
        }
    
    async def discover_data_sources(self) -> List[Dict[str, Any]]:
        self.logger.info("Discovering Slack data sources")
        return [
            {
                "name": "Customer Support Channel",
                "description": "Customer support messages and interactions",
                "source_type": "channel",
                "source_path": "C1234567890",
                "schema": {
                    "columns": ["timestamp", "user", "message", "channel", "thread_ts"],
                    "row_count": 5000
                }
            },
            {
                "name": "Sales Team Channel",
                "description": "Sales team communications and updates",
                "source_type": "channel",
                "source_path": "C0987654321",
                "schema": {
                    "columns": ["timestamp", "user", "message", "channel", "attachments"],
                    "row_count": 3000
                }
            }
        ]
    
    async def extract_data(self, data_source: DataSource, extract_config: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Extracting data from {data_source.name}")
        return {
            "success": True,
            "data_file_path": f"extracts/slack_{data_source.id}.json",
            "row_count": 5000,
            "column_count": 5,
            "extract_type": extract_config.get("extract_type", "full")
        }
    
    async def sync_data(self, data_sources: List[DataSource]) -> Dict[str, Any]:
        self.logger.info(f"Syncing {len(data_sources)} data sources")
        results = []
        for data_source in data_sources:
            result = await self.extract_data(data_source, {"extract_type": "incremental"})
            results.append(result)
        
        return {
            "success": True,
            "data_sources_synced": len(data_sources),
            "results": results
        }

class MockLimsConnector(BaseConnector):
    """Mock LIMS connector for biotech demo"""
    
    async def test_connection(self) -> Dict[str, Any]:
        self.logger.info("Testing LIMS connection")
        return {
            "success": True,
            "message": "Successfully connected to LIMS",
            "details": {
                "system": "LabWare LIMS",
                "modules": ["sample_management", "workflow_management", "results_management"]
            }
        }
    
    async def discover_data_sources(self) -> List[Dict[str, Any]]:
        self.logger.info("Discovering LIMS data sources")
        return [
            {
                "name": "Sample Database",
                "description": "Sample tracking and metadata",
                "source_type": "database_table",
                "source_path": "samples",
                "schema": {
                    "columns": ["sample_id", "sample_type", "collection_date", "status", "location"],
                    "row_count": 10000
                }
            },
            {
                "name": "Experimental Results",
                "description": "Laboratory test results and measurements",
                "source_type": "database_table",
                "source_path": "experimental_results",
                "schema": {
                    "columns": ["result_id", "sample_id", "test_type", "value", "unit", "timestamp"],
                    "row_count": 50000
                }
            }
        ]
    
    async def extract_data(self, data_source: DataSource, extract_config: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Extracting data from {data_source.name}")
        return {
            "success": True,
            "data_file_path": f"extracts/lims_{data_source.id}.csv",
            "row_count": 10000,
            "column_count": 6,
            "extract_type": extract_config.get("extract_type", "full")
        }
    
    async def sync_data(self, data_sources: List[DataSource]) -> Dict[str, Any]:
        self.logger.info(f"Syncing {len(data_sources)} data sources")
        results = []
        for data_source in data_sources:
            result = await self.extract_data(data_source, {"extract_type": "incremental"})
            results.append(result)
        
        return {
            "success": True,
            "data_sources_synced": len(data_sources),
            "results": results
        }

# Register mock connectors
ConnectorFactory.register_connector(ConnectorType.GOOGLE_WORKSPACE, MockGoogleWorkspaceConnector)
ConnectorFactory.register_connector(ConnectorType.SLACK, MockSlackConnector)
ConnectorFactory.register_connector(ConnectorType.LIMS, MockLimsConnector)
