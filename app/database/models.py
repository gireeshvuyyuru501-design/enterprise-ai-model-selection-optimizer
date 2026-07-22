from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class AIModel(Base):
    __tablename__ = "ai_models"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    supported_use_cases: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    cost_per_million_tokens: Mapped[float] = mapped_column(Float, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    context_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    privacy_score: Mapped[float] = mapped_column(Float, nullable=False)
    deployment: Mapped[str] = mapped_column(String(20), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class OptimizationHistory(Base):
    __tablename__ = "optimization_history"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    use_case: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    selected_model: Mapped[str] = mapped_column(String(120), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    cost_limit: Mapped[float] = mapped_column(Float, nullable=False)
    latency_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    context_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    deployment: Mapped[str] = mapped_column(String(20), nullable=False)
    privacy_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    request_payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
