from app.models import SelectionRequest
from app.services.optimizer import optimize


def test_optimizer_returns_ranked_models() -> None:
    request = SelectionRequest(
        use_case="rag",
        max_cost_per_million_tokens=15,
        max_latency_ms=1500,
        minimum_context_tokens=32000,
        deployment="either",
        privacy_required=False,
        top_n=3,
    )
    response = optimize(request)
    assert response.recommendations
    assert response.recommendations[0].rank == 1
    assert "cost_per_million_tokens" in response.recommendations[0].metrics
