from __future__ import annotations

from pathlib import Path
import sys

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.routes.approvals import submit_demo_approval
from app.api.routes.planning import planning_demo
from app.api.routes.replanning import replan_demo
from app.database.base import Base
from app.database.models import FarmDB, FieldDB
from app.schemas.farm import ApprovalRequest, PlanningRequest, PlanReplanningRequest
from app.services.approval import clear_approval
from app.services.audit import clear_audit_events
from app.services.fields import resolve_planning_scope
from app.services.farm_state import get_demo_farm_state


DEMO_GOAL = "Maximize tomato yield while reducing water consumption by 20%"


def test_legacy_planning_request_remains_compatible():
    response = planning_demo(PlanningRequest(goal=DEMO_GOAL))

    assert response.plan.status == "awaiting_approval"
    assert response.weather.recommendation == "WAIT"
    assert response.irrigation.recommendation == "IRRIGATE"
    assert response.plan.farm_id is None
    assert response.plan.field_id is None


def test_field_aware_planning_propagates_context_and_persists_links():
    response = planning_demo(
        PlanningRequest(
            goal=DEMO_GOAL,
            farm_id="farm-demo-001",
            field_id="field-demo-001",
        )
    )

    assert response.context is not None
    assert response.context.farm_id == "farm-demo-001"
    assert response.context.field_id == "field-demo-001"
    assert response.context.field_name == "Field A"
    assert response.goal_analysis.field_id == "field-demo-001"
    assert response.weather.field_id == "field-demo-001"
    assert response.irrigation.field_id == "field-demo-001"
    assert response.conflicts[0].field_id == "field-demo-001"
    assert response.verification.verified is True
    assert response.verification.field_id == "field-demo-001"
    assert response.plan.farm_id == "farm-demo-001"
    assert response.plan.field_id == "field-demo-001"
    assert response.plan.status == "awaiting_approval"

    stored = get_demo_farm_state()
    assert stored.goal is not None
    assert stored.goal.field_id == "field-demo-001"
    assert stored.plan is not None
    assert stored.plan.field_id == "field-demo-001"


def test_field_aware_plan_approval_and_replanning_retain_scope():
    clear_approval()
    clear_audit_events()
    response = planning_demo(
        PlanningRequest(
            goal=DEMO_GOAL,
            farm_id="farm-demo-001",
            field_id="field-demo-001",
        )
    )

    approval = submit_demo_approval(
        ApprovalRequest(
            decision="approve",
            plan_id=response.plan.plan_id,
            farmer_note="Approve field-aware simulation plan",
        )
    )
    assert approval.approval.status == "approved"
    assert approval.execution.status == "simulation_only"
    assert approval.execution.executed is False

    replanned = replan_demo(PlanReplanningRequest(plan_id=response.plan.plan_id))
    assert replanned.plan_id == response.plan.plan_id
    assert replanned.farm_id == "farm-demo-001"
    assert replanned.field_id == "field-demo-001"


def test_invalid_field_scope_is_rejected():
    with pytest.raises(HTTPException) as missing_field:
        planning_demo(
            PlanningRequest(
                goal=DEMO_GOAL,
                farm_id="farm-demo-001",
                field_id="field-does-not-exist",
            )
        )
    assert missing_field.value.status_code == 404


def test_field_belonging_to_another_farm_is_rejected():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine, future=True) as session:
        farm = FarmDB(
            external_id="farm-other-001",
            name="Other Farm",
            location="Nashik, Maharashtra",
            area=4.0,
            crop="tomato",
        )
        session.add(farm)
        session.commit()
        other_farm = FarmDB(
            external_id="farm-requested-001",
            name="Requested Farm",
            location="Nashik, Maharashtra",
            area=4.0,
            crop="tomato",
        )
        session.add(other_farm)
        session.flush()
        session.add(
            FieldDB(
                external_id="field-owned-by-other-001",
                farm_id=farm.id,
                name="Other Field",
                area_acres=1.0,
                crop="tomato",
                growth_stage="flowering",
            )
        )
        session.commit()

        with pytest.raises(ValueError, match="does not belong"):
            resolve_planning_scope("farm-requested-001", "field-owned-by-other-001", session)