from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.database.base import Base

_engine = None
SessionLocal = None


def _make_engine() -> Any:
    return create_engine(settings.database_url_resolved, connect_args={"check_same_thread": False}, future=True)


def _ensure_session_factory() -> None:
    global _engine, SessionLocal
    if _engine is None or SessionLocal is None:
        _engine = _make_engine()
        SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)

        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
            """Ensure SQLite behaves predictably in local development."""
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.close()


_ensure_session_factory()


def get_db_session() -> Generator[Session, None, None]:
    """Yield a database session for each request or unit of work."""
    _ensure_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create the local SQLite schema for the current application."""
    _ensure_session_factory()
    Base.metadata.create_all(bind=_engine)
    _ensure_field_context_columns()
    from app.services.fields import ensure_demo_field_exists

    ensure_demo_field_exists()


def _ensure_field_context_columns() -> None:
    """Add the new nullable field links to pre-Step-13 SQLite tables if needed."""
    if _engine.dialect.name != "sqlite":
        return
    with _engine.begin() as connection:
        inspector = inspect(connection)
        for table_name in ("goals", "plans"):
            columns = {column["name"] for column in inspector.get_columns(table_name)}
            if "field_id" not in columns:
                connection.execute(
                    text(f"ALTER TABLE {table_name} ADD COLUMN field_id INTEGER REFERENCES fields(id)")
                )
