from typing import Literal

from pydantic import BaseModel, Field, model_validator


UseCase = Literal["rag", "chatbot", "coding", "summarization", "agents"]
Deployment = Literal["cloud", "local", "either"]


class SelectionWeights(BaseModel):
    quality: float = Field(default=0.35, ge=0, le=1)
    cost: float = Field(default=0.25, ge=0, le=1)
    latency: float = Field(default=0.20, ge=0, le=1)
    context: float = Field(default=0.10, ge=0, le=1)
    privacy: float = Field(default=0.10, ge=0, le=1)

    @model_validator(mode="after")
    def validate_total(self) -> "SelectionWeights":
        total = self.quality + self.cost + self.latency + self.context + self.privacy
        if abs(total - 1.0) > 0.0001:
            raise ValueError(f"Weights must total 1.0; received {total:.4f}")
        return self


class SelectionRequest(BaseModel):
    use_case: UseCase
    max_cost_per_million_tokens: float = Field(gt=0)
    max_latency_ms: int = Field(gt=0)
    minimum_context_tokens: int = Field(gt=0)
    deployment: Deployment = "either"
    privacy_required: bool = False
    top_n: int = Field(default=3, ge=1, le=10)
    weights: SelectionWeights = Field(default_factory=SelectionWeights)


class ModelCandidate(BaseModel):
    name: str
    provider: str
    supported_use_cases: list[UseCase]
    quality_score: float
    cost_per_million_tokens: float
    latency_ms: int
    context_tokens: int
    privacy_score: float
    deployment: Deployment


class RankedModel(BaseModel):
    rank: int
    name: str
    provider: str
    total_score: float
    score_breakdown: dict[str, float]
    metrics: dict[str, float | int | str]
    explanation: list[str]


class SelectionResponse(BaseModel):
    request_summary: dict[str, object]
    recommendations: list[RankedModel]
    evaluated_models: int
    eligible_models: int
