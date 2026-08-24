from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app.access_request_confirmed import router as access_request_confirmed_router
from app.account_password_confirmed import router as account_password_confirmed_router
from app.agent_management import router as agent_management_router
from app.agent_model_assignments import router as agent_model_assignments_router
from app.ai_workspace_access import router as ai_workspace_access_router
from app.ai_workspace_attachments import router as ai_workspace_attachments_router
from app.ai_workspace_chat import router as ai_workspace_chat_router
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
import app.mcp_shadow_reads as _mcp_shadow_reads  # noqa: F401
from app.nanogpt_catalog import router as nanogpt_catalog_router
from app.native_agent_runtime import router as native_agent_runtime_router
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
AGENT_ASSIGNMENT_GUARD_ASSET_VERSION = "f72d4-preflight-1"
NATIVE_AGENT_TEST_ASSET_VERSION = "f72d4d-native-test-1"
AI_WORKSPACE_ACCESS_ASSET_VERSION = "f72d4-access-1"
AI_WORKSPACE_ASSET_VERSION = "f72d47b-attachments-1"
MULTI_AGENT_REVIEW_ASSET_VERSION = "f72d48-review-ui-2"
MULTI_AGENT_LIVE_EXPORT_ASSET_VERSION = "f72d48-live-export-3"
AGENT_POLISH_ASSET_VERSION = "f72d31-agentui-1"
MCP_BINDING_ASSET_VERSION = "f72d4a-mcpbind-2"
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
        "Authenticated inventory, human identity/User Management, native AI Agent Management, "
        "Provider Registry/model assignments, MCP-independent internal-agent inference, AI Workspace access policy, durable Chat, bounded native reads, attachment evidence and Owner-only native REVIEW are available; "
        "external MCP/OAuth typed operations and audit evidence remain peer paths; canonical inventory writes remain disabled."
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


app.include_router(dashboard_login_router)
app.include_router(email_recovery_page_router)
app.include_router(email_recovery_router)
app.include_router(account_password_confirmed_router)
app.include_router(read_router)
app.include_router(shadow_read_router)
app.include_router(user_management_router)
app.include_router(access_request_confirmed_router)
app.include_router(credential_lifecycle_router)
app.include_router(agent_management_router)
app.include_router(provider_registry_router)
app.include_router(saved_model_catalog_router)
app.include_router(agent_model_assignments_router)
app.include_router(ai_workspace_access_router)
app.include_router(ai_workspace_chat_router)
app.include_router(ai_workspace_attachments_router)
app.include_router(mcp_oauth_router)
app.include_router(mcp_agent_binding_router)
app.include_router(audit_events_router)
app.include_router(native_agent_runtime_router)
app.include_router(provider_model_view_router)
app.include_router(dashboard_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "environment": ENVIRONMENT,
        "build_sha": BUILD_SHA,
        "status": "ok",
    }


@app.get("/ready")
def ready(response: Response) -> dict[str, object]:
    readiness = database_readiness()
    if readiness["status"] != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return readiness


@app.get("/dashboard/app.css", include_in_schema=False)
def dashboard_css() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard.css", media_type="text/css")
    _dashboard_security_headers(response)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.get("/dashboard/app.js", include_in_schema=False)
def dashboard_js() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard.js", media_type="application/javascript")
    _dashboard_security_headers(response)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.get("/dashboard/agents.css", include_in_schema=False)
def dashboard_agents_css() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_agents.css", media_type="text/css")
    _dashboard_security_headers(response)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.get("/dashboard/agents.js", include_in_schema=False)
def dashboard_agents_js() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_agents.js", media_type="application/javascript")
    _dashboard_security_headers(response)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.get("/dashboard/mcp-binding.css", include_in_schema=False)
def dashboard_mcp_binding_css() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_mcp_binding.css", media_type="text/css")
    _dashboard_security_headers(response)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.get("/dashboard/mcp-binding.js", include_in_schema=False)
def dashboard_mcp_binding_js() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_mcp_binding.js", media_type="application/javascript")
    _dashboard_security_headers(response)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.get("/dashboard/audit.css", include_in_schema=False)
def dashboard_audit_css() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_audit.css", media_type="text/css")
    _dashboard_security_headers(response)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.get("/dashboard/audit.js", include_in_schema=False)
def dashboard_audit_js() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard_audit.js", media_type="application/javascript")
    _dashboard_security_headers(response)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.mount("/mcp", mcp_http_app)
