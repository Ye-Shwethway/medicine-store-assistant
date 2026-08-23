from __future__ import annotations

import base64
import hashlib
import html
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode, urlparse

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.dashboard_auth import authenticate_user
from app.db import normalize_database_url

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
PUBLIC_BASE_URL = os.getenv("MSA_PUBLIC_BASE_URL", "https://inventory.drthorne.uk").rstrip("/")
ISSUER = os.getenv("MSA_MCP_AUTH_ISSUER_URL", f"{PUBLIC_BASE_URL}/oauth").rstrip("/")
RESOURCE = os.getenv("MSA_MCP_RESOURCE_URL", f"{PUBLIC_BASE_URL}/mcp").rstrip("/")

TRANSPORT_SCOPES = frozenset({"mcp:connect", "offline_access"})
DEFAULT_SCOPES = ("mcp:connect", "offline_access")
AUTH_REQUEST_TTL = timedelta(minutes=10)
AUTH_CODE_TTL = timedelta(minutes=5)
ACCESS_TOKEN_TTL = timedelta(hours=1)
REFRESH_TOKEN_TTL = timedelta(days=90)

router = APIRouter(tags=["mcp-oauth"])


def _engine():
    if not DATABASE_URL:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OAuth database unavailable")
    return create_engine(normalize_database_url(DATABASE_URL), pool_pre_ping=True)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _token(prefix: str) -> str:
    return prefix + secrets.token_urlsafe(36)


def _valid_redirect(uri: str) -> bool:
    try:
        parsed = urlparse(uri)
    except ValueError:
        return False
    if parsed.scheme == "https" and parsed.netloc:
        return True
    return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}


def _scope_list(scope: str | None) -> list[str]:
    requested = [part for part in (scope or "").split() if part]
    if not requested:
        requested = list(DEFAULT_SCOPES)
    if "mcp:connect" not in requested:
        requested.append("mcp:connect")
    unknown = set(requested) - TRANSPORT_SCOPES
    if unknown:
        raise HTTPException(status_code=400, detail="Unsupported OAuth scope")
    return sorted(set(requested))


def _json_error(error: str, description: str, code: int = 400) -> JSONResponse:
    return JSONResponse({"error": error, "error_description": description}, status_code=code)


def _redirect_error(redirect_uri: str, state_value: str | None, error: str, description: str) -> RedirectResponse:
    params = {"error": error, "error_description": description}
    if state_value:
        params["state"] = state_value
    separator = "&" if "?" in redirect_uri else "?"
    return RedirectResponse(redirect_uri + separator + urlencode(params), status_code=302)


def _metadata() -> dict[str, Any]:
    return {
        "issuer": ISSUER,
        "authorization_endpoint": f"{ISSUER}/authorize",
        "token_endpoint": f"{ISSUER}/token",
        "registration_endpoint": f"{ISSUER}/register",
        "revocation_endpoint": f"{ISSUER}/revoke",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_methods_supported": ["none"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["mcp:connect", "offline_access"],
        "service_documentation": f"{PUBLIC_BASE_URL}/docs",
    }


@router.get("/.well-known/oauth-authorization-server/oauth", include_in_schema=False)
def oauth_metadata_path_issuer() -> dict[str, Any]:
    return _metadata()


@router.get("/oauth/.well-known/oauth-authorization-server", include_in_schema=False)
def oauth_metadata_compat() -> dict[str, Any]:
    return _metadata()


@router.get("/.well-known/openid-configuration/oauth", include_in_schema=False)
def oidc_compat_metadata() -> dict[str, Any]:
    return _metadata()


