from typing import Any


def _value(model: Any, *names: str, default=None):
    for name in names:
        if hasattr(model, name):
            value = getattr(model, name)
            if value is not None:
                return value
    return default


def _number(model: Any, *names: str, default: float = 0.0) -> float:
    value = _value(model, *names, default=default)

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def recommend_model(question: str, models: list[Any]) -> dict:
    text = question.lower().strip()
    ranked = []

    for model in models:
        score = 50.0
        reasons = []

        name = str(_value(model, "name", "model_name", default="Unknown Model"))
        provider = str(_value(model, "provider", default="Unknown"))

        cost = _number(
            model,
            "cost_per_1m_tokens",
            "cost",
            "input_cost",
            "price",
            default=0.0,
        )

        latency = _number(
            model,
            "latency_ms",
            "latency",
            "response_time_ms",
            default=0.0,
        )

        accuracy = _number(
            model,
            "accuracy_score",
            "accuracy",
            "quality_score",
            "performance_score",
            default=0.0,
        )

        context_window = _number(
            model,
            "context_window",
            "context_length",
            "max_tokens",
            default=0.0,
        )

        privacy = str(
            _value(
                model,
                "privacy_level",
                "deployment_type",
                "hosting",
                default="",
            )
        ).lower()

        model_text = f"{name} {provider}".lower()

        if any(word in text for word in ["cheap", "low cost", "budget", "cost effective"]):
            score += max(0, 30 - cost)
            reasons.append("Strong cost efficiency for a budget-focused workload")

        if any(word in text for word in ["fast", "latency", "real time", "realtime"]):
            score += max(0, 30 - latency / 100)
            reasons.append("Suitable for latency-sensitive or real-time usage")

        if any(word in text for word in ["accurate", "accuracy", "quality", "reasoning", "complex"]):
            score += accuracy * 0.3
            reasons.append("Strong quality and reasoning suitability")

        if any(word in text for word in ["long document", "large context", "context window", "documents"]):
            score += min(context_window / 10000, 30)
            reasons.append("Useful context capacity for large documents")

        if any(word in text for word in ["private", "privacy", "secure", "on premise", "on-premise"]):
            if any(word in privacy for word in ["private", "on-prem", "local", "self-hosted"]):
                score += 30
                reasons.append("Matches privacy or private-deployment requirements")

        if "openai" in text and "openai" in model_text:
            score += 35
            reasons.append("Matches the requested OpenAI provider")

        if "anthropic" in text and ("anthropic" in model_text or "claude" in model_text):
            score += 35
            reasons.append("Matches the requested Anthropic/Claude provider")

        if "google" in text and ("google" in model_text or "gemini" in model_text):
            score += 35
            reasons.append("Matches the requested Google/Gemini provider")

        if "aws" in text and ("aws" in model_text or "bedrock" in model_text):
            score += 35
            reasons.append("Matches the requested AWS/Bedrock ecosystem")

        if "coding" in text or "code" in text:
            if any(word in model_text for word in ["gpt", "claude", "gemini", "code"]):
                score += 15
                reasons.append("Suitable for code-generation and developer-assistance tasks")

        if "rag" in text or "retrieval" in text:
            if context_window > 0:
                score += min(context_window / 20000, 20)
            reasons.append("Suitable for retrieval-augmented generation workflows")

        if not reasons:
            reasons.append("Best overall match based on the available catalog attributes")
            score += accuracy * 0.1

        ranked.append(
            {
                "model": model,
                "score": round(score, 2),
                "reasons": reasons[:4],
                "name": name,
                "provider": provider,
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)

    if not ranked:
        return {
            "recommendation": None,
            "answer": "No AI models are currently available in the catalog.",
            "evaluated_models": 0,
        }

    winner = ranked[0]
    model = winner["model"]

    answer = (
        f"I recommend {winner['name']} from {winner['provider']}. "
        f"It received a suitability score of {winner['score']}. "
        f"Primary reasons: {'; '.join(winner['reasons'])}."
    )

    return {
        "recommendation": {
            "id": int(_value(model, "id", default=0)),
            "name": winner["name"],
            "provider": winner["provider"],
            "score": winner["score"],
            "reasons": winner["reasons"],
        },
        "answer": answer,
        "evaluated_models": len(ranked),
    }