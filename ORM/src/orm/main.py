"""
FastAPI application entry point.

Wires together the database lifespan hook, API routers, and health-check endpoint.
Run with: uvicorn orm.main:app --reload
"""

from fastapi import FastAPI
from Models.databaseModel import User  # noqa: F401 — imported so SQLAlchemy registers the model before create_all
from src.orm.databaseConnection import engine, Base
from contextlib import asynccontextmanager
from Routes.user import router as user_router
from Routes.login import router as login_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup if they do not already exist."""
    Base.metadata.create_all(engine)
    print("Database created")
    yield


app = FastAPI(
    title="ORM",
    description="ORM for the database",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


@app.get("/")
def read_root():
    """Simple health-check endpoint."""
    return {"message": "Server is running and is healthy"}


# Mount route modules — each router defines its own prefix and tags
app.include_router(user_router)
app.include_router(login_router)
