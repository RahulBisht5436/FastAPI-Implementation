"""
Database connection and session management.

Reads DB_URL from .env, creates a SQLAlchemy engine and session factory,
and exposes get_db() as a FastAPI dependency for per-request DB sessions.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Connection string format: postgresql://user:password@host:port/database
url = os.getenv("DB_URL")
engine = create_engine(url, echo=True)  # echo=True logs every SQL statement to the console
sessionPool = sessionmaker(bind=engine)

# Shared declarative base — all SQLAlchemy models inherit from this
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a DB session and closes it after the request.

    Usage in routes: db: Session = Depends(get_db)
    """
    db = sessionPool()
    try:
        yield db
    finally:
        db.close()
