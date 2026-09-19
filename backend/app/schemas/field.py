from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FieldBase(BaseModel):
    """Shared validated field properties."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    area_acres: float = Field(gt=0)
    location: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    crop: str = Field(min_length=1, max_length=120)
    variety: str | None = Field(default=None, max_length=120)
    growth_stage: str = Field(min_length=1, max_length=120)


class FieldCreate(FieldBase):
    """Validated payload for creating a field."""

    id: str | None = Field(default=None, min_length=1, max_length=120)


class FieldUpdate(BaseModel):
    """Validated mutable field properties."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=255)
    area_acres: float | None = Field(default=None, gt=0)
    location: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    crop: str | None = Field(default=None, min_length=1, max_length=120)
    variety: str | None = Field(default=None, max_length=120)
    growth_stage: str | None = Field(default=None, min_length=1, max_length=120)


class FieldResponse(FieldBase):
    """API representation of a persisted field."""

    id: str = Field(min_length=1, max_length=120)
    farm_id: str = Field(min_length=1, max_length=120)
    created_at: datetime
    updated_at: datetime