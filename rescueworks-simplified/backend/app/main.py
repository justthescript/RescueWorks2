from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .database import init_db
from .config import settings
from .routers import auth, animals, foster, operations, admin

# Initialize FastAPI app
app = FastAPI(
    title="RescueWorks API",
    description="Animal rescue management system",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory
if os.path.exists("/app/uploads"):
    app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(animals.router)
app.include_router(foster.router)
app.include_router(operations.router)
app.include_router(admin.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
def read_root():
    return {
        "message": "RescueWorks API",
        "version": "2.0.0",
        "status": "healthy"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
