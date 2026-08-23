from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app.access_request_confirmed import router as access_request_confirmed_router
from app.account_password_confirmed import router as account_password_confirmed_router
from app.agent_management import router as agent_management_router
from app.audit_events import router as audit_events_router
from app.credential_lifecycle import router as credential_lifecycle_router
from app.dashboard import ASSET_DIR, DASHBOARD_CSP, router as dashboard_router
from app.dashboard_auth import SESSION_COOKIE, validate_session_token
from app.dashboard_login import router as dashboard_login_router
from app.db import database_readiness
from app.email_recovery import router as email_recovery_router
from app.email_recovery_page import router as email_recovery_page_router
from app.mcp_agent_binding import router as mcp_agent_binding_router
from app.mcp_oauth import router as mcp_oauth_router
from app.mcp_server import mcp, mcp_http_app
from app.nanogpt_catalog import router as nanogpt_catalog_router
from app.provider_model_view import router as provider_model_view_router
from app.provider_registry import router as provider_registry_router
from app.read_api import router as read_router
from app.recovery_identifier import router as recovery_identifier_router
from app.saved_model_catalog import router as saved_model_catalog_router
from app.shadow_read_api import router as shadow_read_router
from app.user_management import router as user_management_router

SERVICE_NAME = "medicine-store-assistant-api"
SERVICE_VERSION = os.getenv("MSA_SERVICE_VERSION", "0.1.0-dev")
ENVIRONMENT = os.getenv("MSA_ENVIRONMENT", "development")
BUILD_SHA = os.getenv("MSA_BUILD_SHA", "unknown")
SAVED_MODEL_ASSET_VERSION = "f72d31-2"
AGENT_POLISH_ASSET_VERSION = "f72d31-agentui-1"
MCP_BINDING_ASSET_VERSION = "f72d4a-mcpbind-1"
AUDIT_ASSET_VERSION = "f73a-mcpaudit-1"


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title="Medicine Store Assistant Inventory API",
    version=SERVICE_VERSION,
    description=(
        "Typed API boundary for the Medicine Store Assistant backend. "
        "Authenticated inventory, canonical human identity/User Management/credential and email-recovery lifecycle, catalogue, "
        "test-only shadow reads, the F7 dashboard, F7.2D named Agent Management/multi-agent session foundation, "
        "Owner-only Provider Registry/model discovery, tested saved-model catalog and agent model-assignment foundation, "
        "external MCP named-agent binding, minimal MCP audit evidence, NanoGPT detailed catalog enrichment, and the MCP/OAuth protocol surface are available; "
        "canonical inventory writes remain disabled."
    ),
    lifespan=app_lifespan,
)


@app.middleware("http")
async def dashboard_login_gate(request: Request, call_next):
    path = request.url.path.rstrip("/") or "/"
    token = request.cookies.get(SESSION_COOKIE)
    authenticated = validate_session_token(token)

    if path == "/dashboard" and not authenticated:
        return RedirectResponse(url="/dashboard/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    if path == "/dashboard/login" and authenticated and request.query_params.get("verify-email") != "1":
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    return await call_next(request)


def _dashboard_security_headers(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Content-Security-Policy"] = DASHBOARD_CSP
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"


@app.get("/dashboard", include_in_schema=False)
def dashboard_shell_with_saved_model_assets() -> HTMLResponse:
    html = (ASSET_DIR / "dashboard.html").read_text(encoding="utf-8")
    html = html.replace(
        "</head>",
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_saved_models.css?v={SAVED_MODEL_ASSET_VERSION}">\n'
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_agent_polish.css?v={AGENT_POLISH_ASSET_VERSION}">\n'
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_mcp_binding.css?v={MCP_BINDING_ASSET_VERSION}">\n'
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_audit.css?v={AUDIT_ASSET_VERSION}">\n</head>',
        1,
    )
    html = html.replace(
        "</body>",
        f'<script src="/dashboard/assets/dashboard_saved_models.js?v={SAVED_MODEL_ASSET_VERSION}" defer></script>\n'
        f'<script src="/dashboard/assets/dashboard_mcp_binding.js?v={MCP_BINDING_ASSET_VERSION}" defer></script>\n'
        f'<script src="/dashboard/assets/dashboard_audit.js?v={AUDIT_ASSET_VERSION}" defer></script>\n</body>',
        1,
    )
    response = HTMLResponse(html)
    _dashboard_security_headers(response)
    return response


@app.get("/dashboard/assets/dashboard_saved_models.css", include_in_schema=False)
def saved_model_css() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_saved_models.css", media_type="text/css")
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/dashboard/assets/dashboard_agent_polish.css", include_in_schema=False)
def agent_polish_css() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_agent_polish.css", media_type="text/css")
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/dashboard/assets/dashboard_mcp_binding.css", include_in_schema=False)
def mcp_binding_css() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_mcp_binding.css", media_type="text/css")
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/dashboard/assets/dashboard_audit.css", include_in_schema=False)
def audit_css() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_audit.css", media_type="text/css")
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/dashboard/assets/dashboard_saved_models.js", include_in_schema=False)
def saved_model_js() -> Response:
    javascript = (ASSET_DIR / "dashboard_saved_models.js").read_text(encoding="utf-8")
    javascript = javascript.replace("{childList:true,subtree:true}", "{childList:true,subtree:false}")
    response = Response(content=javascript, media_type="text/javascript")
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/dashboard/assets/dashboard_mcp_binding.js", include_in_schema=False)
def mcp_binding_js() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_mcp_binding.js", media_type="text/javascript")
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/dashboard/assets/dashboard_audit.js", include_in_schema=False)
def audit_js() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_audit.js", media_type="text/javascript")
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


app.include_router(dashboard_login_router)
app.include_router(dashboard_router)
app.include_router(email_recovery_page_router)
app.include_router(user_management_router)
app.include_router(agent_management_router)
app.include_router(mcp_agent_binding_router)
app.include_router(audit_events_router)
app.include_router(provider_registry_router)
app.include_router(nanogpt_catalog_router)
app.include_router(provider_model_view_router)
app.include_router(saved_model_catalog_router)
app.include_router(access_request_confirmed_router)
app.include_router(credential_lifecycle_router)
app.include_router(account_password_confirmed_router)
app.include_router(email_recovery_router)
app.include_router(recovery_identifier_router)
app.include_router(read_router)
app.include_router(shadow_read_router)
app.include_router(mcp_oauth_router)


@app.get("/health", tags=["system"], summary="Service health")
def health() -> dict[str, object]:
    return {
        "ok": True,
        "service": SERVICE_NAME,
        "environment": ENVIRONMENT,
        "version": SERVICE_VERSION,
        "build_sha": BUILD_SHA,
        "database_canonical": False,
        "mcp_surface": "full-schema-policy-gated",
        "mcp_oauth": "enabled",
        "mcp_named_agent_binding": "f7.2d4a",
        "mcp_audit_evidence": "f7.3a",
        "agent_management": "f7.2d2",
        "provider_registry": "f7.2d3",
        "saved_model_catalog": "f7.2d3.1",
        "nanogpt_detailed_catalog": "enabled",
        "production_inventory_writes": False,
    }


@app.get("/ready", tags=["system"], summary="Database readiness")
def ready(response: Response) -> dict[str, object]:
    readiness = database_readiness()
    if not readiness["ok"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        **readiness,
        "service": SERVICE_NAME,
        "database_canonical": False,
    }


app.mount("/", mcp_http_app)
