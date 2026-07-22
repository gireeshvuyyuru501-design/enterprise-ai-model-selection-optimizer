from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_db
from app.schemas.assistant import AssistantRequest, AssistantResponse
from app.services.ai_assistant import recommend_model

try:
    from app.database.models import AIModel
except ImportError:
    from app.database.models import Model as AIModel


router = APIRouter(
    prefix="/api/v1/assistant",
    tags=["AI Recommendation Assistant"],
)


@router.post("/recommend", response_model=AssistantResponse)
def recommend(
    payload: AssistantRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    models = db.query(AIModel).all()
    result = recommend_model(payload.question, models)

    return AssistantResponse(
        question=payload.question,
        recommendation=result["recommendation"],
        answer=result["answer"],
        evaluated_models=result["evaluated_models"],
    )


@router.get("/examples")
def examples(current_user=Depends(get_current_user)):
    return {
        "examples": [
            "Which model is cheapest for a customer-service chatbot?",
            "Recommend a fast model for a real-time application.",
            "Which model is best for complex reasoning?",
            "Recommend a model for RAG over long documents.",
            "Which model is best for private enterprise deployment?",
        ]
    }