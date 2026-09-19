from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import FarmDB, FieldDB
from app.schemas.field import FieldCreate, FieldResponse, FieldUpdate
from app.services.persistence import DEMO_FARM_EXTERNAL_ID, ensure_demo_farm_exists

DEMO_FIELD_EXTERNAL_ID = "field-demo-001"


def _to_response(field: FieldDB) -> FieldResponse:
    """Convert a persisted field to its public API representation."""
    return FieldResponse(
        id=field.external_id,
        farm_id=field.farm.external_id or str(field.farm_id),
        name=field.name,
        area_acres=field.area_acres,
        location=field.location,
        description=field.description,
        crop=field.crop,
        variety=field.variety,
        growth_stage=field.growth_stage,
        created_at=field.created_at,
        updated_at=field.updated_at,
    )


def ensure_demo_field_exists(session: Session | None = None) -> FieldDB:
    """Create the deterministic demo field once without overwriting user changes."""
    owns_session = session is None
    db = session or SessionLocal()
    try:
        existing = db.scalar(select(FieldDB).where(FieldDB.external_id == DEMO_FIELD_EXTERNAL_ID))
        if existing is not None:
            return existing

        farm = ensure_demo_farm_exists(db)
        field = FieldDB(
            external_id=DEMO_FIELD_EXTERNAL_ID,
            farm_id=farm.id,
            name="Field A",
            area_acres=farm.area,
            location=farm.location,
            description="Primary tomato demonstration field.",
            crop="tomato",
            variety="Sahyadri",
            growth_stage="flowering",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(field)
        db.commit()
        db.refresh(field)
        return field
    finally:
        if owns_session:
            db.close()


def list_fields_for_farm(farm_id: str, session: Session | None = None) -> list[FieldResponse]:
    """List fields belonging to a farm external ID."""
    owns_session = session is None
    db = session or SessionLocal()
    try:
        farm = db.scalar(select(FarmDB).where(FarmDB.external_id == farm_id))
        if farm is None:
            raise LookupError("farm not found")
        fields = db.execute(select(FieldDB).where(FieldDB.farm_id == farm.id).order_by(FieldDB.id.asc())).scalars().all()
        return [_to_response(field) for field in fields]
    finally:
        if owns_session:
            db.close()


def get_field(field_id: str, session: Session | None = None) -> FieldResponse | None:
    """Return one field by external ID."""
    owns_session = session is None
    db = session or SessionLocal()
    try:
        field = db.scalar(select(FieldDB).where(FieldDB.external_id == field_id))
        return _to_response(field) if field is not None else None
    finally:
        if owns_session:
            db.close()


def create_field(farm_id: str, payload: FieldCreate, session: Session | None = None) -> FieldResponse:
    """Create and persist a field under an existing farm."""
    owns_session = session is None
    db = session or SessionLocal()
    try:
        farm = db.scalar(select(FarmDB).where(FarmDB.external_id == farm_id))
        if farm is None:
            raise LookupError("farm not found")
        external_id = payload.id or f"field-{uuid4().hex[:12]}"
        if db.scalar(select(FieldDB).where(FieldDB.external_id == external_id)) is not None:
            raise ValueError("field already exists")
        field = FieldDB(
            external_id=external_id,
            farm_id=farm.id,
            **payload.model_dump(exclude={"id"}),
        )
        db.add(field)
        db.commit()
        db.refresh(field)
        return _to_response(field)
    finally:
        if owns_session:
            db.close()


def update_field(field_id: str, payload: FieldUpdate, session: Session | None = None) -> FieldResponse | None:
    """Update allowed field properties and persist the result."""
    owns_session = session is None
    db = session or SessionLocal()
    try:
        field = db.scalar(select(FieldDB).where(FieldDB.external_id == field_id))
        if field is None:
            return None
        for name, value in payload.model_dump(exclude_unset=True).items():
            setattr(field, name, value)
        field.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(field)
        return _to_response(field)
    finally:
        if owns_session:
            db.close()


def resolve_planning_scope(
    farm_id: str | None,
    field_id: str | None,
    session: Session | None = None,
) -> tuple[str | None, FieldResponse | None]:
    """Validate and resolve optional farm/field planning scope."""
    if farm_id is None and field_id is None:
        return None, None
    if field_id is not None and farm_id is None:
        raise ValueError("farm_id is required when field_id is provided")

    owns_session = session is None
    db = session or SessionLocal()
    try:
        farm = db.scalar(select(FarmDB).where(FarmDB.external_id == farm_id))
        if farm is None:
            raise LookupError("farm not found")
        if field_id is None:
            return farm.external_id, None

        field = db.scalar(select(FieldDB).where(FieldDB.external_id == field_id))
        if field is None:
            raise LookupError("field not found")
        if field.farm_id != farm.id:
            raise ValueError("field does not belong to the specified farm")
        return farm.external_id, _to_response(field)
    finally:
        if owns_session:
            db.close()