@router.post("/oauth/register")
async def register_client(request: Request) -> JSONResponse:
    try:
        payload = await request.json()
    except Exception:
        return _json_error("invalid_client_metadata", "JSON body required")

    redirect_uris = payload.get("redirect_uris")
    if not isinstance(redirect_uris, list) or not redirect_uris or len(redirect_uris) > 10:
        return _json_error("invalid_redirect_uri", "redirect_uris is required")
    clean_redirects = [str(value).strip() for value in redirect_uris]
    if any(not _valid_redirect(uri) for uri in clean_redirects):
        return _json_error("invalid_redirect_uri", "Only HTTPS or loopback redirect URIs are allowed")

    auth_method = str(payload.get("token_endpoint_auth_method") or "none")
    if auth_method != "none":
        return _json_error("invalid_client_metadata", "Only public PKCE clients are supported")

    grant_types = payload.get("grant_types") or ["authorization_code", "refresh_token"]
    response_types = payload.get("response_types") or ["code"]
    if not set(grant_types).issubset({"authorization_code", "refresh_token"}) or set(response_types) != {"code"}:
        return _json_error("invalid_client_metadata", "Unsupported grant or response type")

    client_id = "msa_mcp_" + secrets.token_urlsafe(24)
    client_name = str(payload.get("client_name") or "ChatGPT MCP Client").strip()[:200] or "ChatGPT MCP Client"

    engine = _engine()
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO mcp_oauth_clients
                      (client_id, client_name, redirect_uris, grant_types, response_types, token_endpoint_auth_method)
                    VALUES (:client_id, :client_name, CAST(:redirect_uris AS jsonb), CAST(:grant_types AS jsonb),
                            CAST(:response_types AS jsonb), 'none')
                    """
                ),
                {
                    "client_id": client_id,
                    "client_name": client_name,
                    "redirect_uris": __import__("json").dumps(clean_redirects),
                    "grant_types": __import__("json").dumps(list(grant_types)),
                    "response_types": __import__("json").dumps(list(response_types)),
                },
            )
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="OAuth registration unavailable") from exc
    finally:
        engine.dispose()

    return JSONResponse(
        {
            "client_id": client_id,
            "client_id_issued_at": int(time.time()),
            "client_name": client_name,
            "redirect_uris": clean_redirects,
            "grant_types": list(grant_types),
            "response_types": list(response_types),
            "token_endpoint_auth_method": "none",
        },
        status_code=201,
    )


@router.get("/oauth/authorize", response_class=HTMLResponse, response_model=None)
def authorize(
    client_id: str,
    redirect_uri: str,
    response_type: str = "code",
    scope: str | None = None,
    state: str | None = None,
    code_challenge: str | None = None,
    code_challenge_method: str | None = None,
    resource: str | None = None,
) -> Any:
    engine = _engine()
    try:
        with engine.connect() as connection:
            client = connection.execute(
                text(
                    """
                    SELECT client_id, client_name, redirect_uris
                    FROM mcp_oauth_clients
                    WHERE client_id = :client_id AND revoked_at IS NULL
                    """
                ),
                {"client_id": client_id},
            ).mappings().first()
    finally:
        engine.dispose()

    if client is None:
        raise HTTPException(status_code=400, detail="Unknown OAuth client")
    registered_redirects = list(client["redirect_uris"] or [])
    if redirect_uri not in registered_redirects:
        raise HTTPException(status_code=400, detail="Redirect URI mismatch")
    if response_type != "code":
        return _redirect_error(redirect_uri, state, "unsupported_response_type", "Only authorization code is supported")
    if not code_challenge or code_challenge_method != "S256":
        return _redirect_error(redirect_uri, state, "invalid_request", "PKCE S256 is required")

    try:
        scopes = _scope_list(scope)
    except HTTPException:
        return _redirect_error(redirect_uri, state, "invalid_scope", "Unsupported OAuth scope")

    resource_value = (resource or RESOURCE).rstrip("/")
    if resource_value != RESOURCE:
        return _redirect_error(redirect_uri, state, "invalid_target", "OAuth resource does not match MSA MCP")

    expires_at = _now() + AUTH_REQUEST_TTL
    engine = _engine()
    try:
        with engine.begin() as connection:
            request_id = connection.execute(
                text(
                    """
                    INSERT INTO mcp_oauth_authorization_requests
                      (client_id, redirect_uri, state, oauth_scopes, resource,
                       code_challenge, code_challenge_method, expires_at)
                    VALUES (:client_id, :redirect_uri, :state, :oauth_scopes, :resource,
                            :code_challenge, 'S256', :expires_at)
                    RETURNING request_id::text
                    """
                ),
                {
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "state": state,
                    "oauth_scopes": scopes,
                    "resource": RESOURCE,
                    "code_challenge": code_challenge,
                    "expires_at": expires_at,
                },
            ).scalar_one()
    finally:
        engine.dispose()

    safe_name = html.escape(str(client["client_name"]))
    safe_request = html.escape(request_id)
    return HTMLResponse(
        f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Authorize Medicine Store Assistant</title>
<style>body{{font-family:system-ui,sans-serif;max-width:480px;margin:48px auto;padding:0 20px;color:#172033}}label{{display:block;margin-top:16px;font-weight:600}}input{{width:100%;box-sizing:border-box;padding:12px;margin-top:6px}}button{{margin-top:22px;padding:12px 18px;min-height:44px}}.note{{color:#596579;line-height:1.5}}</style></head>
<body><h1>Connect Medicine Store Assistant</h1>
<p class="note"><strong>{safe_name}</strong> is requesting an authenticated MCP connection. Initial MSA execution remains read-only and policy-gated. Signing in does not enable inventory writes.</p>
<form method="post" action="/oauth/authorize/login">
<input type="hidden" name="request_id" value="{safe_request}">
<label for="username">MSA username</label><input id="username" name="username" autocomplete="username" required>
<label for="password">Password</label><input id="password" type="password" name="password" autocomplete="current-password" required>
<button type="submit">Authorize MCP connection</button></form></body></html>"""
    )


