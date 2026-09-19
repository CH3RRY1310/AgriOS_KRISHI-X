"""Lightweight executable checks for the Farm Digital Twin foundation."""

from pathlib import Path
import sys

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas.farm import Farm, FarmState, SoilState
from app.services.farm_state import get_demo_farm_state, replace_demo_farm_state


def main() -> None:
    """Run model and service assertions without requiring pytest."""
    original = get_demo_farm_state()
    assert original.crop.crop == "tomato"
    assert original.weather.rain_probability_percent == 82

    try:
        SoilState(soil_moisture_percent=101)
    except ValidationError:
        pass
    else:
        raise AssertionError("percentage validation should reject values above 100")

    try:
        Farm(id="invalid", name="Invalid", location="Nowhere", area_acres=0)
    except ValidationError:
        pass
    else:
        raise AssertionError("area validation should reject zero")

    serialized = original.model_dump_json()
    restored = FarmState.model_validate_json(serialized)
    assert restored == original

    updated = original.model_copy(update={"updated_at": original.updated_at})
    replaced = replace_demo_farm_state(updated)
    assert replaced == updated
    assert get_demo_farm_state() == updated
    print("farm state checks passed")


if __name__ == "__main__":
    main()
