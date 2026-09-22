from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User prompt for the LLM")


class QueryResponse(BaseModel):
    response: str
