import json

from sqlalchemy.orm import Session

from app.crud.model_crud import save_history
from app.database.models import AIModel, OptimizationHistory
from app.models import RankedModel, SelectionRequest, SelectionResponse


def _deployment_matches(requested: str, candidate: str) -> bool:
    return requested == "either" or candidate == "either" or requested == candidate


def _normalize_cost(cost: float, max_cost: float) -> float:
    return max(0.0, min(1.0, 1.0 - (cost / max_cost)))


def _normalize_latency(latency: int, max_latency: int) -> float:
    return max(0.0, min(1.0, 1.0 - (latency / max_latency)))


def _normalize_context(context: int, minimum_context: int) -> float:
    return min(1.0, context / minimum_context)


def optimize(
    request: SelectionRequest,
    candidates: list[AIModel],
    db: Session,
) -> SelectionResponse:
    eligible: list[AIModel] = []

    for candidate in candidates:
        if request.use_case not in candidate.supported_use_cases:
            continue
        if candidate.cost_per_million_tokens > request.max_cost_per_million_tokens:
            continue
        if candidate.latency_ms > request.max_latency_ms:
            continue
        if candidate.context_tokens < request.minimum_context_tokens:
            continue
        if not _deployment_matches(request.deployment, candidate.deployment):
            continue
        if request.privacy_required and candidate.privacy_score < 0.9:
            continue
        eligible.append(candidate)

    ranked: list[RankedModel] = []

    for candidate in eligible:
        breakdown = {
            "quality": candidate.quality_score,
            "cost": _normalize_cost(
                candidate.cost_per_million_tokens,
                request.max_cost_per_million_tokens,
            ),
            "latency": _normalize_latency(
                candidate.latency_ms,
                request.max_latency_ms,
            ),
            "context": _normalize_context(
                candidate.context_tokens,
                request.minimum_context_tokens,
            ),
            "privacy": candidate.privacy_score,
        }

        weights = request.weights
        total = (
            breakdown["quality"] * weights.quality
            + breakdown["cost"] * weights.cost
            + breakdown["latency"] * weights.latency
            + breakdown["context"] * weights.context
            + breakdown["privacy"] * weights.privacy
        )

        ranked.append(
            RankedModel(
                rank=0,
                name=candidate.name,
                provider=candidate.provider,
                total_score=round(total, 4),
                score_breakdown={key: round(value, 4) for key, value in breakdown.items()},
                metrics={
                    "cost_per_million_tokens": candidate.cost_per_million_tokens,
                    "latency_ms": candidate.latency_ms,
                    "context_tokens": candidate.context_tokens,
                    "privacy_score": candidate.privacy_score,
                    "deployment": candidate.deployment,
                },
                explanation=[
                    f"Strong fit for {request.use_case} workloads.",
                    (
                        f"Estimated cost is "
                        f"${candidate.cost_per_million_tokens:.2f} per million tokens."
                    ),
                    f"Estimated latency is {candidate.latency_ms} ms.",
                    f"Supports a {candidate.context_tokens:,}-token context window.",
                    f"Deployment mode: {candidate.deployment}.",
                ],
            )
        )

    ranked.sort(key=lambda model: model.total_score, reverse=True)
    ranked = ranked[: request.top_n]

    for index, model in enumerate(ranked, start=1):
        model.rank = index

    if ranked:
        best = ranked[0]
        save_history(
            db,
            OptimizationHistory(
                use_case=request.use_case,
                selected_model=best.name,
                score=best.total_score,
                cost_limit=request.max_cost_per_million_tokens,
                latency_limit=request.max_latency_ms,
                context_limit=request.minimum_context_tokens,
                deployment=request.deployment,
                privacy_required=request.privacy_required,
                request_payload=json.dumps(request.model_dump()),
            ),
        )

    return SelectionResponse(
        request_summary={
            "use_case": request.use_case,
            "deployment": request.deployment,
            "privacy_required": request.privacy_required,
            "max_cost_per_million_tokens": request.max_cost_per_million_tokens,
            "max_latency_ms": request.max_latency_ms,
            "minimum_context_tokens": request.minimum_context_tokens,
        },
        recommendations=ranked,
        evaluated_models=len(candidates),
        eligible_models=len(eligible),
    )
