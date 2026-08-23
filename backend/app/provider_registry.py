from __future__ import annotations

import ipaddress
import json
import socket
from typing import Any, Literal
from urllib.parse import urljoin, urlparse

import requests
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.dashboard_auth import _engine, require_owner_session
from app.provider_secrets import delete_provider_secret, read_provider_secret, store_provider_secret

router = APIRouter(prefix="/dashboard/api/providers", tags=["provider-registry"])

PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "OPENAI": {"base_url": "https://api.openai.com/v1", "compatibility_mode": "OPENAI_MODELS"},
    "GEMINI": {"base_url": "https://generativelanguage.googleapis.com/v1beta", "compatibility_mode": "GEMINI_NATIVE_MODELS"},
    "OPENROUTER": {"base_url": "https://openrouter.ai/api/v1", "compatibility_mode": "OPENAI_MODELS"},
    "NANOGPT": {"base_url": "https://nano-gpt.com/api/v1", "compatibility_mode": "OPENAI_MODELS"},
}
MAX_PROVIDER_RESPONSE_BYTES = 4 * 1024 * 1024
MAX_MODELS = 2000


class ProviderCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    provider_kind: Literal["OPENAI", "GEMINI", "OPENROUTER", "NANOGPT", "OPENAI_COMPATIBLE"]
    base_url: str | None = Field(default=None, max_length=500)


class ProviderUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    base_url: str | None = Field(default=None, max_length=500)


class ProviderCredential(BaseModel):
    api_key: str = Field(min_length=8, max_length=8192)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _clean_name(value: str) -> str:
    value = " ".join(value.strip().split())
    if not value or len(value) > 100:
        raise HTTPException(status_code=400, detail="Enter a valid provider name")
    return value


def _host_is_public(hostname: str) -> bool:
    try:
        infos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False
    if not infos:
        return False
    for info in infos:
        address = info[4][0].split("%", 1)[0]
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            return False
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return False
    return True


def _validate_base_url(value: str) -> str:
    raw = value.strip().rstrip("/")
    parsed = urlparse(raw)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise HTTPException(status_code=400, detail="Provider base URL must be a public HTTPS URL")
    if parsed.fragment or parsed.query:
        raise HTTPException(status_code=400, detail="Provider base URL must not contain a query or fragment")
    if not _host_is_public(parsed.hostname):
        raise HTTPException(status_code=400, detail="Provider base URL resolves to a forbidden network destination")
    return raw


def _provider_dict(row: Any, *, model_count: int = 0) -> dict[str, Any]:
    item = dict(row)
    item["credential_configured"] = bool(item.pop("credential_ref", None))
    item["model_count"] = int(model_count)
    return item


