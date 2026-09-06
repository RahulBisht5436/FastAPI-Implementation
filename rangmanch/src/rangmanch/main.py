from fastapi import FastAPI
from contextlib import asynccontextmanager
from Data.database import create_tables

# Importing the router
from Routes.reviews import route as reviews_router

@asynccontextmanager
async def lifespan(app:FastAPI):
    # when the server start it starts executing this function
    create_tables()
    print("database tables created")
    yield
    #we can clean up here 


app = FastAPI(
    title="Rang Manch App",
    description="App for the theritical drama",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Adding the router that we made
app.include_router(reviews_router)


@app.get("/api/root")
def root():
    return {
        "status": 200,
        "message": "system is healthy"
    }