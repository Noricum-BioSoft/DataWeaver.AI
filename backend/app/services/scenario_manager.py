from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models.connector import Connector, DataSource, ConnectorType, ConnectorStatus, AuthenticationType
from ..schemas.connector import ConnectorCreate, DataSourceCreate, DemoScenario
from .connector_factory import ConnectorFactory
import logging

logger = logging.getLogger(__name__)

class ScenarioManager:
    """Manages demo scenarios and their setup"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def get_available_scenarios(self) -> List[DemoScenario]:
        """Get list of available demo scenarios"""
        return [
            self._get_customer_intelligence_scenario(),
            self._get_project_management_scenario(),
            self._get_financial_consolidation_scenario(),
            self._get_biotech_research_scenario()
        ]
    
    def setup_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Setup a specific demo scenario"""
        scenario_map = {
            "customer_intelligence": self._setup_customer_intelligence,
            "project_management": self._setup_project_management,
            "financial_consolidation": self._setup_financial_consolidation,
            "biotech_research": self._setup_biotech_research
        }
        
        if scenario_id not in scenario_map:
            raise ValueError(f"Unknown scenario: {scenario_id}")
        
        return scenario_map[scenario_id]()
    
    def _get_customer_intelligence_scenario(self) -> DemoScenario:
        """Customer Intelligence Dashboard scenario"""
        return DemoScenario(
            id="customer_intelligence",
            name="Customer Intelligence Dashboard",
            description="Integrate customer data from multiple sources to create a comprehensive customer intelligence platform",
            scenario_type="enterprise",
            connectors=[],
            data_sources=[],
            sample_queries=[
                "Show me customer satisfaction trends from support channels",
                "Identify high-value customers with declining engagement",
                "Correlate sales data with customer support interactions",
                "Find customers at risk of churning based on communication patterns",
                "Generate a customer 360 view combining all data sources"
            ],
            expected_outcomes=[
                "Unified customer profiles across all touchpoints",
                "Predictive churn models based on multi-source data",
                "Customer sentiment analysis from communications",
                "Sales opportunity identification and scoring",
                "Automated customer health dashboards"
            ]
        )
    
    def _get_project_management_scenario(self) -> DemoScenario:
        """Project Management Analytics scenario"""
        return DemoScenario(
            id="project_management",
            name="Project Management Analytics",
            description="Analyze project data from various collaboration platforms to optimize project delivery",
            scenario_type="enterprise",
            connectors=[],
            data_sources=[],
            sample_queries=[
                "Show me project timeline correlations across teams",
                "Identify bottlenecks in project workflows",
                "Analyze team collaboration patterns and productivity",
                "Predict project completion dates based on current progress",
                "Find resource allocation optimization opportunities"
            ],
            expected_outcomes=[
                "Project timeline optimization recommendations",
                "Team productivity and collaboration insights",
                "Resource utilization analysis and forecasting",
                "Risk assessment based on communication patterns",
                "Automated project status reporting"
            ]
        )
    
    def _get_financial_consolidation_scenario(self) -> DemoScenario:
        """Financial Data Consolidation scenario"""
        return DemoScenario(
            id="financial_consolidation",
            name="Financial Data Consolidation",
            description="Consolidate financial data from multiple sources for comprehensive financial analysis",
            scenario_type="enterprise",
            connectors=[],
            data_sources=[],
            sample_queries=[
                "Consolidate all financial transactions across systems",
                "Identify unusual spending patterns and anomalies",
                "Generate cash flow forecasts based on historical data",
                "Analyze expense patterns by department and category",
                "Create compliance reports for regulatory requirements"
            ],
            expected_outcomes=[
                "Unified financial data warehouse",
                "Automated anomaly detection and alerting",
                "Predictive cash flow modeling",
                "Expense optimization recommendations",
                "Regulatory compliance automation"
            ]
        )
    
    def _get_biotech_research_scenario(self) -> DemoScenario:
        """Biotech Research & Drug Discovery scenario"""
        return DemoScenario(
            id="biotech_research",
            name="Multi-Omics Research Intelligence",
            description="Integrate multi-omics data and scientific literature for drug discovery and research",
            scenario_type="biotech",
            connectors=[],
            data_sources=[],
            sample_queries=[
                "Analyze transcriptomics data for differentially expressed genes in cancer samples",
                "Cross-reference potential drug targets with literature evidence",
                "Identify biomarker candidates from multi-omics data integration",
                "Predict drug response based on patient genomic profiles",
                "Generate target prioritization reports with druggability scores"
            ],
            expected_outcomes=[
                "AI-powered target identification and prioritization",
                "Multi-omics biomarker discovery and validation",
                "Drug response prediction models",
                "Literature-based hypothesis generation",
                "Automated regulatory documentation"
            ]
        )
    
    def _setup_customer_intelligence(self) -> Dict[str, Any]:
        """Setup Customer Intelligence scenario"""
        self.logger.info("Setting up Customer Intelligence scenario")
        
        # Create connectors
        google_connector = self._create_connector(
            ConnectorCreate(
                name="Google Workspace",
                description="Google Sheets and Docs for customer data",
                connector_type=ConnectorType.GOOGLE_WORKSPACE,
                auth_type=AuthenticationType.OAUTH2,
                auth_config={"demo_mode": True},
                connection_config={"scopes": ["sheets.readonly", "docs.readonly"]}
            )
        )
        
        slack_connector = self._create_connector(
            ConnectorCreate(
                name="Slack Communications",
                description="Slack channels for customer support and sales",
                connector_type=ConnectorType.SLACK,
                auth_type=AuthenticationType.API_KEY,
                auth_config={"demo_mode": True},
                connection_config={"channels": ["customer-support", "sales"]}
            )
        )
        
        # Create data sources
        data_sources = []
        for connector in [google_connector, slack_connector]:
            connector_instance = ConnectorFactory.create_connector(connector, self.db)
            discovered_sources = connector_instance.discover_data_sources()
            
            for source_data in discovered_sources:
                data_source = self._create_data_source(
                    DataSourceCreate(
                        connector_id=connector.id,
                        name=source_data["name"],
                        description=source_data["description"],
                        source_type=source_data["source_type"],
                        source_path=source_data["source_path"],
                        schema=source_data.get("schema"),
                        metadata=source_data.get("metadata", {})
                    )
                )
                data_sources.append(data_source)
        
        return {
            "scenario_id": "customer_intelligence",
            "connectors": [google_connector, slack_connector],
            "data_sources": data_sources,
            "message": "Customer Intelligence scenario setup completed"
        }
    
    def _setup_project_management(self) -> Dict[str, Any]:
        """Setup Project Management scenario"""
        self.logger.info("Setting up Project Management scenario")
        
        # Create connectors
        google_connector = self._create_connector(
            ConnectorCreate(
                name="Google Workspace",
                description="Google Docs and Sheets for project documentation",
                connector_type=ConnectorType.GOOGLE_WORKSPACE,
                auth_type=AuthenticationType.OAUTH2,
                auth_config={"demo_mode": True},
                connection_config={"scopes": ["docs.readonly", "sheets.readonly"]}
            )
        )
        
        slack_connector = self._create_connector(
            ConnectorCreate(
                name="Slack Team Communications",
                description="Slack channels for team collaboration",
                connector_type=ConnectorType.SLACK,
                auth_type=AuthenticationType.API_KEY,
                auth_config={"demo_mode": True},
                connection_config={"channels": ["general", "project-updates"]}
            )
        )
        
        # Create data sources
        data_sources = []
        for connector in [google_connector, slack_connector]:
            connector_instance = ConnectorFactory.create_connector(connector, self.db)
            discovered_sources = connector_instance.discover_data_sources()
            
            for source_data in discovered_sources:
                data_source = self._create_data_source(
                    DataSourceCreate(
                        connector_id=connector.id,
                        name=source_data["name"],
                        description=source_data["description"],
                        source_type=source_data["source_type"],
                        source_path=source_data["source_path"],
                        schema=source_data.get("schema"),
                        metadata=source_data.get("metadata", {})
                    )
                )
                data_sources.append(data_source)
        
        return {
            "scenario_id": "project_management",
            "connectors": [google_connector, slack_connector],
            "data_sources": data_sources,
            "message": "Project Management scenario setup completed"
        }
    
    def _setup_financial_consolidation(self) -> Dict[str, Any]:
        """Setup Financial Consolidation scenario"""
        self.logger.info("Setting up Financial Consolidation scenario")
        
        # Create connectors
        google_connector = self._create_connector(
            ConnectorCreate(
                name="Google Sheets Financial Data",
                description="Google Sheets for financial reports and budgets",
                connector_type=ConnectorType.GOOGLE_WORKSPACE,
                auth_type=AuthenticationType.OAUTH2,
                auth_config={"demo_mode": True},
                connection_config={"scopes": ["sheets.readonly"]}
            )
        )
        
        # Create data sources
        data_sources = []
        connector_instance = ConnectorFactory.create_connector(google_connector, self.db)
        discovered_sources = connector_instance.discover_data_sources()
        
        for source_data in discovered_sources:
            data_source = self._create_data_source(
                DataSourceCreate(
                    connector_id=google_connector.id,
                    name=source_data["name"],
                    description=source_data["description"],
                    source_type=source_data["source_type"],
                    source_path=source_data["source_path"],
                    schema=source_data.get("schema"),
                    metadata=source_data.get("metadata", {})
                )
            )
            data_sources.append(data_source)
        
        return {
            "scenario_id": "financial_consolidation",
            "connectors": [google_connector],
            "data_sources": data_sources,
            "message": "Financial Consolidation scenario setup completed"
        }
    
    def _setup_biotech_research(self) -> Dict[str, Any]:
        """Setup Biotech Research scenario"""
        self.logger.info("Setting up Biotech Research scenario")
        
        # Create connectors
        lims_connector = self._create_connector(
            ConnectorCreate(
                name="Laboratory Information Management System",
                description="LIMS for sample tracking and experimental data",
                connector_type=ConnectorType.LIMS,
                auth_type=AuthenticationType.API_KEY,
                auth_config={"demo_mode": True},
                connection_config={"system": "LabWare LIMS"}
            )
        )
        
        # Create data sources
        data_sources = []
        connector_instance = ConnectorFactory.create_connector(lims_connector, self.db)
        discovered_sources = connector_instance.discover_data_sources()
        
        for source_data in discovered_sources:
            data_source = self._create_data_source(
                DataSourceCreate(
                    connector_id=lims_connector.id,
                    name=source_data["name"],
                    description=source_data["description"],
                    source_type=source_data["source_type"],
                    source_path=source_data["source_path"],
                    schema=source_data.get("schema"),
                    metadata=source_data.get("metadata", {})
                )
            )
            data_sources.append(data_source)
        
        return {
            "scenario_id": "biotech_research",
            "connectors": [lims_connector],
            "data_sources": data_sources,
            "message": "Biotech Research scenario setup completed"
        }
    
    def _create_connector(self, connector_data: ConnectorCreate) -> Connector:
        """Create a connector in the database"""
        connector = Connector(
            name=connector_data.name,
            description=connector_data.description,
            connector_type=connector_data.connector_type,
            auth_type=connector_data.auth_type,
            auth_config=connector_data.auth_config,
            connection_config=connector_data.connection_config,
            sync_enabled=connector_data.sync_enabled,
            sync_schedule=connector_data.sync_schedule,
            status=ConnectorStatus.CONNECTED  # Demo mode - assume connected
        )
        
        self.db.add(connector)
        self.db.commit()
        self.db.refresh(connector)
        
        self.logger.info(f"Created connector: {connector.name} (ID: {connector.id})")
        return connector
    
    def _create_data_source(self, data_source_data: DataSourceCreate) -> DataSource:
        """Create a data source in the database"""
        data_source = DataSource(
            connector_id=data_source_data.connector_id,
            name=data_source_data.name,
            description=data_source_data.description,
            source_type=data_source_data.source_type,
            source_path=data_source_data.source_path,
            schema=data_source_data.schema,
            metadata=data_source_data.metadata,
            is_active=data_source_data.is_active,
            sync_enabled=data_source_data.sync_enabled
        )
        
        self.db.add(data_source)
        self.db.commit()
        self.db.refresh(data_source)
        
        self.logger.info(f"Created data source: {data_source.name} (ID: {data_source.id})")
        return data_source
