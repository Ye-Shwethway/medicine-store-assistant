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
from app.dashboard_asset_version import asset_bundle_version
from app.dashboard_auth import SESSION_COOKIE, validate_session_token
from app.dashboard_login import router as dashboard_login_router
from app.db import database_readiness
from app.email_recovery import router as email_recovery_router
from app.email_recovery_page import router as email_recovery_page_router
from app.inventory_view_engine import router as inventory_view_router
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
SAVED_MODEL_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_saved_models.js", "dashboard_saved_models.css")
AGENT_ASSIGNMENT_GUARD_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_agent_assignment_guard.js")
NATIVE_AGENT_TEST_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_native_agent_test.js")
AI_WORKSPACE_ACCESS_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_ai_workspace_access.js")
AI_WORKSPACE_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_ai_workspace.js", "dashboard_ai_workspace.css")
MULTI_AGENT_REVIEW_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_multi_agent_review.js", "dashboard_multi_agent_review.css")
MULTI_AGENT_LIVE_EXPORT_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_multi_agent_live_export.js", "dashboard_multi_agent_live_export.css")
AGENT_POLISH_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_agent_polish.css")
MCP_BINDING_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_mcp_binding.js", "dashboard_mcp_binding.css")
AUDIT_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_audit.js", "dashboard_audit.css")
INVENTORY_VIEW_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_inventory_views.js", "dashboard_inventory_views.css")


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
    response.headers["X-Content-Type-Options"] = "nosniff"


AI_WORKSPACE_NAV = '<button class="workspace-nav-btn" id="aiWorkspaceNav" type="button">AI Workspace</button>'
AI_WORKSPACE_PANEL = r'''
        <section class="view" data-panel="ai-workspace">
          <div class="management-head">
            <div><h2>AI Workspace</h2><p>Operational Chat and Owner-only native Review with Medicine Store Assistant agents. ChatGPT and public MCP are not required for the native path.</p></div>
          </div>
          <div class="ai-workspace-tabs">
            <button class="ai-workspace-tab active" data-ai-tab="chat" type="button">Chat</button>
            <button class="ai-workspace-tab owner-only" id="aiMultiTab" data-ai-tab="multi" type="button" hidden>Multi-Agent</button>
          </div>
          <div id="aiWorkspaceBody">
            <div id="aiChatMode">
              <div class="ai-workspace-shell">
                <article class="card panel ai-workspace-sidebar">
                  <div class="ai-workspace-toolbar"><select id="aiAgentSelect" aria-label="Select AI agent"><option>Loading agents…</option></select><button id="aiNewConversation" type="button">New chat</button></div>
                  <div id="aiConversationList" class="ai-conversation-list"><div class="empty-copy">Loading conversations…</div></div>
                </article>
                <article class="card panel ai-chat-panel">
                  <div class="ai-chat-head"><div><h2 id="aiChatTitle">New conversation</h2><p class="sub" id="aiChatAgent">Select an agent and start a chat.</p></div></div>
                  <div class="ai-chat-thread" id="aiChatThread"><div class="ai-workspace-empty">Open AI Workspace to load your conversations.</div></div>
                  <form class="ai-chat-form" id="aiChatForm" hidden>
                    <div class="ai-pending-attachments" id="aiPendingAttachments" hidden></div>
                    <div class="ai-attachment-actions">
                      <input id="aiPhotoInput" type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif" multiple hidden>
                      <input id="aiFileInput" type="file" accept="application/pdf,text/plain,text/csv,.xls,.xlsx,.docx" multiple hidden>
                      <button class="ai-attach-button" id="aiPhotoButton" type="button" aria-label="Attach photo">Photo</button>
                      <button class="ai-attach-button" id="aiFileButton" type="button" aria-label="Attach file">File</button>
                      <span class="ai-attachment-hint">Up to 4 attachments, 8 MB each</span>
                    </div>
                    <textarea id="aiMessageInput" maxlength="20000" placeholder="Message your selected MSA agent…" aria-label="AI Chat message"></textarea>
                    <button id="aiSend" type="submit">Send</button>
                  </form>
                  <p class="ai-runtime-note">Native internal-agent runtime. Bounded read-only MSA tools are available. Uploaded photos/files are persisted as evidence, but vision/OCR processing is not wired yet. Production writes remain disabled.</p>
                </article>
              </div>
            </div>
            <div id="aiMultiMode" hidden>
              <article class="card panel ai-multi-placeholder">
                <h2>Multi-Agent Workspace</h2><p class="sub">Owner-only native Review is loading.</p>
                <p>Review work persists through the shared Work Item, Artifact, Review, Event and Attention substrate. Production inventory writes remain disabled.</p>
              </article>
            </div>
          </div>
        </section>
'''


