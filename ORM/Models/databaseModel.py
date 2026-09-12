"""
Data models for the application.

Contains three layers:
  - User        → SQLAlchemy ORM model (maps to the `users` table in PostgreSQL)
  - UserCreate  → Pydantic schema for validating incoming create requests
  - UserUpdate  → Pydantic schema for validating partial update requests (all fields optional)
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from src.orm.databaseConnection import Base
from pydantic import BaseModel
from typing import Optional


class User(Base):
    """SQLAlchemy model — represents a row in the `users` table."""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)  # stored as a bcrypt hash, never plain text
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip = Column(String, nullable=True)
    country = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)   # soft-delete flag
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)


class UserCreate(BaseModel):
    """Request body schema for POST /user/create."""

    name: str
    email: str
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    is_admin: Optional[bool] = False
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False
    is_verified: Optional[bool] = False
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
    deleted_at: Optional[datetime] = datetime.now()


class UserUpdate(BaseModel):
    """Request body schema for PUT /user/edit/{user_id} — only send fields you want to change."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
