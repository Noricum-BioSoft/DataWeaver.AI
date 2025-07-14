from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import files, workflows, datasets
from api import bio_entities

app = FastAPI(
    title="DataWeaver.AI API",
    description="Data management system for workflows and biological entities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(files.router, prefix="/api")
app.include_router(workflows.router, prefix="/api")
app.include_router(datasets.router, prefix="/api")
app.include_router(bio_entities.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "DataWeaver.AI API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"} 