"""SQLite-backed Farm Digital Twin state service."""

from app.schemas.farm import FarmState
from app.services.persistence import ensure_demo_farm_exists, load_demo_farm_state, persist_demo_farm_state


def get_demo_farm_state() -> FarmState:
    """Return the current deterministic demo state stored in SQLite."""
    return load_demo_farm_state()


def replace_demo_farm_state(state: FarmState) -> FarmState:
    """Replace the demo state and return the persisted value."""
    ensure_demo_farm_exists()
    return persist_demo_farm_state(state)
