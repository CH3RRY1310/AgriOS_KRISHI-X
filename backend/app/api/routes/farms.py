"""Farm Digital Twin API routes."""

from fastapi import APIRouter

from app.schemas.farm import FarmState
from app.services.farm_state import get_demo_farm_state, replace_demo_farm_state

router = APIRouter(prefix="/farms", tags=["farms"])


@router.get(
    "/demo/state",
    response_model=FarmState,
    summary="Get the demo farm state",
    description="Return the deterministic in-memory Farm Digital Twin state for development.",
)
def get_demo_state() -> FarmState:
    """Return the current simulated farm state."""
    return get_demo_farm_state()


@router.put(
    "/demo/state",
    response_model=FarmState,
    summary="Replace the demo farm state",
    description="Replace the in-memory Farm Digital Twin state for development and simulation.",
)
def update_demo_state(state: FarmState) -> FarmState:
    """Replace and return the simulated farm state."""
    return replace_demo_farm_state(state)