@app.get("/dashboard", include_in_schema=False)
def dashboard_shell_with_saved_model_assets() -> HTMLResponse:
    html = (ASSET_DIR / "dashboard.html").read_text(encoding="utf-8")
    html = html.replace(
        '<button class="nav-btn owner-only" data-view="agents" type="button" hidden>AI Agent Management</button>',
        '<button class="nav-btn owner-only" data-view="agents" type="button" hidden>AI Agent Management</button>\n        ' + AI_WORKSPACE_NAV,
        1,
    )
    html = html.replace(
        '<section class="view" data-panel="account">',
        AI_WORKSPACE_PANEL + '\n        <section class="view" data-panel="account">',
        1,
    )
    html = html.replace(
        "</head>",
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_saved_models.css?v={SAVED_MODEL_ASSET_VERSION}">\n'
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_agent_polish.css?v={AGENT_POLISH_ASSET_VERSION}">\n'
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_ai_workspace.css?v={AI_WORKSPACE_ASSET_VERSION}">\n'
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_multi_agent_review.css?v={MULTI_AGENT_REVIEW_ASSET_VERSION}">\n'
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_multi_agent_live_export.css?v={MULTI_AGENT_LIVE_EXPORT_ASSET_VERSION}">\n'
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_mcp_binding.css?v={MCP_BINDING_ASSET_VERSION}">\n'
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_audit.css?v={AUDIT_ASSET_VERSION}">\n'
        f'<link rel="stylesheet" href="/dashboard/assets/dashboard_inventory_views.css?v={INVENTORY_VIEW_ASSET_VERSION}">\n</head>',
        1,
    )
    html = html.replace(
        "</body>",
        f'<script src="/dashboard/assets/dashboard_saved_models.js?v={SAVED_MODEL_ASSET_VERSION}" defer></script>\n'
        f'<script src="/dashboard/assets/dashboard_agent_assignment_guard.js?v={AGENT_ASSIGNMENT_GUARD_ASSET_VERSION}" defer></script>\n'
        f'<script src="/dashboard/assets/dashboard_native_agent_test.js?v={NATIVE_AGENT_TEST_ASSET_VERSION}" defer></script>\n'
        f'<script src="/dashboard/assets/dashboard_ai_workspace_access.js?v={AI_WORKSPACE_ACCESS_ASSET_VERSION}" defer></script>\n'
        f'<script src="/dashboard/assets/dashboard_ai_workspace.js?v={AI_WORKSPACE_ASSET_VERSION}" defer></script>\n'
        f'<script src="/dashboard/assets/dashboard_multi_agent_review.js?v={MULTI_AGENT_REVIEW_ASSET_VERSION}" defer></script>\n'
        f'<script src="/dashboard/assets/dashboard_multi_agent_live_export.js?v={MULTI_AGENT_LIVE_EXPORT_ASSET_VERSION}" defer></script>\n'
        f'<script src="/dashboard/assets/dashboard_mcp_binding.js?v={MCP_BINDING_ASSET_VERSION}" defer></script>\n'
        f'<script src="/dashboard/assets/dashboard_audit.js?v={AUDIT_ASSET_VERSION}" defer></script>\n'
        f'<script src="/dashboard/assets/dashboard_inventory_views.js?v={INVENTORY_VIEW_ASSET_VERSION}" defer></script>\n</body>',
        1,
    )
    response = HTMLResponse(html)
    _dashboard_security_headers(response)
    return response


def _asset_file(name: str, media_type: str) -> FileResponse:
    response = FileResponse(ASSET_DIR / name, media_type=media_type)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/dashboard/assets/dashboard_saved_models.css", include_in_schema=False)
def saved_model_css() -> FileResponse:
    return _asset_file("dashboard_saved_models.css", "text/css")


@app.get("/dashboard/assets/dashboard_agent_polish.css", include_in_schema=False)
def agent_polish_css() -> FileResponse:
    return _asset_file("dashboard_agent_polish.css", "text/css")


@app.get("/dashboard/assets/dashboard_ai_workspace.css", include_in_schema=False)
def ai_workspace_css() -> FileResponse:
    return _asset_file("dashboard_ai_workspace.css", "text/css")


@app.get("/dashboard/assets/dashboard_multi_agent_review.css", include_in_schema=False)
def multi_agent_review_css() -> FileResponse:
    return _asset_file("dashboard_multi_agent_review.css", "text/css")


