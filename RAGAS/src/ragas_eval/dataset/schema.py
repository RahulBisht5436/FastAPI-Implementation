from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SampleCategory(str, Enum):
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    SKILLS = "skills"
    PROJECTS = "projects"
    RESUME_LINKS = "resume_links"
    NEGATIVE = "negative"
    ADVERSARIAL = "adversarial"


class GoldenSample(BaseModel):
    id: str
    question: str
    ground_truth: str
    category: SampleCategory
    difficulty: str = "medium"
    tags: list[str] = Field(default_factory=list)
    reference_contexts: list[str] = Field(default_factory=list)
    skip_generation: bool = False


class GoldenDataset(BaseModel):
    version: str
    kb_manifest_hash: str | None = None
    require_manifest_match: bool = True
    samples: list[GoldenSample]

    @field_validator("samples")
    @classmethod
    def validate_unique_ids(cls, samples: list[GoldenSample]) -> list[GoldenSample]:
        ids = [sample.id for sample in samples]
        if len(ids) != len(set(ids)):
            raise ValueError("Golden dataset sample ids must be unique.")
        return samples


class EvalTraceRow(BaseModel):
    sample_id: str
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    category: str
    context_metadata: list[dict[str, Any]] = Field(default_factory=list)
    retrieval_latency_ms: float | None = None
    generation_latency_ms: float | None = None
    error: str | None = None
