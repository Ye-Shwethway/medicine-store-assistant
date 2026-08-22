from __future__ import annotations

import os

from fastapi import FastAPI, Response, status

from app.db import database_readiness
from app.read_api import router as read_router

SERVICE_NAME = "medicine-store-assistant-api"
SERVICE_VERSION = os.getenv("MSA_SERVICE_VERSION", "0.1.0-dev")
ENVIRONMENT = os.getenv("MSA_ENVIRONMENT", "development")
BUILD_SHA = os.getenv("MSA_BUILD_SHA", "unknown")

app = FastAPI(
    title="Medicine Store Assistant Inventory API",
    version=SERVICE_VERSION,
    description=(
        "Typed API boundary for the Medicine Store Assistant backend. "
        "Authenticated inventory and catalogue reads are available; canonical inventory writes remain disabled."
    ),
)

app.include_router(read_router)


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