def _fetch_provider(connection, provider_id: str, *, for_update: bool = False):
    suffix = " FOR UPDATE" if for_update else ""
    row = connection.execute(
        text(
            """
            SELECT provider_id::text AS provider_id, display_name, provider_kind, base_url,
                   credential_ref, compatibility_mode, state, last_connection_status,
                   last_connection_at, last_model_fetch_status, last_model_fetch_at,
                   last_error_code, created_by_user_id::text AS created_by_user_id,
                   created_at, updated_at
            FROM ai_providers
            WHERE provider_id = CAST(:provider_id AS uuid)
            """ + suffix
        ),
        {"provider_id": provider_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    return row


def _model_endpoint(provider: dict[str, Any]) -> str:
    return provider["base_url"].rstrip("/") + "/models"


def _headers(provider: dict[str, Any], secret: str) -> dict[str, str]:
    headers = {"Accept": "application/json", "User-Agent": "MedicineStoreAssistant/ProviderRegistry"}
    if provider["compatibility_mode"] == "GEMINI_NATIVE_MODELS":
        headers["x-goog-api-key"] = secret
    else:
        headers["Authorization"] = "Bearer " + secret
    return headers


def _get_json(provider: dict[str, Any], secret: str) -> dict[str, Any]:
    endpoint = _model_endpoint(provider)
    parsed = urlparse(endpoint)
    if not parsed.hostname or not _host_is_public(parsed.hostname):
        raise RuntimeError("FORBIDDEN_DESTINATION")
    session = requests.Session()
    session.trust_env = False
    try:
        response = session.get(
            endpoint,
            headers=_headers(provider, secret),
            timeout=(5, 20),
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


def _sanitize(value: Any, *, depth: int = 0) -> Any:
    if depth > 3:
        return None
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:1000]
    if isinstance(value, list):
        return [_sanitize(item, depth=depth + 1) for item in value[:50]]
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in list(value.items())[:50]:
            key_text = str(key)[:120]
            result[key_text] = _sanitize(item, depth=depth + 1)
        return result
    return str(value)[:500]


def _nullable_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def _normalize_openai_model(raw: dict[str, Any]) -> dict[str, Any] | None:
    model_id = str(raw.get("id") or "").strip()
    if not model_id or len(model_id) > 240:
        return None
    display = str(raw.get("name") or raw.get("display_name") or model_id).strip()[:240] or model_id
    architecture = raw.get("architecture") if isinstance(raw.get("architecture"), dict) else {}
    input_modalities = architecture.get("input_modalities") or raw.get("input_modalities")
    output_modalities = architecture.get("output_modalities") or raw.get("output_modalities")
    supported = raw.get("supported_parameters")
    if isinstance(supported, dict):
        supported_names = set(str(x) for x in supported.keys())
    elif isinstance(supported, list):
        supported_names = set(str(x) for x in supported)
    else:
        supported_names = set()
    if isinstance(input_modalities, list):
        lowered = {str(x).lower() for x in input_modalities}
        supports_text: bool | None = "text" in lowered
        supports_vision: bool | None = "image" in lowered
    else:
        supports_text = None
        supports_vision = None
    supports_tools = True if {"tools", "tool_choice"} & supported_names else None
    supports_structured = True if {"response_format", "structured_outputs", "json_schema"} & supported_names else None
    return {
        "model_id": model_id,
        "display_name": display,
        "supports_text": supports_text,
        "supports_vision": supports_vision,
        "supports_tools": supports_tools,
        "supports_structured_output": supports_structured,
        "context_window": _nullable_int(raw.get("context_length") or raw.get("context_window")),
        "max_output_tokens": _nullable_int(raw.get("max_output_tokens") or raw.get("top_provider", {}).get("max_completion_tokens") if isinstance(raw.get("top_provider"), dict) else None),
        "provider_metadata": _sanitize({
            "owned_by": raw.get("owned_by"),
            "description": raw.get("description"),
            "architecture": architecture,
            "supported_parameters": supported,
            "pricing": raw.get("pricing"),
        }),
    }


def _normalize_gemini_model(raw: dict[str, Any]) -> dict[str, Any] | None:
    resource_name = str(raw.get("name") or "").strip()
    model_id = resource_name.removeprefix("models/")
    if not model_id or len(model_id) > 240:
        return None
    methods = raw.get("supportedGenerationMethods") if isinstance(raw.get("supportedGenerationMethods"), list) else []
    return {
        "model_id": model_id,
        "display_name": str(raw.get("displayName") or model_id).strip()[:240] or model_id,
        "supports_text": True if "generateContent" in methods else None,
        "supports_vision": None,
        "supports_tools": None,
        "supports_structured_output": None,
        "context_window": _nullable_int(raw.get("inputTokenLimit")),
        "max_output_tokens": _nullable_int(raw.get("outputTokenLimit")),
        "provider_metadata": _sanitize({
            "description": raw.get("description"),
            "version": raw.get("version"),
            "supportedGenerationMethods": methods,
        }),
    }


def _normalize_models(provider: dict[str, Any], payload: dict[str, Any]) -> list[dict[str, Any]]:
    if provider["compatibility_mode"] == "GEMINI_NATIVE_MODELS":
        raw_items = payload.get("models")
        normalizer = _normalize_gemini_model
    else:
        raw_items = payload.get("data")
        normalizer = _normalize_openai_model
    if not isinstance(raw_items, list):
        raise RuntimeError("INVALID_MODEL_LIST")
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in raw_items[:MAX_MODELS]:
        if not isinstance(raw, dict):
            continue
        item = normalizer(raw)
        if item is None or item["model_id"] in seen:
            continue
        seen.add(item["model_id"])
        items.append(item)
    if not items:
        raise RuntimeError("EMPTY_MODEL_LIST")
    return items


def _safe_error_code(exc: Exception) -> str:
    code = str(exc)
    allowed_prefixes = ("HTTP_", "NETWORK_ERROR", "INVALID_", "EMPTY_", "RESPONSE_TOO_LARGE", "REDIRECT_BLOCKED", "FORBIDDEN_DESTINATION")
    if any(code.startswith(prefix) for prefix in allowed_prefixes):
        return code[:80]
    return "PROVIDER_ERROR"


@router.get("", summary="List AI providers", dependencies=[Depends(require_owner_session)])
def list_providers(response: Response) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(text("""
                SELECT p.provider_id::text AS provider_id, p.display_name, p.provider_kind, p.base_url,
                       p.credential_ref, p.compatibility_mode, p.state, p.last_connection_status,
                       p.last_connection_at, p.last_model_fetch_status, p.last_model_fetch_at,
                       p.last_error_code, p.created_by_user_id::text AS created_by_user_id,
                       p.created_at, p.updated_at, COUNT(m.provider_model_id) AS model_count
                FROM ai_providers p
                LEFT JOIN ai_provider_models m ON m.provider_id = p.provider_id
                GROUP BY p.provider_id
                ORDER BY CASE p.state WHEN 'ENABLED' THEN 0 ELSE 1 END, lower(p.display_name)
            """)).mappings().all()
        return {"items": [_provider_dict(row, model_count=row["model_count"]) for row in rows], "count": len(rows)}
    finally:
        engine.dispose()


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create AI provider")
def create_provider(payload: ProviderCreate, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    defaults = PROVIDER_DEFAULTS.get(payload.provider_kind)
    if defaults:
        base_url = _validate_base_url(payload.base_url or defaults["base_url"])
        compatibility = defaults["compatibility_mode"]
    else:
        if not payload.base_url:
            raise HTTPException(status_code=400, detail="Custom OpenAI-compatible providers require a base URL")
        base_url = _validate_base_url(payload.base_url)
        compatibility = "OPENAI_MODELS"
    engine = _engine()
    try:
        try:
            with engine.begin() as connection:
                row = connection.execute(text("""
                    INSERT INTO ai_providers (display_name, provider_kind, base_url, compatibility_mode, created_by_user_id)
                    VALUES (:display_name, :provider_kind, :base_url, :compatibility_mode, CAST(:owner_id AS uuid))
                    RETURNING provider_id::text AS provider_id, display_name, provider_kind, base_url,
                              credential_ref, compatibility_mode, state, last_connection_status,
                              last_connection_at, last_model_fetch_status, last_model_fetch_at,
                              last_error_code, created_by_user_id::text AS created_by_user_id,
                              created_at, updated_at
                """), {
                    "display_name": _clean_name(payload.display_name),
                    "provider_kind": payload.provider_kind,
                    "base_url": base_url,
                    "compatibility_mode": compatibility,
                    "owner_id": owner["user_id"],
                }).mappings().one()
            return _provider_dict(row)
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail="Provider name is already in use") from exc
    finally:
        engine.dispose()


@router.patch("/{provider_id}", summary="Update AI provider")
def update_provider(provider_id: str, payload: ProviderUpdate, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        try:
            with engine.begin() as connection:
                current = _fetch_provider(connection, provider_id, for_update=True)
                if current["state"] == "ENABLED" and payload.base_url is not None:
                    raise HTTPException(status_code=409, detail="Disable the provider before changing its base URL")
                assignments: list[str] = []
                params: dict[str, Any] = {"provider_id": provider_id}
                if payload.display_name is not None:
                    assignments.append("display_name=:display_name")
                    params["display_name"] = _clean_name(payload.display_name)
                if payload.base_url is not None:
                    assignments.extend([
                        "base_url=:base_url",
                        "last_connection_status='UNTESTED'",
                        "last_connection_at=NULL",
                        "last_model_fetch_status='NEVER'",
                        "last_model_fetch_at=NULL",
                        "last_error_code=NULL",
                    ])
                    params["base_url"] = _validate_base_url(payload.base_url)
                    connection.execute(text("DELETE FROM ai_provider_models WHERE provider_id=CAST(:provider_id AS uuid)"), params)
                if not assignments:
                    raise HTTPException(status_code=400, detail="No provider changes supplied")
                assignments.append("updated_at=now()")
                row = connection.execute(text(f"""
                    UPDATE ai_providers SET {', '.join(assignments)}
                    WHERE provider_id=CAST(:provider_id AS uuid)
                    RETURNING provider_id::text AS provider_id, display_name, provider_kind, base_url,
                              credential_ref, compatibility_mode, state, last_connection_status,
                              last_connection_at, last_model_fetch_status, last_model_fetch_at,
                              last_error_code, created_by_user_id::text AS created_by_user_id,
                              created_at, updated_at
                """), params).mappings().one()
            return _provider_dict(row)
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail="Provider name is already in use") from exc
    finally:
        engine.dispose()


@router.put("/{provider_id}/credential", summary="Provision write-only provider credential")
def provision_credential(provider_id: str, payload: ProviderCredential, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    try:
        new_ref = store_provider_secret(payload.api_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Enter a valid provider API credential") from exc
    engine = _engine()
    old_ref: str | None = None
    try:
        try:
            with engine.begin() as connection:
                current = _fetch_provider(connection, provider_id, for_update=True)
                old_ref = current["credential_ref"]
                connection.execute(text("""
                    UPDATE ai_providers
                    SET credential_ref=:credential_ref, last_connection_status='UNTESTED', last_connection_at=NULL,
                        last_error_code=NULL, state='DISABLED', updated_at=now()
                    WHERE provider_id=CAST(:provider_id AS uuid)
                """), {"credential_ref": new_ref, "provider_id": provider_id})
        except Exception:
            delete_provider_secret(new_ref)
            raise
    finally:
        engine.dispose()
    delete_provider_secret(old_ref)
    return {"provider_id": provider_id, "credential_configured": True, "state": "DISABLED"}


@router.delete("/{provider_id}/credential", summary="Remove provider credential")
def remove_credential(provider_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    old_ref: str | None = None
    try:
        with engine.begin() as connection:
            current = _fetch_provider(connection, provider_id, for_update=True)
            old_ref = current["credential_ref"]
            connection.execute(text("""
                UPDATE ai_providers
                SET credential_ref=NULL, state='DISABLED', last_connection_status='UNTESTED',
                    last_connection_at=NULL, last_error_code=NULL, updated_at=now()
                WHERE provider_id=CAST(:provider_id AS uuid)
            """), {"provider_id": provider_id})
    finally:
        engine.dispose()
    delete_provider_secret(old_ref)
    return {"provider_id": provider_id, "credential_configured": False, "state": "DISABLED"}


def _provider_and_secret(provider_id: str) -> tuple[dict[str, Any], str]:
    engine = _engine()
    try:
        with engine.connect() as connection:
            provider = dict(_fetch_provider(connection, provider_id))
    finally:
        engine.dispose()
    secret = read_provider_secret(provider.get("credential_ref"))
    if secret is None:
        raise HTTPException(status_code=409, detail="Provider credential is not configured")
    return provider, secret


@router.post("/{provider_id}/test", summary="Test provider connection")
def test_provider(provider_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    provider, secret = _provider_and_secret(provider_id)
    error_code: str | None = None
    try:
        payload = _get_json(provider, secret)
        _normalize_models(provider, payload)
        result = "HEALTHY"
    except RuntimeError as exc:
        result = "ERROR"
        error_code = _safe_error_code(exc)
    engine = _engine()
    try:
        with engine.begin() as connection:
            connection.execute(text("""
                UPDATE ai_providers
                SET last_connection_status=:status, last_connection_at=now(), last_error_code=:error_code, updated_at=now()
                WHERE provider_id=CAST(:provider_id AS uuid)
            """), {"provider_id": provider_id, "status": result, "error_code": error_code})
    finally:
        engine.dispose()
    if result != "HEALTHY":
        raise HTTPException(status_code=502, detail=f"Provider connection failed ({error_code})")
    return {"provider_id": provider_id, "connection_status": "HEALTHY"}


@router.post("/{provider_id}/models/fetch", summary="Fetch and normalize provider models")
def fetch_models(provider_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    provider, secret = _provider_and_secret(provider_id)
    try:
        payload = _get_json(provider, secret)
        models = _normalize_models(provider, payload)
    except RuntimeError as exc:
        error_code = _safe_error_code(exc)
        engine = _engine()
        try:
            with engine.begin() as connection:
                connection.execute(text("""
                    UPDATE ai_providers SET last_model_fetch_status='ERROR', last_model_fetch_at=now(),
                        last_error_code=:error_code, updated_at=now()
                    WHERE provider_id=CAST(:provider_id AS uuid)
                """), {"provider_id": provider_id, "error_code": error_code})
        finally:
            engine.dispose()
        raise HTTPException(status_code=502, detail=f"Model fetch failed ({error_code})") from exc

    engine = _engine()
    try:
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM ai_provider_models WHERE provider_id=CAST(:provider_id AS uuid)"), {"provider_id": provider_id})
            for model in models:
                connection.execute(text("""
                    INSERT INTO ai_provider_models (
                        provider_id, model_id, display_name, availability, supports_text, supports_vision,
                        supports_tools, supports_structured_output, context_window, max_output_tokens, provider_metadata
                    ) VALUES (
                        CAST(:provider_id AS uuid), :model_id, :display_name, 'AVAILABLE', :supports_text, :supports_vision,
                        :supports_tools, :supports_structured_output, :context_window, :max_output_tokens, CAST(:provider_metadata AS jsonb)
                    )
                """), {**model, "provider_id": provider_id, "provider_metadata": json.dumps(model["provider_metadata"])})
            connection.execute(text("""
                UPDATE ai_providers SET last_model_fetch_status='SUCCESS', last_model_fetch_at=now(),
                    last_connection_status='HEALTHY', last_connection_at=now(), last_error_code=NULL, updated_at=now()
                WHERE provider_id=CAST(:provider_id AS uuid)
            """), {"provider_id": provider_id})
    finally:
        engine.dispose()
    return {"provider_id": provider_id, "model_count": len(models), "model_fetch_status": "SUCCESS"}


@router.get("/{provider_id}/models", summary="List normalized provider models", dependencies=[Depends(require_owner_session)])
def list_models(provider_id: str, response: Response) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            _fetch_provider(connection, provider_id)
            rows = connection.execute(text("""
                SELECT provider_model_id::text AS provider_model_id, provider_id::text AS provider_id,
                       model_id, display_name, availability, supports_text, supports_vision, supports_tools,
                       supports_structured_output, context_window, max_output_tokens, provider_metadata,
                       fetched_at, updated_at
                FROM ai_provider_models
                WHERE provider_id=CAST(:provider_id AS uuid)
                ORDER BY lower(display_name), model_id
            """), {"provider_id": provider_id}).mappings().all()
        return {"items": [dict(row) for row in rows], "count": len(rows)}
    finally:
        engine.dispose()


def _set_provider_state(provider_id: str, target: str) -> dict[str, Any]:
    engine = _engine()
    try:
        with engine.begin() as connection:
            current = _fetch_provider(connection, provider_id, for_update=True)
            if target == "ENABLED":
                if not current["credential_ref"]:
                    raise HTTPException(status_code=409, detail="Configure a provider credential before enabling")
                if current["last_connection_status"] != "HEALTHY" or current["last_model_fetch_status"] != "SUCCESS":
                    raise HTTPException(status_code=409, detail="Test connection and fetch models before enabling")
            row = connection.execute(text("""
                UPDATE ai_providers SET state=:state, updated_at=now()
                WHERE provider_id=CAST(:provider_id AS uuid)
                RETURNING provider_id::text AS provider_id, display_name, provider_kind, base_url,
                          credential_ref, compatibility_mode, state, last_connection_status,
                          last_connection_at, last_model_fetch_status, last_model_fetch_at,
                          last_error_code, created_by_user_id::text AS created_by_user_id,
                          created_at, updated_at
            """), {"provider_id": provider_id, "state": target}).mappings().one()
        return _provider_dict(row)
    finally:
        engine.dispose()


@router.post("/{provider_id}/enable", summary="Enable AI provider")
def enable_provider(provider_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    return _set_provider_state(provider_id, "ENABLED")


@router.post("/{provider_id}/disable", summary="Disable AI provider")
def disable_provider(provider_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    return _set_provider_state(provider_id, "DISABLED")
