"""
Өгөгдлийн сангийн тохиргооны модуль.
SQLite, PostgreSQL, MySQL болон бусад SQLAlchemy-тэй нийцтэй өгөгдлийн сангуудыг дэмждэг.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.currency import Base
from app.config import config

# Тохируулсан DATABASE_URL-аас engine үүсгэх
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if config.DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Өгөгдлийн санг эхлүүлж бүх хүснэгтүүдийг үүсгэх."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI-д зориулсан өгөгдлийн сангийн сешн авах dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
