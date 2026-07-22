from sqlalchemy import select

from app.database.database import Base, SessionLocal, engine
from app.database.models import AIModel


SEED_MODELS = [
    {
        "name": "Atlas-Pro",
        "provider": "ExampleCloud",
        "supported_use_cases": ["rag", "chatbot", "summarization", "agents"],
        "quality_score": 0.94,
        "cost_per_million_tokens": 12.0,
        "latency_ms": 850,
        "context_tokens": 200000,
        "privacy_score": 0.75,
        "deployment": "cloud",
    },
    {
        "name": "Nova-Fast",
        "provider": "ExampleAI",
        "supported_use_cases": ["rag", "chatbot", "summarization"],
        "quality_score": 0.86,
        "cost_per_million_tokens": 3.5,
        "latency_ms": 280,
        "context_tokens": 128000,
        "privacy_score": 0.70,
        "deployment": "cloud",
    },
    {
        "name": "CodeForge",
        "provider": "ExampleLabs",
        "supported_use_cases": ["coding", "agents"],
        "quality_score": 0.91,
        "cost_per_million_tokens": 8.0,
        "latency_ms": 600,
        "context_tokens": 128000,
        "privacy_score": 0.72,
        "deployment": "cloud",
    },
    {
        "name": "LocalGuard-70B",
        "provider": "OpenModels",
        "supported_use_cases": ["rag", "chatbot", "coding", "summarization", "agents"],
        "quality_score": 0.83,
        "cost_per_million_tokens": 2.0,
        "latency_ms": 1200,
        "context_tokens": 64000,
        "privacy_score": 1.0,
        "deployment": "local",
    },
    {
        "name": "Compact-8B",
        "provider": "OpenModels",
        "supported_use_cases": ["rag", "chatbot", "summarization"],
        "quality_score": 0.72,
        "cost_per_million_tokens": 0.5,
        "latency_ms": 180,
        "context_tokens": 32000,
        "privacy_score": 1.0,
        "deployment": "local",
    },
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        existing = set(db.scalars(select(AIModel.name)).all())
        created = 0

        for payload in SEED_MODELS:
            if payload["name"] not in existing:
                db.add(AIModel(**payload))
                created += 1

        db.commit()
        print(f"Database seed completed. Added {created} model(s).")


if __name__ == "__main__":
    seed()
