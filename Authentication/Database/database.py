# Database connection and session management.
# This module sets up SQLite, provides DB sessions to route handlers, and creates tables.

from sqlmodel import create_engine ,Session ,SQLModel
# Import models so SQLModel registers their tables before create_all() runs.
from Models.user import Users
from Models.books import Book

# create_engine opens a connection pool to the database.
# "sqlite:///database.db" stores data in a local file named database.db in the project root.
# echo=True prints all SQL statements to the console — useful for debugging during development.
engine = create_engine("sqlite:///database.db",echo=True)

# FastAPI dependency: yields a database session per request, then closes it automatically.
# "yield" makes this a generator — FastAPI calls it, uses the session, then continues after yield to clean up.
def get_session():
    with Session(engine) as session:
        yield session

# Creates all tables defined by SQLModel classes (Users, Book) if they don't exist yet.
# Call this once on app startup before handling any requests.
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
