from contextlib import asynccontextmanager

from fastapi import FastAPI
from Models.model import Order, OrderCreated, OrderUpdated, StatusLog
from sqlmodel import SQLModel
from Routes.order import router as order_router
from Routes.stats import router as stats_router
from dabbewale.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    
    title="Dabbewale",
    description="A simple order management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


app.include_router(order_router)
app.include_router(stats_router)