from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from app.dashboard_auth import require_dashboard_session
from app.db import normalize_database_url
from app.inventory_view_engine import FIELD_REGISTRY, PROVIDER_SORT_FIELDS, SYSTEM_PRESETS

router = APIRouter(prefix="/dashboard/api/inventory-view", tags=["inventory-view"])

FillToken = Literal["yellow", "green", "red", "blue", "orange", "gray"]
Density = Literal["comfortable", "compact"]
SortDirection = Literal["asc", "desc"]
MAX_FIELDS = 64
MAX_FILLS = 2_000
MIN_COLUMN_WIDTH = 64
MAX_COLUMN_WIDTH = 800


def _database_url() -> str:
    value = os.getenv("DATABASE_URL", "").strip()
    if not value:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database is not configured")
    return normalize_database_url(value)


def _engine():
    return create_engine(_database_url(), pool_pre_ping=True)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


class SavedViewFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    q: str = Field(default="", max_length=255)
    mapping_status: str = Field(default="", max_length=64)
    source_classification: str = Field(default="", max_length=64)
    review_reason: str = Field(default="", max_length=255)


class SavedViewSort(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(default="", max_length=80)
    direction: SortDirection | None = None

    @model_validator(mode="after")
    def sort_shape(self):
        if bool(self.field) != bool(self.direction):
            raise ValueError("sort field and direction must be supplied together")
        return self


class SavedViewFill(BaseModel):
    model_config = ConfigDict(extra="forbid")

    row_key: str = Field(min_length=1, max_length=180)
    field: str = Field(min_length=1, max_length=80)
    fill: FillToken


class SavedViewDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fields: list[str] = Field(min_length=1, max_length=MAX_FIELDS)
    column_labels: dict[str, str] = Field(default_factory=dict)
    column_widths: dict[str, int] = Field(default_factory=dict)
    density: Density = "comfortable"
    filters: SavedViewFilters = Field(default_factory=SavedViewFilters)
    sort: SavedViewSort = Field(default_factory=SavedViewSort)
    fills: list[SavedViewFill] = Field(default_factory=list, max_length=MAX_FILLS)

    @model_validator(mode="after")
    def unique_fields(self):
        if len(set(self.fields)) != len(self.fields):
            raise ValueError("saved view fields must be unique")
        return self


class SavedViewUpsert(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    base_preset: str = Field(min_length=1, max_length=80)
    definition: SavedViewDefinition



def _validated_payload(payload: SavedViewUpsert) -> SavedViewUpsert:
    payload.name = payload.name.strip()
    if not payload.name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Saved view name is required")
    view = SYSTEM_PRESETS.get(payload.base_preset)
    if view is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown saved-view base preset")

    for field in payload.definition.fields:
        if field not in FIELD_REGISTRY:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unknown saved-view field: {field}")

    selected_fields = set(payload.definition.fields)
    normalized_labels: dict[str, str] = {}
    for field, label in payload.definition.column_labels.items():
        if field not in selected_fields or field not in FIELD_REGISTRY:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Header label targets an invalid field: {field}")
        normalized = label.strip()
        if not normalized:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Header label cannot be blank: {field}")
        if len(normalized) > 120:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Header label is too long: {field}")
        normalized_labels[field] = normalized
    payload.definition.column_labels = normalized_labels

    for field, width in payload.definition.column_widths.items():
        if field not in selected_fields:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Width targets an unselected field: {field}")
        if width < MIN_COLUMN_WIDTH or width > MAX_COLUMN_WIDTH:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Column width is outside {MIN_COLUMN_WIDTH}-{MAX_COLUMN_WIDTH}: {field}")

    if payload.definition.sort.field:
        allowed = PROVIDER_SORT_FIELDS.get(view.provider, {})
        if payload.definition.sort.field not in allowed:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Saved-view sort field is not valid for the base preset")

    if payload.definition.filters.source_classification and payload.base_preset != "migration-review":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Source classification filter is available only for Migration Review")

    seen_fills: set[tuple[str, str]] = set()
    for fill in payload.definition.fills:
        if fill.field not in selected_fields or fill.field not in FIELD_REGISTRY:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Fill targets an invalid field: {fill.field}")
        identity = (fill.row_key, fill.field)
        if identity in seen_fills:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Duplicate saved fill identity")
        seen_fills.add(identity)

    return payload


def _serialize_row(row) -> dict[str, object]:
    mapping = row._mapping if hasattr(row, "_mapping") else row
    definition = mapping["definition"]
    if isinstance(definition, str):
        definition = json.loads(definition)
    created_at = mapping["created_at"]
    updated_at = mapping["updated_at"]
    return {
        "view_id": str(mapping["view_id"]),
        "name": str(mapping["name"]),
        "base_preset": str(mapping["base_preset"]),
        "definition": definition,
        "created_at": created_at.isoformat() if isinstance(created_at, datetime) else str(created_at),
        "updated_at": updated_at.isoformat() if isinstance(updated_at, datetime) else str(updated_at),
        "system_preset": False,
    }


@router.get("/saved-views")
def list_saved_views(
    response: Response,
    principal: dict[str, str] = Depends(require_dashboard_session),
) -> dict[str, object]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT view_id, name, base_preset, definition, created_at, updated_at
                    FROM inventory_saved_views
                    WHERE owner_user_id = CAST(:user_id AS uuid)
                    ORDER BY lower(name), view_id
                    """
                ),
                {"user_id": principal["user_id"]},
            ).all()
        return {
            "items": [_serialize_row(row) for row in rows],
            "database_canonical": False,
            "migration_baseline_accepted": False,
        }
    finally:
        engine.dispose()


@router.post("/saved-views", status_code=status.HTTP_201_CREATED)
def create_saved_view(
    payload: SavedViewUpsert,
    response: Response,
    principal: dict[str, str] = Depends(require_dashboard_session),
) -> dict[str, object]:
    _no_store(response)
    payload = _validated_payload(payload)
    engine = _engine()
    try:
        try:
            with engine.begin() as connection:
                row = connection.execute(
                    text(
                        """
                        INSERT INTO inventory_saved_views (owner_user_id, name, base_preset, definition)
                        VALUES (CAST(:user_id AS uuid), :name, :base_preset, CAST(:definition AS jsonb))
                        RETURNING view_id, name, base_preset, definition, created_at, updated_at
                        """
                    ),
                    {
                        "user_id": principal["user_id"],
                        "name": payload.name,
                        "base_preset": payload.base_preset,
                        "definition": json.dumps(payload.definition.model_dump(mode="json"), separators=(",", ":")),
                    },
                ).one()
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A saved view with this name already exists") from exc
        return _serialize_row(row)
    finally:
        engine.dispose()


@router.put("/saved-views/{view_id}")
def update_saved_view(
    view_id: UUID,
    payload: SavedViewUpsert,
    response: Response,
    principal: dict[str, str] = Depends(require_dashboard_session),
) -> dict[str, object]:
    _no_store(response)
    payload = _validated_payload(payload)
    engine = _engine()
    try:
        try:
            with engine.begin() as connection:
                row = connection.execute(
                    text(
                        """
                        UPDATE inventory_saved_views
                        SET name = :name,
                            base_preset = :base_preset,
                            definition = CAST(:definition AS jsonb),
                            updated_at = now()
                        WHERE view_id = CAST(:view_id AS uuid)
                          AND owner_user_id = CAST(:user_id AS uuid)
                        RETURNING view_id, name, base_preset, definition, created_at, updated_at
                        """
                    ),
                    {
                        "view_id": str(view_id),
                        "user_id": principal["user_id"],
                        "name": payload.name,
                        "base_preset": payload.base_preset,
                        "definition": json.dumps(payload.definition.model_dump(mode="json"), separators=(",", ":")),
                    },
                ).first()
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A saved view with this name already exists") from exc
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved view not found")
        return _serialize_row(row)
    finally:
        engine.dispose()


@router.delete("/saved-views/{view_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_view(
    view_id: UUID,
    principal: dict[str, str] = Depends(require_dashboard_session),
) -> Response:
    engine = _engine()
    try:
        with engine.begin() as connection:
            deleted = connection.execute(
                text(
                    """
                    DELETE FROM inventory_saved_views
                    WHERE view_id = CAST(:view_id AS uuid)
                      AND owner_user_id = CAST(:user_id AS uuid)
                    RETURNING view_id
                    """
                ),
                {"view_id": str(view_id), "user_id": principal["user_id"]},
            ).first()
        if deleted is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved view not found")
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        _no_store(response)
        return response
    finally:
        engine.dispose()
