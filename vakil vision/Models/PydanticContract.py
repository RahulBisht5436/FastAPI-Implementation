from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ContractAnalysisBase(BaseModel):
    """Fields extracted by the LLM from contract text."""

    name: str
    description: str
    terms: List[str]
    conditions: List[str]
    liabilities: List[str]
    rights: List[str]
    obligations: List[str]
    guarantees: List[str]
    warranties: List[str]
    analysis: str


class ContractAnalysis(ContractAnalysisBase):
    """Full analysis record stored or returned by the API."""

    analyzed_at: datetime = Field(default_factory=datetime.now)