@app.get("/dashboard/assets/dashboard_multi_agent_live_export.css", include_in_schema=False)
def multi_agent_live_export_css() -> FileResponse:
    return _asset_file("dashboard_multi_agent_live_export.css", "text/css")


@app.get("/dashboard/assets/dashboard_mcp_binding.css", include_in_schema=False)
def mcp_binding_css() -> FileResponse:
    return _asset_file("dashboard_mcp_binding.css", "text/css")


@app.get("/dashboard/assets/dashboard_audit.css", include_in_schema=False)
def audit_css() -> FileResponse:
    return _asset_file("dashboard_audit.css", "text/css")


@app.get("/dashboard/assets/dashboard_inventory_views.css", include_in_schema=False)
def inventory_view_css() -> FileResponse:
    return _asset_file("dashboard_inventory_views.css", "text/css")


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


@app.get("/dashboard/assets/dashboard_agent_assignment_guard.js", include_in_schema=False)
def agent_assignment_guard_js() -> FileResponse:
    return _asset_file("dashboard_agent_assignment_guard.js", "text/javascript")


@app.get("/dashboard/assets/dashboard_native_agent_test.js", include_in_schema=False)
def native_agent_test_js() -> FileResponse:
    return _asset_file("dashboard_native_agent_test.js", "text/javascript")


@app.get("/dashboard/assets/dashboard_ai_workspace_access.js", include_in_schema=False)
def ai_workspace_access_js() -> FileResponse:
    return _asset_file("dashboard_ai_workspace_access.js", "text/javascript")


@app.get("/dashboard/assets/dashboard_ai_workspace.js", include_in_schema=False)
def ai_workspace_js() -> FileResponse:
    return _asset_file("dashboard_ai_workspace.js", "text/javascript")


@app.get("/dashboard/assets/dashboard_multi_agent_review.js", include_in_schema=False)
def multi_agent_review_js() -> FileResponse:
    return _asset_file("dashboard_multi_agent_review.js", "text/javascript")


@app.get("/dashboard/assets/dashboard_multi_agent_live_export.js", include_in_schema=False)
def multi_agent_live_export_js() -> FileResponse:
    return _asset_file("dashboard_multi_agent_live_export.js", "text/javascript")


@app.get("/dashboard/assets/dashboard_mcp_binding.js", include_in_schema=False)
def mcp_binding_js() -> FileResponse:
    return _asset_file("dashboard_mcp_binding.js", "text/javascript")


@app.get("/dashboard/assets/dashboard_audit.js", include_in_schema=False)
def audit_js() -> FileResponse:
    return _asset_file("dashboard_audit.js", "text/javascript")


@app.get("/dashboard/assets/dashboard_inventory_views.js", include_in_schema=False)
def inventory_view_js() -> FileResponse:
    return _asset_file("dashboard_inventory_views.js", "text/javascript")


app.include_router(dashboard_login_router)
app.include_router(dashboard_router)
app.include_router(inventory_view_router)
app.include_router(email_recovery_page_router)
app.include_router(user_management_router)
app.include_router(agent_management_router)
app.include_router(agent_model_assignments_router)
app.include_router(native_agent_runtime_router)
app.include_router(ai_workspace_access_router)
app.include_router(ai_workspace_attachments_router)
app.include_router(ai_workspace_chat_router)
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
        "mcp_broad_typed_reads": "f7.3b",
        "agent_management": "f7.2d2",
        "provider_registry": "f7.2d3",
        "saved_model_catalog": "f7.2d3.1",
        "internal_agent_assignment_chain": "f7.2d4b",
        "native_internal_agent_inference": "f7.2d4c",
        "native_internal_agent_test_ui": "f7.2d4d",
        "ai_workspace_access_policy": "f7.2d4-access",
        "ai_workspace_chat": "f7.2d47b-attachments",
        "native_internal_agent_tools": "f7.2d47b-human-presentation",
        "ai_workspace_attachments": "metadata-and-evidence-persistence-no-model-processing",
        "multi_agent_review": "f7.2d48-review-provenance-delete",
        "nanogpt_detailed_catalog": "enabled",
        "production_inventory_writes": False,
    }


@app.get("/ready", tags=["system"], summary="Database readiness")
def ready(response: Response) -> dict[str, object]:
    readiness = database_readiness()
    if not readiness["ok"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {**readiness, "service": SERVICE_NAME, "database_canonical": False}


app.mount("/", mcp_http_app)