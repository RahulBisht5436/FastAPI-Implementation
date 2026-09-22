from fastapi import FastAPI

from portkey.router.portkeyRouter import portkeyRouter

app = FastAPI(title="Portkey LLM Gateway")

app.include_router(portkeyRouter, prefix="/api", tags=["llm"])


@app.get("/health")
def root():
    return {"message": "OK"}









