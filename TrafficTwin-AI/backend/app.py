from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from db import engine, Base
from routes.incidents import router as incidents_router

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="TrafficTwin AI",
    description="Adaptive traffic intelligence system for event-driven congestion management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(incidents_router, tags=["Incidents"])

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TrafficTwin AI Backend"
    }

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "service": "TrafficTwin AI",
        "version": "1.0.0",
        "description": "Adaptive traffic intelligence system",
        "docs": "/docs",
        "endpoints": {
            "POST /incident": "Submit new incident",
            "POST /predict-clearance": "Predict clearance time",
            "POST /calculate-severity": "Calculate severity score",
            "POST /retrieve-similar": "Retrieve similar incidents",
            "POST /recommend": "Get recommendations",
            "POST /resolve-incident/{id}": "Resolve incident",
            "GET /incident/{id}": "Get incident details",
            "GET /incidents": "List incidents"
        }
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
