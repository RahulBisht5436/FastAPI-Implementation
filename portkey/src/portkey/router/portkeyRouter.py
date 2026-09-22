from fastapi import APIRouter, HTTPException

from portkey.graph.llm_graph import llm_graph
from portkey.schemas.query import QueryRequest, QueryResponse

portkeyRouter = APIRouter()


@portkeyRouter.post("/query", response_model=QueryResponse)
async def query(body: QueryRequest) -> QueryResponse:
    try:
        result = await llm_graph.ainvoke({"user_message": body.message})
        return QueryResponse(response=result["llm_response"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
