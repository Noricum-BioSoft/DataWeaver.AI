from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables
from app.api import workflows_router, files_router, datasets_router

# Create FastAPI app
app = FastAPI(
    title="DataWeaver.AI API",
    description="A comprehensive data management system for workflow-based applications",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflows_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")
app.include_router(datasets_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "DataWeaver.AI"}

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 