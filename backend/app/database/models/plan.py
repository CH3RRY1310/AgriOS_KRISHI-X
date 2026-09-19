from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PlanDB(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    field_id: Mapped[int | None] = mapped_column(ForeignKey("fields.id", ondelete="SET NULL"), nullable=True, index=True)
    goal_id: Mapped[int | None] = mapped_column(ForeignKey("goals.id", ondelete="SET NULL"), nullable=True, index=True)
    external_plan_id: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: f"plan-{uuid4().hex[:12]}",
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="awaiting_approval")
    decision: Mapped[str] = mapped_column(String(200), nullable=False, default="REVIEW_PLAN")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_water_saved_liters: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    expected_water_reduction_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    farm: Mapped["FarmDB"] = relationship(back_populates="plans")
    field: Mapped["FieldDB | None"] = relationship()
    goal: Mapped["GoalDB | None"] = relationship(back_populates="plans")
    approval: Mapped["ApprovalDB | None"] = relationship(back_populates="plan", cascade="all, delete-orphan")
    audit_events: Mapped[list["AuditEventDB"]] = relationship(back_populates="plan", cascade="all, delete-orphan")
