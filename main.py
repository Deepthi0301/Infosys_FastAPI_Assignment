
from fastapi import FastAPI

from database import engine, Base
import models

from user_routes import router as user_router
from profile_routes import router as profile_router


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="Infosys User Management API",
    description="User Management System with JWT Authentication and Profile Management",
    version="1.0.0"
)


# Register API routers
app.include_router(user_router)
app.include_router(profile_router)


# Home API
@app.get("/")
def home():
    return {
        "message": "Welcome to Infosys User Management API",
        "status": "Running successfully"
    }


# Health Check API
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }
