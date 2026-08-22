from __future__ import annotations

import os

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import RedirectResponse

from app.credential_lifecycle import router as credential_lifecycle_router
from app.dashboard import router as dashboard_router
from app.dashboard_auth import SESSION_COOKIE, validate_session_token
from app.dashboard_login import router as dashboard_login_router
from app.db import database_readiness
from app.email_recovery import router as email_recovery_router
from app.read_api import router as read_router
from app.shadow_read_api import router as shadow_read_router
from app.user_management import router as user_management_router

SERVICE_NAME = "medicine-store-assistant-api"
SERVICE_VERSION = os.getenv("MSA_SERVICE_VERSION", "0.1.0-dev")
ENVIRONMENT = os.getenv("MSA_ENVIRONMENT", "development")
BUILD_SHA = os.getenv("MSA_BUILD_SHA", "unknown")

app = FastAPI(
    title="Medicine Store Assistant Inventory API",
    version=SERVICE_VERSION,
    description=(
        "Typed API boundary for the Medicine Store Assistant backend. "
        "Authenticated inventory, canonical human identity/User Management/credential and email-recovery lifecycle, catalogue, "
        "test-only shadow reads, and the F7 read-only dashboard are available; canonical inventory writes remain disabled."
    ),
)


@app.middleware("http")
async def dashboard_login_gate(request: Request, call_next):
    path = request.url.path.rstrip("/") or "/"
    token = request.cookies.get(SESSION_COOKIE)
    authenticated = validate_session_token(token)

    if path == "/dashboard" and not authenticated:
        return RedirectResponse(url="/dashboard/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    if path == "/dashboard/login" and authenticated:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    return await call_next(request)


app.include_router(dashboard_login_router)
app.include_router(dashboard_router)
app.include_router(user_management_router)
app.include_router(credential_lifecycle_router)
app.include_router(email_recovery_router)
app.include_router(read_router)
app.include_router(shadow_read_router)


@app.get("/health", tags=["system"], summary="Service health")
def health() -> dict[str, object]:
    return {
        "ok": True,
        "service": SERVICE_NAME,
        "environment": ENVIRONMENT,
        "version": SERVICE_VERSION,
        "build_sha": BUILD_SHA,
        "database_canonical": False,
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
