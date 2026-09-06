from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from Database.database import initialize_database
from Routes.chat import router as chat_router
from Routes.contracts import router as contracts_router
from Routes.llm import router as llm_router

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Vakil Vision",
    description="Vakil Vision is a platform for vision-based AI solutions",
    version="0.1.0",
    contact={
        "name": "Vakil Vision",
        "url": "https://vakilvision.com",
        "email": "contact@vakilvision.com",
    },
    lifespan=lifespan,
    license_info={
        "name": "MIT License",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contracts_router)
app.include_router(chat_router)
app.include_router(llm_router)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def home():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Vakil Vision API is running. Visit /docs for API docs."}


@app.get("/healthcheck")
async def health():
    return {"status": "ok"}
