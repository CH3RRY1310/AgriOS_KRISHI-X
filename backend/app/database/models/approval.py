from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ApprovalDB(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    decision: Mapped[str] = mapped_column(String(50), nullable=False, default="approve")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    execution_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="simulation_only")
    executed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    farmer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    modified_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)

    plan: Mapped["PlanDB"] = relationship(back_populates="approval")
