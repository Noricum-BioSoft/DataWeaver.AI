from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/dataweaver"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models to ensure they're registered
from .models.workflow import Workflow, WorkflowStep
from .models.file import File, FileMetadata, FileRelationship
from .models.dataset import Dataset, DatasetMatch

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine) 