@router.post("/oauth/authorize/login", response_model=None)
def authorize_login(
    request_id: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
) -> Any:
    engine = _engine()
    try:
        with engine.connect() as connection:
            pending = connection.execute(
                text(
                    """
                    SELECT request_id::text, client_id, redirect_uri, state, oauth_scopes,
                           resource, code_challenge, code_challenge_method, expires_at, consumed_at
                    FROM mcp_oauth_authorization_requests
                    WHERE request_id::text = :request_id
                    """
                ),
                {"request_id": request_id},
            ).mappings().first()
    finally:
        engine.dispose()

    if pending is None or pending["consumed_at"] is not None or pending["expires_at"] <= _now():
        return HTMLResponse("Authorization request expired or invalid.", status_code=400)

    principal = authenticate_user(username, password)
    if principal is None:
        return HTMLResponse("Invalid MSA credentials. Return to ChatGPT and retry authorization.", status_code=401)
    if principal["role"] != "OWNER":
        return HTMLResponse("Only the MSA Owner can authorize the initial MCP control-plane connection.", status_code=403)

    code = _token("msa_code_")
    code_digest = _digest(code)
    code_expires = _now() + AUTH_CODE_TTL
    engine = _engine()
    try:
        with engine.begin() as connection:
            grant_id = connection.execute(
                text(
                    """
                    INSERT INTO mcp_oauth_grants (client_id, user_id, state, capability_scopes)
                    VALUES (:client_id, CAST(:user_id AS uuid), 'ACTIVE', ARRAY['mcp:read']::text[])
                    ON CONFLICT (client_id, user_id)
                    DO UPDATE SET state = 'ACTIVE', updated_at = now()
                    RETURNING grant_id::text
                    """
                ),
                {"client_id": pending["client_id"], "user_id": principal["user_id"]},
            ).scalar_one()
            connection.execute(
                text(
                    """
                    INSERT INTO mcp_oauth_authorization_codes
                      (code_digest, grant_id, client_id, redirect_uri, oauth_scopes, resource,
                       code_challenge, code_challenge_method, expires_at)
                    VALUES (:code_digest, CAST(:grant_id AS uuid), :client_id, :redirect_uri,
                            :oauth_scopes, :resource, :code_challenge, :code_challenge_method, :expires_at)
                    """
                ),
                {
                    "code_digest": code_digest,
                    "grant_id": grant_id,
                    "client_id": pending["client_id"],
                    "redirect_uri": pending["redirect_uri"],
                    "oauth_scopes": list(pending["oauth_scopes"] or []),
                    "resource": pending["resource"],
                    "code_challenge": pending["code_challenge"],
                    "code_challenge_method": pending["code_challenge_method"],
                    "expires_at": code_expires,
                },
            )
            connection.execute(
                text("UPDATE mcp_oauth_authorization_requests SET consumed_at = now() WHERE request_id::text = :request_id"),
                {"request_id": request_id},
            )
    finally:
        engine.dispose()

    params = {"code": code}
    if pending["state"]:
        params["state"] = str(pending["state"])
    separator = "&" if "?" in pending["redirect_uri"] else "?"
    return RedirectResponse(str(pending["redirect_uri"]) + separator + urlencode(params), status_code=302)


