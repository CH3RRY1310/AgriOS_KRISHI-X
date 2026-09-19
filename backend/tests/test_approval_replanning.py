"""Executable validation for the approval and replanning workflow."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas.farm import ApprovalRequest, PlanReplanningRequest
from app.services.approval import clear_approval, submit_approval
from app.services.audit import clear_audit_events, get_audit_events
from app.services.farm_state import get_demo_farm_state
from app.services.planning import generate_plan
from app.services.replanning import replan_after_approval


def main() -> None:
    """Run deterministic approval and replanning assertions without pytest."""
    clear_approval()
    clear_audit_events()

    farm_state = get_demo_farm_state()
    plan = generate_plan("Maximize tomato yield while reducing water consumption by 20%.", farm_state)
    assert plan.plan_id
    assert plan.status == "awaiting_approval"

    approval = submit_approval(
        ApprovalRequest(
            decision="approve",
            plan_id=plan.plan_id,
            farmer_note="Proceed with the recommended plan.",
        ),
        plan,
    )
    assert approval.status == "approved"
    assert approval.decision == "approve"

    replan = replan_after_approval(farm_state, plan, approval)
    assert replan.status == "monitoring"
    assert replan.plan_id == plan.plan_id
    assert "monitor" in " ".join(replan.actions).lower()

    rejected = submit_approval(
        ApprovalRequest(
            decision="reject",
            plan_id=plan.plan_id,
            farmer_note="Do not irrigate today.",
        ),
        plan,
    )
    assert rejected.status == "rejected"

    modified = submit_approval(
        ApprovalRequest(
            decision="modify",
            plan_id=plan.plan_id,
            farmer_note="Delay irrigation by 12 hours instead.",
            modified_action="delay irrigation for 12 hours",
        ),
        plan,
    )
    assert modified.status == "modified"

    try:
        submit_approval(
            ApprovalRequest(
                decision="modify",
                plan_id=plan.plan_id,
                farmer_note="Missing action",
            ),
            plan,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("modify without modified_action should fail")

    try:
        submit_approval(
            ApprovalRequest(
                decision="approve",
                plan_id="not-a-real-plan",
            ),
            plan,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("invalid plan_id should fail")

    assert any(event.event_type == "PLAN_CREATED" for event in get_audit_events())
    assert any(event.event_type == "APPROVAL_SUBMITTED" for event in get_audit_events())
    assert any(event.event_type == "PLAN_REPLANNED" for event in get_audit_events())

    payload = json.loads(json.dumps(replan.model_dump()))
    assert payload["status"] == "monitoring"
    assert payload["plan_id"] == plan.plan_id

    assert all(
        event.metadata.get("executed") is not True for event in get_audit_events()
    )

    print("approval and replanning checks passed")


if __name__ == "__main__":
    main()
