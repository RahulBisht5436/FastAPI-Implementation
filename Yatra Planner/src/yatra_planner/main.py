from fastapi import FastAPI
from Routes.planner import planner_router

app = FastAPI(
    title="Yatra Planner",
    description="Yatra Planner is a tool that helps you plan your trip to a new place.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    
)

app.include_router(planner_router)

@app.get("/")
async def root():
    return {
        "app_name": "Yatra Planner",
        "app_description": "Yatra Planner is a tool that helps you plan your trip to a new place.",
        "app_version": "0.1.0",
        "app_docs_url": "/docs",
        "app_redoc_url": "/redoc",
        "app_openapi_url": "/openapi.json",
        "endpoints":{
            "POST /plan": "Create a travel plan (Aggregated)",
            "GET /plan/stream": "Stream a travel plan (SSE)",
            "GET /plan/cache-stats": "View Cache statistics for travel plans",
            "DELETE /plan/cache": "Clear Cache for travel plans",
        }
    }
    