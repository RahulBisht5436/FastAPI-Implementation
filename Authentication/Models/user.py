# User-related database models and API schemas.
# SQLModel combines SQLAlchemy (database ORM) and Pydantic (data validation) in one library.
#
# This file defines three related classes:
#   - Users      → the actual database table (persisted data)
#   - UserCreate → shape of JSON sent when creating a user (request body)
#   - UserRead   → shape of JSON returned when reading a user (API response)

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


# ---------------------------------------------------------------------------
# TABLE MODEL — persisted in the database
# ---------------------------------------------------------------------------
class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    college: str

    # One-to-many: one user can own many books.
    # "Book" is quoted (forward reference) because Book is defined in books.py.
    books: list["Book"] = Relationship(back_populates="user")


# ---------------------------------------------------------------------------
# CREATE SCHEMA — used for POST /users request bodies
# ---------------------------------------------------------------------------
class UserCreate(SQLModel):
    name: str
    email: str
    college: str


# ---------------------------------------------------------------------------
# READ SCHEMA — used for API responses (GET endpoints, response_model)
# ---------------------------------------------------------------------------
class UserRead(SQLModel):
    id: int
    name: str
    email: str
    college: str
    books: list["Book"]


# ---------------------------------------------------------------------------
# CIRCULAR IMPORT FIX — import Book after class definitions, then rebuild model
# ---------------------------------------------------------------------------
from .books import Book

Users.model_rebuild()
