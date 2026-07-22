from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.model_crud import (
    create_model,
    delete_model,
    get_model,
    list_history,
    list_models,
    update_model,
)
from app.database.database import get_db
from app.models import SelectionRequest, SelectionResponse
from app.schemas.model_schema import (
    AIModelCreate,
    AIModelRead,
    AIModelUpdate,
    OptimizationHistoryRead,
)
from app.services.optimizer import optimize

router = APIRouter(prefix="/api/v1")


@router.post(
    "/select-model",
    response_model=SelectionResponse,
    tags=["Model Selection"],
)
def select_model(
    request: SelectionRequest,
    db: Session = Depends(get_db),
) -> SelectionResponse:
    candidates = list_models(db, active_only=True)
    return optimize(request, candidates, db)


@router.get(
    "/models",
    response_model=list[AIModelRead],
    tags=["Model Catalog"],
)
def get_models(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
) -> list[AIModelRead]:
    return list_models(db, active_only=not include_inactive)


@router.post(
    "/models",
    response_model=AIModelRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Model Catalog"],
)
def add_model(
    payload: AIModelCreate,
    db: Session = Depends(get_db),
) -> AIModelRead:
    try:
        return create_model(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A model with this name already exists.",
        ) from exc


@router.get(
    "/models/{model_id}",
    response_model=AIModelRead,
    tags=["Model Catalog"],
)
def read_model(
    model_id: UUID,
    db: Session = Depends(get_db),
) -> AIModelRead:
    model = get_model(db, model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found.")
    return model


@router.put(
    "/models/{model_id}",
    response_model=AIModelRead,
    tags=["Model Catalog"],
)
def edit_model(
    model_id: UUID,
    payload: AIModelUpdate,
    db: Session = Depends(get_db),
) -> AIModelRead:
    model = get_model(db, model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found.")
    return update_model(db, model, payload)


@router.delete(
    "/models/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Model Catalog"],
)
def remove_model(
    model_id: UUID,
    db: Session = Depends(get_db),
) -> Response:
    model = get_model(db, model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found.")
    delete_model(db, model)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/history",
    response_model=list[OptimizationHistoryRead],
    tags=["Optimization History"],
)
def get_optimization_history(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[OptimizationHistoryRead]:
    return list_history(db, limit=limit)
