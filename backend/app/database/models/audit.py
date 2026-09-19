from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AuditEventDB(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    farm_id: Mapped[int | None] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True)
    plan_id: Mapped[int | None] = mapped_column(ForeignKey("plans.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)

    farm: Mapped["FarmDB | None"] = relationship(back_populates="audit_events")
    plan: Mapped["PlanDB | None"] = relationship(back_populates="audit_events")

    def __getattribute__(self, name: str):
        """Return the legacy JSON payload for metadata while keeping SQLAlchemy internals intact."""
        if name == "metadata":
            return object.__getattribute__(self, "event_metadata")
        return object.__getattribute__(self, name)

    def __getattr__(self, name: str):
        """Backward-compatible alias for legacy access to the JSON metadata payload."""
        if name == "metadata":
            return self.event_metadata
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    def __setattr__(self, name: str, value):
        """Persist legacy metadata assignment onto the SQLAlchemy column backing the DB field."""
        if name == "metadata":
            object.__setattr__(self, "event_metadata", value or {})
            return
        object.__setattr__(self, name, value)
