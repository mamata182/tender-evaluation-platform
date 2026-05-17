from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from app.config import settings
from app.database import init_db
from app.routers import tender, bidder, evaluation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Tender Evaluation Platform",
    description="Automated tender eligibility evaluation using AI for Government of Karnataka",
    version="1.0.0"
)

# CORS - Allow all origins for now (we can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(tender.router)
app.include_router(bidder.router)
app.include_router(evaluation.router)


@app.on_event("startup")
def startup():
    """Run on application startup."""
    logger.info("Starting Tender Evaluation Platform...")
    
    # Create directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    # Initialize database
    init_db()
    
    logger.info("Server started successfully!")
    logger.info(f"GROQ API Key configured: {bool(settings.GROQ_API_KEY)}")
    logger.info(f"LLM Model: {settings.LLM_MODEL}")


@app.get("/")
def home():
    """Home endpoint - returns API status."""
    return {
        "message": "AI Tender Evaluation Platform",
        "version": "1.0.0",
        "status": "running",
        "ai_provider": "Groq (Llama 3.3 70B)",
        "docs": "/docs",
        "endpoints": {
            "tender_upload": "/api/tender/upload",
            "bidder_upload": "/api/bidder/upload",
            "evaluate": "/api/evaluation/evaluate",
            "api_docs": "/docs"
        }
    }


@app.get("/health")
def health():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "ai_configured": bool(settings.GROQ_API_KEY),
        "model": settings.LLM_MODEL
    }