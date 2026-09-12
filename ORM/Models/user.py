"""
Legacy / alternate User model (simpler version without address fields).

NOTE: The active model used by routes is in Models/databaseModel.py.
This file is kept for reference and is not imported by the running app.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from src.orm.databaseConnection import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
