"""
Database Configuration - Quote Request System
SQLite for local development, can be switched to MySQL/PostgreSQL for production
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - Change this for production
# Local: sqlite:///./quote.db
# MySQL: mysql+pymysql://user:password@host:3306/quote_db
# PostgreSQL: postgresql://user:password@host:5432/quote_db

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quote.db")

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}  # SQLite specific
    )
else:
    engine = create_engine(DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for FastAPI - yields database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    from models import Base  # Import here to avoid circular imports
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    init_db()