def _issue_tokens(connection, *, grant_id: str, client_id: str, oauth_scopes: list[str], resource: str) -> dict[str, Any]:
    access_token = _token("msa_at_")
    access_expires = _now() + ACCESS_TOKEN_TTL
    connection.execute(
        text(
            """
            INSERT INTO mcp_oauth_tokens
              (token_digest, grant_id, client_id, token_kind, oauth_scopes, resource, expires_at)
            VALUES (:digest, CAST(:grant_id AS uuid), :client_id, 'ACCESS', :scopes, :resource, :expires_at)
            """
        ),
        {
            "digest": _digest(access_token),
            "grant_id": grant_id,
            "client_id": client_id,
            "scopes": oauth_scopes,
            "resource": resource,
            "expires_at": access_expires,
        },
    )
    result: dict[str, Any] = {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": int(ACCESS_TOKEN_TTL.total_seconds()),
        "scope": " ".join(oauth_scopes),
    }
    if "offline_access" in oauth_scopes:
        refresh_token = _token("msa_rt_")
        refresh_expires = _now() + REFRESH_TOKEN_TTL
        connection.execute(
            text(
                """
                INSERT INTO mcp_oauth_tokens
                  (token_digest, grant_id, client_id, token_kind, oauth_scopes, resource, expires_at)
                VALUES (:digest, CAST(:grant_id AS uuid), :client_id, 'REFRESH', :scopes, :resource, :expires_at)
                """
            ),
            {
                "digest": _digest(refresh_token),
                "grant_id": grant_id,
                "client_id": client_id,
                "scopes": oauth_scopes,
                "resource": resource,
                "expires_at": refresh_expires,
            },
        )
        result["refresh_token"] = refresh_token
    return result


