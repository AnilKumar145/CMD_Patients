from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import patient
from app.auth_utils import get_current_user, User

app = FastAPI(
    title="Patient Microservice",
    description="Handles patient management in the healthcare system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://healthcare-frontend.onrender.com",
        "http://localhost:3000"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(patient.router)  # Changed from 'patients' to 'patient'

@app.get("/")
def read_root():
    return {"message": "Patient Microservice Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
