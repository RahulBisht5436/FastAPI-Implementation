# Book-related database models and API schemas.
# Each book belongs to one user via the user_id foreign key.

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

# Database table model — maps to a "book" table in the database.
class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    author: str = Field(index=True)
    description: str
    price: float
    # Defaults to False when a new book is created.
    is_sold: bool = Field(default=False)
    
    # Foreign key links this book to a row in the users table.
    user_id: int = Field(foreign_key="users.id")
    # Many-to-one relationship: many books can belong to one user.
    user: Optional["Users"] = Relationship(back_populates="books")
    # this is a relationship between the book and the user model
    
    
# Schema for creating a new book via API request body.
# Requires user_id to associate the book with an existing user.
class BookCreate(SQLModel):
    title: str
    author: str
    description: str
    price: float
    is_sold: bool = False
    user_id: int

# Schema for returning book data in API responses.
class BookRead(SQLModel):
    id: int
    title: str
    author: str
    description: str
    price: float
    is_sold: bool
    user_id: int
    
    
# Deferred import avoids circular dependency with user.py (same pattern as user.py).
# model_rebuild() resolves any forward references on the Book model.
from .user import Users
Book.model_rebuild()
