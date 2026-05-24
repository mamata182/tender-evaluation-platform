from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.db_models import Base

database_url = settings.DATABASE_URL

# Fix: Render/PostgreSQL gives postgres:// but SQLAlchemy needs postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# SQLite needs check_same_thread=False, PostgreSQL does not
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created")


def get_db():
    """Dependency to get database session in routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()