from __future__ import annotations

import json
import time
from typing import Any

import requests
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.dashboard_auth import _engine, require_owner_session
from app.provider_secrets import read_provider_secret

router = APIRouter(tags=["saved-model-catalog"])
MAX_TEST_RESPONSE_BYTES = 256 * 1024


class AgentModelAssignmentInput(BaseModel):
    saved_model_id: str


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _safe_error_code(exc: Exception) -> str:
    code = str(exc)
    prefixes = ("HTTP_", "NETWORK_ERROR", "INVALID_", "RESPONSE_TOO_LARGE", "REDIRECT_BLOCKED", "MODEL_")
    return code[:80] if any(code.startswith(prefix) for prefix in prefixes) else "MODEL_TEST_ERROR"


def _provider_and_model(provider_id: str, provider_model_id: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    engine = _engine()
    try:
        with engine.connect() as connection:
            provider = connection.execute(
                text(
                    """
                    SELECT provider_id::text AS provider_id, provider_kind, base_url, credential_ref,
                           compatibility_mode, state
                    FROM ai_providers WHERE provider_id=CAST(:provider_id AS uuid)
                    """
                ),
                {"provider_id": provider_id},
            ).mappings().first()
            if provider is None:
                raise HTTPException(status_code=404, detail="Provider not found")
            model = connection.execute(
                text(
                    """
                    SELECT provider_model_id::text AS provider_model_id, provider_id::text AS provider_id,
                           model_id, display_name, availability, supports_text, supports_vision,
                           supports_tools, supports_structured_output, context_window, max_output_tokens,
                           provider_metadata, last_test_status, last_tested_at, last_test_error_code
                    FROM ai_provider_models
                    WHERE provider_model_id=CAST(:provider_model_id AS uuid)
                      AND provider_id=CAST(:provider_id AS uuid)
                    """
                ),
                {"provider_model_id": provider_model_id, "provider_id": provider_id},
            ).mappings().first()
            if model is None:
                raise HTTPException(status_code=404, detail="Discovered model not found")
    finally:
        engine.dispose()
    secret = read_provider_secret(provider["credential_ref"])
    if secret is None:
        raise HTTPException(status_code=409, detail="Provider credential is not configured")
    return dict(provider), dict(model), secret


def _read_bounded_json(response: requests.Response) -> dict[str, Any]:
    if 300 <= response.status_code < 400:
        raise RuntimeError("REDIRECT_BLOCKED")
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP_{response.status_code}")
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=32768):
        if not chunk:
            continue
        total += len(chunk)
        if total > MAX_TEST_RESPONSE_BYTES:
            raise RuntimeError("RESPONSE_TOO_LARGE")
        chunks.append(chunk)
    try:
        payload = json.loads(b"".join(chunks).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("INVALID_JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("INVALID_RESPONSE")
    return payload


def _test_model(provider: dict[str, Any], model: dict[str, Any], secret: str) -> int:
    session = requests.Session()
    session.trust_env = False
    started = time.monotonic()
    try:
        if provider["provider_kind"] == "GEMINI":
            endpoint = provider["base_url"].rstrip("/") + "/models/" + model["model_id"] + ":generateContent"
            headers = {"Accept": "application/json", "Content-Type": "application/json", "x-goog-api-key": secret, "User-Agent": "MedicineStoreAssistant/ModelTest"}
            payload = {
                "contents": [{"parts": [{"text": "Reply only with OK."}]}],
                "generationConfig": {"maxOutputTokens": 4, "temperature": 0},
            }
        else:
            endpoint = provider["base_url"].rstrip("/") + "/chat/completions"
            headers = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Bearer " + secret, "User-Agent": "MedicineStoreAssistant/ModelTest"}
            payload = {
                "model": model["model_id"],
                "messages": [{"role": "user", "content": "Reply only with OK."}],
                "stream": False,
                "temperature": 0,
                "max_tokens": 4,
            }
        try:
            response = session.post(endpoint, headers=headers, json=payload, timeout=(5, 30), allow_redirects=False, stream=True)
            _read_bounded_json(response)
        except requests.RequestException as exc:
            raise RuntimeError("NETWORK_ERROR") from exc
    finally:
        session.close()
    return max(0, int((time.monotonic() - started) * 1000))


def _record_discovered_test(provider_model_id: str, result: str, error_code: str | None) -> None:
    engine = _engine()
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE ai_provider_models
                    SET last_test_status=:status, last_tested_at=now(), last_test_error_code=:error_code,
                        updated_at=now()
                    WHERE provider_model_id=CAST(:provider_model_id AS uuid)
                    """
                ),
                {"provider_model_id": provider_model_id, "status": result, "error_code": error_code},
            )
    finally:
        engine.dispose()


@router.post("/dashboard/api/providers/{provider_id}/models/{provider_model_id}/test", summary="Test one discovered provider model")
def test_discovered_model(provider_id: str, provider_model_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    del owner
    _no_store(response)
    provider, model, secret = _provider_and_model(provider_id, provider_model_id)
    try:
        latency_ms = _test_model(provider, model, secret)
    except RuntimeError as exc:
        error_code = _safe_error_code(exc)
        _record_discovered_test(provider_model_id, "ERROR", error_code)
        raise HTTPException(status_code=502, detail=f"Model test failed ({error_code})") from exc
    _record_discovered_test(provider_model_id, "HEALTHY", None)
    return {"provider_model_id": provider_model_id, "model_id": model["model_id"], "test_status": "HEALTHY", "latency_ms": latency_ms}


@router.post("/dashboard/api/providers/{provider_id}/models/{provider_model_id}/save", status_code=status.HTTP_201_CREATED, summary="Save one tested model to the provider catalog")
def save_discovered_model(provider_id: str, provider_model_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        try:
            with engine.begin() as connection:
                model = connection.execute(
                    text(
                        """
                        SELECT provider_model_id::text AS provider_model_id, provider_id::text AS provider_id,
                               model_id, display_name, availability, supports_text, supports_vision,
                               supports_tools, supports_structured_output, context_window, max_output_tokens,
                               provider_metadata, last_test_status, last_tested_at, last_test_error_code
                        FROM ai_provider_models
                        WHERE provider_model_id=CAST(:provider_model_id AS uuid)
                          AND provider_id=CAST(:provider_id AS uuid)
                        FOR UPDATE
                        """
                    ),
                    {"provider_model_id": provider_model_id, "provider_id": provider_id},
                ).mappings().first()
                if model is None:
                    raise HTTPException(status_code=404, detail="Discovered model not found")
                if model["last_test_status"] != "HEALTHY" or model["last_tested_at"] is None:
                    raise HTTPException(status_code=409, detail="Test this model successfully before saving it")
                snapshot = {
                    "provider_model_id": model["provider_model_id"],
                    "availability": model["availability"],
                    "supports_text": model["supports_text"],
                    "supports_vision": model["supports_vision"],
                    "supports_tools": model["supports_tools"],
                    "supports_structured_output": model["supports_structured_output"],
                    "context_window": model["context_window"],
                    "max_output_tokens": model["max_output_tokens"],
                    "provider_metadata": model["provider_metadata"],
                }
                row = connection.execute(
                    text(
                        """
                        INSERT INTO ai_saved_provider_models (
                            provider_id, model_id, display_name, state, last_test_status, last_tested_at,
                            last_test_error_code, snapshot_metadata, created_by_user_id
                        ) VALUES (
                            CAST(:provider_id AS uuid), :model_id, :display_name, 'ACTIVE', 'HEALTHY',
                            :last_tested_at, NULL, CAST(:snapshot_metadata AS jsonb), CAST(:owner_id AS uuid)
                        )
                        ON CONFLICT (provider_id, model_id) DO UPDATE SET
                            display_name=EXCLUDED.display_name,
                            state='ACTIVE',
                            last_test_status='HEALTHY',
                            last_tested_at=EXCLUDED.last_tested_at,
                            last_test_error_code=NULL,
                            snapshot_metadata=EXCLUDED.snapshot_metadata,
                            updated_at=now()
                        RETURNING saved_model_id::text AS saved_model_id, provider_id::text AS provider_id,
                                  model_id, display_name, state, last_test_status, last_tested_at,
                                  last_test_error_code, snapshot_metadata, created_at, updated_at
                        """
                    ),
                    {
                        "provider_id": provider_id,
                        "model_id": model["model_id"],
                        "display_name": model["display_name"],
                        "last_tested_at": model["last_tested_at"],
                        "snapshot_metadata": json.dumps(snapshot),
                        "owner_id": owner["user_id"],
                    },
                ).mappings().one()
            return dict(row)
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail="Unable to save provider model") from exc
    finally:
        engine.dispose()


@router.get("/dashboard/api/providers/{provider_id}/saved-models", summary="List saved models for one provider", dependencies=[Depends(require_owner_session)])
def list_saved_models(provider_id: str, response: Response) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT s.saved_model_id::text AS saved_model_id, s.provider_id::text AS provider_id,
                           s.model_id, s.display_name, s.state, s.last_test_status, s.last_tested_at,
                           s.last_test_error_code, s.snapshot_metadata, s.created_at, s.updated_at,
                           EXISTS (
                               SELECT 1 FROM ai_provider_models d
                               WHERE d.provider_id=s.provider_id AND d.model_id=s.model_id
                           ) AS currently_discovered
                    FROM ai_saved_provider_models s
                    WHERE s.provider_id=CAST(:provider_id AS uuid)
                    ORDER BY CASE s.state WHEN 'ACTIVE' THEN 0 WHEN 'STALE' THEN 1 ELSE 2 END,
                             lower(s.display_name), s.model_id
                    """
                ),
                {"provider_id": provider_id},
            ).mappings().all()
        return {"items": [dict(row) for row in rows], "count": len(rows)}
    finally:
        engine.dispose()


