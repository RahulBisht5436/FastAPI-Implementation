from pydantic import BaseModel
from typing import List, Optional

class RAGModelQuery(BaseModel):
    query: str

class RAGModelResponse(BaseModel):
    response: str
    source: Optional[List[str]] = None
    