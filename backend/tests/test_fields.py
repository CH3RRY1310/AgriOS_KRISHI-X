from __future__ import annotations

from pathlib import Path
import sys
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.base import Base
from app.database.models import FarmDB, FieldDB
from app.api.routes.fields import (
    create_farm_field,
    get_field_by_id,
    list_farm_fields,
    update_field_by_id,
)
from app.schemas.field import FieldCreate, FieldUpdate
from app.services.fields import (
    DEMO_FIELD_EXTERNAL_ID,
    create_field,
    ensure_demo_field_exists,
    get_field,
    list_fields_for_farm,
    update_field,
)
from app.services.persistence import DEMO_FARM_EXTERNAL_ID, ensure_demo_farm_exists


@pytest.fixture
def field_database():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine, future=True) as session:
        farm = ensure_demo_farm_exists(session)
        ensure_demo_field_exists(session)
        yield engine, session, farm


def test_demo_field_is_seeded_and_belongs_to_demo_farm(field_database):
    _, session, farm = field_database

    field = session.scalar(select(FieldDB).where(FieldDB.external_id == DEMO_FIELD_EXTERNAL_ID))

    assert session.scalar(select(FarmDB).where(FarmDB.external_id == DEMO_FARM_EXTERNAL_ID)) is not None
    assert field is not None
    assert field.farm_id == farm.id
    assert field.farm.external_id == DEMO_FARM_EXTERNAL_ID


def test_field_crud_and_restart_persistence(field_database):
    engine, session, _ = field_database
    field_id = f"field-test-{uuid4().hex[:8]}"
    payload = FieldCreate(
        id=field_id,
        name="North Test Field",
        area_acres=2.5,
        location="Nashik, Maharashtra",
        crop="tomato",
        variety="Sahyadri",
        growth_stage="vegetative",
    )

    created = create_field(DEMO_FARM_EXTERNAL_ID, payload, session)
    assert created.id == field_id
    assert created.farm_id == DEMO_FARM_EXTERNAL_ID
    assert any(field.id == field_id for field in list_fields_for_farm(DEMO_FARM_EXTERNAL_ID, session))
    assert get_field(field_id, session).name == "North Test Field"

    updated = update_field(field_id, FieldUpdate(name="North Test Field Updated", area_acres=3.0), session)
    assert updated is not None
    assert updated.name == "North Test Field Updated"
    assert updated.area_acres == 3.0

    session.close()
    with Session(bind=engine, future=True) as restarted_session:
        persisted = get_field(field_id, restarted_session)
        assert persisted is not None
        assert persisted.name == "North Test Field Updated"


def test_field_errors_are_safe(field_database):
    _, session, _ = field_database
    payload = FieldCreate(
        id="field-duplicate-test",
        name="Duplicate Test Field",
        area_acres=1.0,
        crop="tomato",
        growth_stage="flowering",
    )

    create_field(DEMO_FARM_EXTERNAL_ID, payload, session)
    with pytest.raises(ValueError, match="already exists"):
        create_field(DEMO_FARM_EXTERNAL_ID, payload, session)
    with pytest.raises(LookupError, match="farm not found"):
        create_field("farm-missing", payload, session)
    assert get_field("field-missing", session) is None
    with pytest.raises(LookupError, match="farm not found"):
        list_fields_for_farm("farm-missing", session)


def test_field_api_and_existing_farm_state_compatibility(field_database):
    _, session, _ = field_database
    fields_response = list_farm_fields(DEMO_FARM_EXTERNAL_ID, session)
    assert fields_response[0].id == DEMO_FIELD_EXTERNAL_ID

    field_id = f"field-api-{uuid4().hex[:8]}"
    created = create_farm_field(
        DEMO_FARM_EXTERNAL_ID,
        FieldCreate(
            id=field_id,
            name="API Test Field",
            area_acres=1.25,
            crop="tomato",
            growth_stage="flowering",
        ),
        session,
    )
    assert created.id == field_id
    assert get_field_by_id(field_id, session).id == field_id
    updated = update_field_by_id(field_id, FieldUpdate(growth_stage="fruiting"), session)
    assert updated.growth_stage == "fruiting"

    with pytest.raises(HTTPException) as missing_field:
        get_field_by_id("field-missing", session)
    assert missing_field.value.status_code == 404
    with pytest.raises(HTTPException) as missing_farm:
        list_farm_fields("farm-missing", session)
    assert missing_farm.value.status_code == 404