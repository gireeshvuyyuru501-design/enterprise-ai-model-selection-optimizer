from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import Deployment, UseCase


class AIModelBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    provider: str = Field(min_length=2, max_length=120)
    supported_use_cases: list[UseCase]
    quality_score: float = Field(ge=0, le=1)
    cost_per_million_tokens: float = Field(ge=0)
    latency_ms: int = Field(gt=0)
    context_tokens: int = Field(gt=0)
    privacy_score: float = Field(ge=0, le=1)
    deployment: Deployment
    active: bool = True


class AIModelCreate(AIModelBase):
    pass


class AIModelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    provider: str | None = Field(default=None, min_length=2, max_length=120)
    supported_use_cases: list[UseCase] | None = None
    quality_score: float | None = Field(default=None, ge=0, le=1)
    cost_per_million_tokens: float | None = Field(default=None, ge=0)
    latency_ms: int | None = Field(default=None, gt=0)
    context_tokens: int | None = Field(default=None, gt=0)
    privacy_score: float | None = Field(default=None, ge=0, le=1)
    deployment: Deployment | None = None
    active: bool | None = None


class AIModelRead(AIModelBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OptimizationHistoryRead(BaseModel):
    id: UUID
    use_case: str
    selected_model: str
    score: float
    cost_limit: float
    latency_limit: int
    context_limit: int
    deployment: str
    privacy_required: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
