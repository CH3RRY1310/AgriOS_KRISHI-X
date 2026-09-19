from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.database.base import Base
from app.database.connection import SessionLocal
from app.database.models import ApprovalDB, AuditEventDB, FarmDB, GoalDB, PlanDB
from app.services.farm_state import get_demo_farm_state, replace_demo_farm_state


@pytest.fixture
def temp_db_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine, future=True)
    try:
        yield session
    finally:
        session.close()


def test_demo_farm_seed_and_idempotency(temp_db_session: Session):
    farm = temp_db_session.query(FarmDB).filter(FarmDB.external_id == "farm-demo-001").first()
    assert farm is None

    state = get_demo_farm_state()
    assert state.farm.id == "farm-demo-001"
    assert state.crop.crop == "tomato"

    replace_demo_farm_state(state)
    saved = get_demo_farm_state()
    assert saved.farm.id == "farm-demo-001"


def test_goal_plan_approval_and_audit_persist(temp_db_session: Session):
    state = get_demo_farm_state()
    farm = temp_db_session.query(FarmDB).first()
    if farm is None:
        farm = FarmDB(
            name="Shinde Farm / Block A",
            location="Nashik, Maharashtra",
            area=11.86,
            crop="tomato",
            growth_stage="flowering",
            external_id="farm-demo-001",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        temp_db_session.add(farm)
        temp_db_session.commit()

    goal = GoalDB(farm_id=farm.id, text="Increase yield with lower water use", status="active")
    temp_db_session.add(goal)
    temp_db_session.commit()

    plan = PlanDB(
        farm_id=farm.id,
        goal_id=goal.id,
        status="awaiting_approval",
        decision="POSTPONE_IRRIGATION",
        confidence=92.0,
        rationale="Deterministic safety plan",
        expected_water_saved_liters=3200,
        expected_water_reduction_percent=20,
    )
    temp_db_session.add(plan)
    temp_db_session.commit()

    approval = ApprovalDB(
        plan_id=plan.id,
        decision="approve",
        status="approved",
        execution_mode="simulation_only",
        executed=False,
        farmer_note="Approved by farmer",
        rationale="No physical action",
    )
    temp_db_session.add(approval)
    temp_db_session.commit()

    audit = AuditEventDB(
        farm_id=farm.id,
        plan_id=plan.id,
        event_type="PLAN_CREATED",
        message="Plan created",
        metadata={"goal": "Increase yield with lower water use", "executed": False},
    )
    temp_db_session.add(audit)
    temp_db_session.commit()

    stored_approval = temp_db_session.query(ApprovalDB).filter_by(plan_id=plan.id).one()
    assert stored_approval.execution_mode == "simulation_only"
    assert stored_approval.executed is False

    stored_event = temp_db_session.query(AuditEventDB).filter_by(plan_id=plan.id).one()
    assert stored_event.event_type == "PLAN_CREATED"
    assert stored_event.metadata["executed"] is False


def test_persistence_restart_equivalence():
    first = get_demo_farm_state()
    second = replace_demo_farm_state(first)
    assert second.farm.id == first.farm.id
    assert second.goal == first.goal
