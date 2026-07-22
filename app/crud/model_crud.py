from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import AIModel, OptimizationHistory
from app.schemas.model_schema import AIModelCreate, AIModelUpdate


def list_models(db: Session, active_only: bool = True) -> list[AIModel]:
    statement = select(AIModel).order_by(AIModel.provider, AIModel.name)
    if active_only:
        statement = statement.where(AIModel.active.is_(True))
    return list(db.scalars(statement).all())


def get_model(db: Session, model_id: UUID) -> AIModel | None:
    return db.get(AIModel, model_id)


def create_model(db: Session, payload: AIModelCreate) -> AIModel:
    model = AIModel(**payload.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def update_model(db: Session, model: AIModel, payload: AIModelUpdate) -> AIModel:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(model, field, value)
    db.commit()
    db.refresh(model)
    return model


def delete_model(db: Session, model: AIModel) -> None:
    db.delete(model)
    db.commit()


def save_history(db: Session, history: OptimizationHistory) -> OptimizationHistory:
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def list_history(db: Session, limit: int = 50) -> list[OptimizationHistory]:
    statement = (
        select(OptimizationHistory)
        .order_by(OptimizationHistory.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(statement).all())
