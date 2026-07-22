from app.schemas.model_schema import AIModelCreate


def test_ai_model_schema() -> None:
    model = AIModelCreate(
        name="TestModel",
        provider="TestProvider",
        supported_use_cases=["rag"],
        quality_score=0.9,
        cost_per_million_tokens=4.0,
        latency_ms=500,
        context_tokens=64000,
        privacy_score=0.8,
        deployment="cloud",
    )
    assert model.name == "TestModel"
    assert model.supported_use_cases == ["rag"]
