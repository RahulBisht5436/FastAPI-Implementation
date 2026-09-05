# Application entry point — creates the FastAPI app and mounts all routers.

from fastapi import FastAPI
from Router.users import router as user_router
from Router.books import router as book_router
from contextlib import asynccontextmanager
from Database.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create the database and tables
    create_db_and_tables()
    yield


# FastAPI instance: the main web application object.
# Metadata below appears in the auto-generated API docs (Swagger UI and ReDoc).

app = FastAPI(
    title="Authentication API",
    description="API for authentication",
    version="1.0.0",
    docs_url="/docs",           # Swagger UI — interactive API explorer
    redoc_url="/redoc" ,        # ReDoc — alternative API documentation view
    openapi_url="/openapi.json", # Raw OpenAPI schema (used by tools and clients)
    lifespan=lifespan
    
)

# Mount routers so their endpoints become part of the app.
app.include_router(user_router)
app.include_router(book_router)
