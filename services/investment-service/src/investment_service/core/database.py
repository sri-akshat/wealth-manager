# src/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.orm import Session
from typing import Generator
from .config import settings

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass

# Create engine with the correct configuration
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.TEST_MODE else {},
    echo=settings.TEST_MODE  # Enable SQL logging in test mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Database dependency to be used in FastAPI endpoints.
    Yields a SQLAlchemy session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()