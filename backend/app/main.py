from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from app.config import settings
from app.database import init_db
from app.routers import tender, bidder, evaluation
from app.routers.auth import router as auth_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Tender Evaluation Platform",
    description="AI-Based Tender Evaluation and Eligibility Analysis",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tender.router)
app.include_router(bidder.router)
app.include_router(evaluation.router)


@app.on_event("startup")
def startup():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    init_db()
    logger.info("Server started successfully!")
    logger.info(f"GROQ configured: {bool(settings.GROQ_API_KEY)}")
    logger.info(f"SECRET_KEY configured: {bool(settings.SECRET_KEY)}")


@app.get("/")
def home():
    return {
        "message": "AI Tender Evaluation Platform",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "ai_configured": bool(settings.GROQ_API_KEY),
        "model": settings.LLM_MODEL
    }