@router.post("/oauth/token")
def token_endpoint(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    code: str | None = Form(default=None),
    redirect_uri: str | None = Form(default=None),
    code_verifier: str | None = Form(default=None),
    refresh_token: str | None = Form(default=None),
    resource: str | None = Form(default=None),
    scope: str | None = Form(default=None),
) -> JSONResponse:
    engine = _engine()
    try:
        with engine.begin() as connection:
            client = connection.execute(
                text("SELECT client_id FROM mcp_oauth_clients WHERE client_id = :client_id AND revoked_at IS NULL"),
                {"client_id": client_id},
            ).first()
            if client is None:
                return _json_error("invalid_client", "Unknown or revoked client", 401)

            if grant_type == "authorization_code":
                if not code or not redirect_uri or not code_verifier:
                    return _json_error("invalid_request", "code, redirect_uri and code_verifier are required")
                stored = connection.execute(
                    text(
                        """
                        SELECT code_digest, grant_id::text, client_id, redirect_uri, oauth_scopes,
                               resource, code_challenge, code_challenge_method, expires_at, consumed_at
                        FROM mcp_oauth_authorization_codes
                        WHERE code_digest = :digest
                        FOR UPDATE
                        """
                    ),
                    {"digest": _digest(code)},
                ).mappings().first()
                if (
                    stored is None
                    or stored["client_id"] != client_id
                    or stored["redirect_uri"] != redirect_uri
                    or stored["consumed_at"] is not None
                    or stored["expires_at"] <= _now()
                    or stored["code_challenge_method"] != "S256"
                    or not secrets.compare_digest(_pkce_challenge(code_verifier), str(stored["code_challenge"]))
                ):
                    return _json_error("invalid_grant", "Authorization code is invalid or expired")
                if resource and resource.rstrip("/") != str(stored["resource"]).rstrip("/"):
                    return _json_error("invalid_target", "Resource mismatch")
                connection.execute(
                    text("UPDATE mcp_oauth_authorization_codes SET consumed_at = now() WHERE code_digest = :digest"),
                    {"digest": stored["code_digest"]},
                )
                payload = _issue_tokens(
                    connection,
                    grant_id=stored["grant_id"],
                    client_id=client_id,
                    oauth_scopes=list(stored["oauth_scopes"] or []),
                    resource=str(stored["resource"]),
                )
                return JSONResponse(payload, headers={"Cache-Control": "no-store", "Pragma": "no-cache"})

            if grant_type == "refresh_token":
                if not refresh_token:
                    return _json_error("invalid_request", "refresh_token is required")
                stored = connection.execute(
                    text(
                        """
                        SELECT t.token_digest, t.grant_id::text, t.client_id, t.oauth_scopes, t.resource,
                               t.expires_at, t.revoked_at, g.state AS grant_state, u.state AS user_state
                        FROM mcp_oauth_tokens t
                        JOIN mcp_oauth_grants g ON g.grant_id = t.grant_id
                        JOIN users u ON u.user_id = g.user_id
                        WHERE t.token_digest = :digest AND t.token_kind = 'REFRESH'
                        FOR UPDATE OF t
                        """
                    ),
                    {"digest": _digest(refresh_token)},
                ).mappings().first()
                if (
                    stored is None
                    or stored["client_id"] != client_id
                    or stored["revoked_at"] is not None
                    or stored["expires_at"] <= _now()
                    or stored["grant_state"] != "ACTIVE"
                    or stored["user_state"] != "ACTIVE"
                ):
                    return _json_error("invalid_grant", "Refresh token is invalid or expired")
                if resource and resource.rstrip("/") != str(stored["resource"]).rstrip("/"):
                    return _json_error("invalid_target", "Resource mismatch")
                requested_scopes = _scope_list(scope) if scope else list(stored["oauth_scopes"] or [])
                if not set(requested_scopes).issubset(set(stored["oauth_scopes"] or [])):
                    return _json_error("invalid_scope", "Refresh cannot expand OAuth scopes")
                connection.execute(
                    text("UPDATE mcp_oauth_tokens SET revoked_at = now() WHERE token_digest = :digest"),
                    {"digest": stored["token_digest"]},
                )
                payload = _issue_tokens(
                    connection,
                    grant_id=stored["grant_id"],
                    client_id=client_id,
                    oauth_scopes=requested_scopes,
                    resource=str(stored["resource"]),
                )
                return JSONResponse(payload, headers={"Cache-Control": "no-store", "Pragma": "no-cache"})

            return _json_error("unsupported_grant_type", "Only authorization_code and refresh_token are supported")
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="OAuth token service unavailable") from exc
    finally:
        engine.dispose()


@router.post("/oauth/revoke")
def revoke_token(
    token: str = Form(...),
    client_id: str = Form(...),
) -> JSONResponse:
    engine = _engine()
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE mcp_oauth_tokens
                    SET revoked_at = COALESCE(revoked_at, now())
                    WHERE token_digest = :digest AND client_id = :client_id
                    """
                ),
                {"digest": _digest(token), "client_id": client_id},
            )
    finally:
        engine.dispose()
    return JSONResponse({}, status_code=200)