@router.delete("/dashboard/api/providers/{provider_id}/saved-models/{saved_model_id}", summary="Remove a saved provider model")
def remove_saved_model(provider_id: str, saved_model_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    del owner
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            assigned = connection.execute(
                text("SELECT 1 FROM ai_agent_model_assignments WHERE saved_model_id=CAST(:saved_model_id AS uuid) AND enabled=true LIMIT 1"),
                {"saved_model_id": saved_model_id},
            ).first()
            if assigned:
                raise HTTPException(status_code=409, detail="Unassign this model from agents before removing it")
            deleted = connection.execute(
                text("DELETE FROM ai_saved_provider_models WHERE saved_model_id=CAST(:saved_model_id AS uuid) AND provider_id=CAST(:provider_id AS uuid) RETURNING saved_model_id"),
                {"saved_model_id": saved_model_id, "provider_id": provider_id},
            ).first()
            if not deleted:
                raise HTTPException(status_code=404, detail="Saved model not found")
        return {"saved_model_id": saved_model_id, "removed": True}
    finally:
        engine.dispose()


@router.get("/dashboard/api/agents/{agent_id}/model-assignment", summary="Read primary model assignment", dependencies=[Depends(require_owner_session)])
def get_agent_model_assignment(agent_id: str, response: Response) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT a.assignment_id::text AS assignment_id, a.agent_id::text AS agent_id,
                           a.saved_model_id::text AS saved_model_id, s.provider_id::text AS provider_id,
                           p.display_name AS provider_name, s.model_id, s.display_name AS model_name,
                           s.state AS saved_model_state, s.last_test_status, a.enabled
                    FROM ai_agent_model_assignments a
                    JOIN ai_saved_provider_models s ON s.saved_model_id=a.saved_model_id
                    JOIN ai_providers p ON p.provider_id=s.provider_id
                    WHERE a.agent_id=CAST(:agent_id AS uuid)
                      AND a.assignment_kind='PRIMARY' AND a.position=0
                    """
                ),
                {"agent_id": agent_id},
            ).mappings().first()
        return {"assignment": dict(row) if row else None}
    finally:
        engine.dispose()


@router.put("/dashboard/api/agents/{agent_id}/model-assignment", summary="Assign primary saved model to an internal agent")
def set_agent_model_assignment(agent_id: str, payload: AgentModelAssignmentInput, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            agent = connection.execute(text("SELECT runtime_mode, state FROM ai_agents WHERE agent_id=CAST(:agent_id AS uuid) FOR UPDATE"), {"agent_id": agent_id}).mappings().first()
            if agent is None:
                raise HTTPException(status_code=404, detail="AI agent not found")
            if agent["runtime_mode"] != "INTERNAL_MODEL":
                raise HTTPException(status_code=409, detail="Only internal model agents can receive provider/model assignments")
            if agent["state"] == "REVOKED":
                raise HTTPException(status_code=409, detail="Revoked agents cannot receive model assignments")
            saved = connection.execute(
                text(
                    """
                    SELECT s.saved_model_id::text AS saved_model_id, s.state, s.last_test_status,
                           p.state AS provider_state
                    FROM ai_saved_provider_models s
                    JOIN ai_providers p ON p.provider_id=s.provider_id
                    WHERE s.saved_model_id=CAST(:saved_model_id AS uuid)
                    """
                ),
                {"saved_model_id": payload.saved_model_id},
            ).mappings().first()
            if saved is None:
                raise HTTPException(status_code=404, detail="Saved model not found")
            if saved["provider_state"] != "ENABLED" or saved["state"] != "ACTIVE" or saved["last_test_status"] != "HEALTHY":
                raise HTTPException(status_code=409, detail="Only active, healthy saved models from enabled providers can be assigned")
            connection.execute(text("DELETE FROM ai_agent_model_assignments WHERE agent_id=CAST(:agent_id AS uuid) AND assignment_kind='PRIMARY'"), {"agent_id": agent_id})
            row = connection.execute(
                text(
                    """
                    INSERT INTO ai_agent_model_assignments (agent_id, saved_model_id, assignment_kind, position, enabled, created_by_user_id)
                    VALUES (CAST(:agent_id AS uuid), CAST(:saved_model_id AS uuid), 'PRIMARY', 0, true, CAST(:owner_id AS uuid))
                    RETURNING assignment_id::text AS assignment_id, agent_id::text AS agent_id,
                              saved_model_id::text AS saved_model_id, assignment_kind, position, enabled
                    """
                ),
                {"agent_id": agent_id, "saved_model_id": payload.saved_model_id, "owner_id": owner["user_id"]},
            ).mappings().one()
        return dict(row)
    finally:
        engine.dispose()


@router.delete("/dashboard/api/agents/{agent_id}/model-assignment", summary="Remove primary model assignment")
def clear_agent_model_assignment(agent_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    del owner
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM ai_agent_model_assignments WHERE agent_id=CAST(:agent_id AS uuid) AND assignment_kind='PRIMARY'"), {"agent_id": agent_id})
        return {"agent_id": agent_id, "assignment": None}
    finally:
        engine.dispose()
