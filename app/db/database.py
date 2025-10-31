"""
Database setup module.
Supports SQLite, PostgreSQL, MySQL and any SQLAlchemy-compatible databases.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import config
from app.models.currency import Base

# Create engine from configured DATABASE_URL
engine = create_engine(
    config.DATABASE_URL, connect_args={"check_same_thread": False} if config.DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database and create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency to yield a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
