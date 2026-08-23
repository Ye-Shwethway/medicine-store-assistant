from __future__ import annotations

import json
from typing import Any

import requests
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import text

from app.dashboard_auth import _engine, require_owner_session
from app.provider_secrets import read_provider_secret

router = APIRouter(prefix="/dashboard/api/providers", tags=["provider-registry"])

NANOGPT_API_ROOT = "https://nano-gpt.com/api"
MAX_PROVIDER_RESPONSE_BYTES = 4 * 1024 * 1024
MAX_MODELS = 2000


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _fetch_provider(provider_id: str) -> dict[str, Any]:
    engine = _engine()
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT provider_id::text AS provider_id, display_name, provider_kind,
                           credential_ref, state
                    FROM ai_providers
                    WHERE provider_id=CAST(:provider_id AS uuid)
                    """
                ),
                {"provider_id": provider_id},
            ).mappings().first()
        if row is None:
            raise HTTPException(status_code=404, detail="Provider not found")
        provider = dict(row)
        if provider["provider_kind"] != "NANOGPT":
            raise HTTPException(status_code=409, detail="Detailed NanoGPT catalog is available only for NanoGPT providers")
        return provider
    finally:
        engine.dispose()


def _secret(provider: dict[str, Any]) -> str:
    value = read_provider_secret(provider.get("credential_ref"))
    if value is None:
        raise HTTPException(status_code=409, detail="Provider credential is not configured")
    return value


def _request_json(path: str, secret: str) -> dict[str, Any]:
    session = requests.Session()
    session.trust_env = False
    try:
        response = session.get(
            NANOGPT_API_ROOT + path,
            headers={
                "Accept": "application/json",
                "Authorization": "Bearer " + secret,
                "User-Agent": "MedicineStoreAssistant/NanoGPTCatalog",
            },
            timeout=(5, 25),
            allow_redirects=False,
            stream=True,
        )
        if 300 <= response.status_code < 400:
            raise RuntimeError("REDIRECT_BLOCKED")
        if response.status_code >= 400:
            raise RuntimeError(f"HTTP_{response.status_code}")
        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_content(chunk_size=65536):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_PROVIDER_RESPONSE_BYTES:
                raise RuntimeError("RESPONSE_TOO_LARGE")
            chunks.append(chunk)
        try:
            payload = json.loads(b"".join(chunks).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("INVALID_JSON") from exc
        if not isinstance(payload, dict):
            raise RuntimeError("INVALID_RESPONSE")
        return payload
    except requests.RequestException as exc:
        raise RuntimeError("NETWORK_ERROR") from exc
    finally:
        session.close()


def _safe_error_code(exc: Exception) -> str:
    code = str(exc)
    prefixes = ("HTTP_", "NETWORK_ERROR", "INVALID_", "EMPTY_", "RESPONSE_TOO_LARGE", "REDIRECT_BLOCKED")
    return code[:80] if any(code.startswith(prefix) for prefix in prefixes) else "NANOGPT_CATALOG_ERROR"


def _catalog_ids(payload: dict[str, Any]) -> set[str]:
    data = payload.get("data")
    if not isinstance(data, list):
        return set()
    result: set[str] = set()
    for raw in data[:MAX_MODELS]:
        if isinstance(raw, dict):
            model_id = str(raw.get("id") or "").strip()
            if model_id and len(model_id) <= 240:
                result.add(model_id)
    return result


def _merge_catalog_payloads(*payloads: dict[str, Any]) -> dict[str, Any]:
    """Union detailed catalogs by model id, preferring fields from earlier payloads."""
    merged: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for payload in payloads:
        data = payload.get("data")
        if not isinstance(data, list):
            continue
        for raw in data[:MAX_MODELS]:
            if not isinstance(raw, dict):
                continue
            model_id = str(raw.get("id") or "").strip()
            if not model_id or len(model_id) > 240:
                continue
            if model_id not in merged:
                merged[model_id] = dict(raw)
                order.append(model_id)
                continue
            current = merged[model_id]
            for key, value in raw.items():
                if key not in current or current[key] in (None, "", {}, []):
                    current[key] = value
    return {"object": "list", "data": [merged[model_id] for model_id in order[:MAX_MODELS]]}


def _nullable_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def _nullable_bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _sanitize(value: Any, *, depth: int = 0) -> Any:
    if depth > 4:
        return None
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:1500]
    if isinstance(value, list):
        return [_sanitize(item, depth=depth + 1) for item in value[:60]]
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in list(value.items())[:60]:
            result[str(key)[:120]] = _sanitize(item, depth=depth + 1)
        return result
    return str(value)[:500]


def _normalize_model(raw: dict[str, Any], subscription_ids: set[str], paid_ids: set[str]) -> dict[str, Any] | None:
    model_id = str(raw.get("id") or "").strip()
    if not model_id or len(model_id) > 240:
        return None
    display_name = str(raw.get("name") or model_id).strip()[:240] or model_id
    capabilities = raw.get("capabilities") if isinstance(raw.get("capabilities"), dict) else {}
    pricing = raw.get("pricing") if isinstance(raw.get("pricing"), dict) else {}
    if model_id in subscription_ids:
        billing_tier = "SUBSCRIPTION_INCLUDED"
        subscription_included: bool | None = True
        paid_only: bool | None = False
    elif model_id in paid_ids:
        billing_tier = "PAID_ONLY"
        subscription_included = False
        paid_only = True
    else:
        billing_tier = "UNKNOWN"
        subscription_included = None
        paid_only = None
    return {
        "model_id": model_id,
        "display_name": display_name,
        "supports_text": True,
        "supports_vision": _nullable_bool(capabilities.get("vision")),
        "supports_tools": _nullable_bool(capabilities.get("tool_calling")),
        "supports_structured_output": _nullable_bool(capabilities.get("structured_output")),
        "context_window": _nullable_int(raw.get("context_length")),
        "max_output_tokens": _nullable_int(raw.get("max_output_tokens")),
        "provider_metadata": _sanitize(
            {
                "catalog_source": "nanogpt_detailed_v1_union",
                "owned_by": raw.get("owned_by"),
                "description": raw.get("description"),
                "category": raw.get("category"),
                "capabilities": capabilities,
                "pricing": pricing,
                "billing_tier": billing_tier,
                "subscription_included": subscription_included,
                "paid_only": paid_only,
                "cost_estimate": raw.get("cost_estimate"),
            }
        ),
    }


def _normalize_catalog(payload: dict[str, Any], subscription_ids: set[str], paid_ids: set[str]) -> list[dict[str, Any]]:
    data = payload.get("data")
    if not isinstance(data, list):
        raise RuntimeError("INVALID_MODEL_LIST")
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in data[:MAX_MODELS]:
        if not isinstance(raw, dict):
            continue
        item = _normalize_model(raw, subscription_ids, paid_ids)
        if item is None or item["model_id"] in seen:
            continue
        seen.add(item["model_id"])
        items.append(item)
    if not items:
        raise RuntimeError("EMPTY_MODEL_LIST")
    return items


@router.post("/{provider_id}/nanogpt/models/fetch-detailed", summary="Fetch NanoGPT detailed models, capabilities, pricing, and billing inclusion")
def fetch_nanogpt_detailed_models(
    provider_id: str,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    del owner
    _no_store(response)
    provider = _fetch_provider(provider_id)
    secret = _secret(provider)
    try:
        canonical = _request_json("/v1/models?detailed=true", secret)
        subscription_payload = _request_json("/subscription/v1/models?detailed=true", secret)
        paid_payload = _request_json("/paid/v1/models?detailed=true", secret)
        subscription_ids = _catalog_ids(subscription_payload)
        paid_ids = _catalog_ids(paid_payload)
        # The canonical list may be account-preference filtered. Union all official
        # detailed catalogs so Provider Registry can always show included and paid-only models.
        merged_payload = _merge_catalog_payloads(canonical, subscription_payload, paid_payload)
        models = _normalize_catalog(merged_payload, subscription_ids, paid_ids)
    except RuntimeError as exc:
        error_code = _safe_error_code(exc)
        engine = _engine()
        try:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        """
                        UPDATE ai_providers
                        SET last_model_fetch_status='ERROR', last_model_fetch_at=now(),
                            last_error_code=:error_code, updated_at=now()
                        WHERE provider_id=CAST(:provider_id AS uuid)
                        """
                    ),
                    {"provider_id": provider_id, "error_code": error_code},
                )
        finally:
            engine.dispose()
        raise HTTPException(status_code=502, detail=f"NanoGPT detailed model fetch failed ({error_code})") from exc

    engine = _engine()
    try:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM ai_provider_models WHERE provider_id=CAST(:provider_id AS uuid)"),
                {"provider_id": provider_id},
            )
            for model in models:
                connection.execute(
                    text(
                        """
                        INSERT INTO ai_provider_models (
                            provider_id, model_id, display_name, availability, supports_text, supports_vision,
                            supports_tools, supports_structured_output, context_window, max_output_tokens, provider_metadata
                        ) VALUES (
                            CAST(:provider_id AS uuid), :model_id, :display_name, 'AVAILABLE', :supports_text, :supports_vision,
                            :supports_tools, :supports_structured_output, :context_window, :max_output_tokens,
                            CAST(:provider_metadata AS jsonb)
                        )
                        """
                    ),
                    {
                        **model,
                        "provider_id": provider_id,
                        "provider_metadata": json.dumps(model["provider_metadata"]),
                    },
                )
            connection.execute(
                text(
                    """
                    UPDATE ai_providers
                    SET last_model_fetch_status='SUCCESS', last_model_fetch_at=now(),
                        last_connection_status='HEALTHY', last_connection_at=now(),
                        last_error_code=NULL, updated_at=now()
                    WHERE provider_id=CAST(:provider_id AS uuid)
                    """
                ),
                {"provider_id": provider_id},
            )
    finally:
        engine.dispose()

    subscription_count = sum(1 for item in models if item["provider_metadata"].get("billing_tier") == "SUBSCRIPTION_INCLUDED")
    paid_count = sum(1 for item in models if item["provider_metadata"].get("billing_tier") == "PAID_ONLY")
    return {
        "provider_id": provider_id,
        "model_count": len(models),
        "subscription_included_count": subscription_count,
        "paid_only_count": paid_count,
        "billing_unknown_count": len(models) - subscription_count - paid_count,
        "model_fetch_status": "SUCCESS",
    }
