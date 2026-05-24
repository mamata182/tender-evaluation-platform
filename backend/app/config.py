import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "Tender Evaluation Platform"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tender_eval.db")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

    SECRET_KEY = os.getenv("SECRET_KEY", "tender-secret-key-2024")

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./outputs")
    MAX_FILE_SIZE = 50 * 1024 * 1024

    TESSERACT_CMD = os.getenv(
        "TESSERACT_CMD",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


settings = Settings()