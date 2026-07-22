from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class RecommendedModel(BaseModel):
    id: int
    name: str
    provider: str | None = None
    score: float
    reasons: list[str]


class AssistantResponse(BaseModel):
    question: str
    recommendation: RecommendedModel | None
    answer: str
    evaluated_models: int