"""Farm field persistence API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db_session
from app.schemas.field import FieldCreate, FieldResponse, FieldUpdate
from app.services.fields import create_field, get_field, list_fields_for_farm, update_field

router = APIRouter(tags=["fields"])


@router.get("/farms/{farm_id}/fields", response_model=list[FieldResponse])
def list_farm_fields(farm_id: str, db: Session = Depends(get_db_session)) -> list[FieldResponse]:
    """Return all fields belonging to a farm."""
    try:
        return list_fields_for_farm(farm_id, db)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post("/farms/{farm_id}/fields", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
def create_farm_field(
    farm_id: str,
    payload: FieldCreate,
    db: Session = Depends(get_db_session),
) -> FieldResponse:
    """Create a new persistent field under an existing farm."""
    try:
        return create_field(farm_id, payload, db)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.get("/fields/{field_id}", response_model=FieldResponse)
def get_field_by_id(field_id: str, db: Session = Depends(get_db_session)) -> FieldResponse:
    """Return one field by its stable external ID."""
    field = get_field(field_id, db)
    if field is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="field not found")
    return field


@router.put("/fields/{field_id}", response_model=FieldResponse)
def update_field_by_id(
    field_id: str,
    payload: FieldUpdate,
    db: Session = Depends(get_db_session),
) -> FieldResponse:
    """Update allowed properties for one field."""
    field = update_field(field_id, payload, db)
    if field is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="field not found")
    return field