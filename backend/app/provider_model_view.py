from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text

from app.dashboard_auth import _engine, require_owner_session

router = APIRouter(tags=["saved-model-catalog"])


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


@router.get(
    "/dashboard/api/providers/{provider_id}/catalog-models",
    summary="List discovered models with model-test and saved-catalog state",
    dependencies=[Depends(require_owner_session)],
)
def list_catalog_models(provider_id: str, response: Response) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT d.provider_model_id::text AS provider_model_id,
                           d.provider_id::text AS provider_id,
                           d.model_id, d.display_name, d.availability,
                           d.supports_text, d.supports_vision, d.supports_tools,
                           d.supports_structured_output, d.context_window, d.max_output_tokens,
                           d.provider_metadata, d.last_test_status, d.last_tested_at,
                           d.last_test_error_code, d.fetched_at, d.updated_at,
                           s.saved_model_id::text AS saved_model_id,
                           s.state AS saved_model_state,
                           s.last_test_status AS saved_test_status,
                           s.last_tested_at AS saved_last_tested_at
                    FROM ai_provider_models d
                    LEFT JOIN ai_saved_provider_models s
                      ON s.provider_id=d.provider_id AND s.model_id=d.model_id
                    WHERE d.provider_id=CAST(:provider_id AS uuid)
                    ORDER BY lower(d.display_name), d.model_id
                    """
                ),
                {"provider_id": provider_id},
            ).mappings().all()
        return {"items": [dict(row) for row in rows], "count": len(rows)}
    finally:
        engine.dispose()
