from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class GoalDB(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    field_id: Mapped[int | None] = mapped_column(ForeignKey("fields.id", ondelete="SET NULL"), nullable=True, index=True)
    text: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    objective: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    crop: Mapped[str | None] = mapped_column(String(120), nullable=True)
    target_yield_change_percent: Mapped[float | None] = mapped_column(nullable=True)
    water_reduction_percent: Mapped[float | None] = mapped_column(nullable=True)
    priority: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)

    farm: Mapped["FarmDB"] = relationship(back_populates="goals")
    field: Mapped["FieldDB | None"] = relationship()
    plans: Mapped[list["PlanDB"]] = relationship(back_populates="goal", cascade="all, delete-orphan")
