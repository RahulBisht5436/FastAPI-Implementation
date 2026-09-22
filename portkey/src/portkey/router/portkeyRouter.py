from fastapi import APIRouter, HTTPException, Request

portkeyRouter = APIRouter()

@portkeyRouter.post("/query")
def query(request: Request):
    try:
        return {"message": "OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))