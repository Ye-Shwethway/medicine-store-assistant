from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Response
from fastapi.responses import FileResponse

from app.dashboard_auth import require_dashboard_session

router = APIRouter(tags=["dashboard"])
ASSET_DIR = Path(__file__).resolve().parent / "dashboard_assets"


def _secure(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"


@router.get("/dashboard/recovery-email", include_in_schema=False, dependencies=[Depends(require_dashboard_session)])
def recovery_email_page() -> FileResponse:
    response = FileResponse(ASSET_DIR / "recovery_email.html", media_type="text/html")
    _secure(response)
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    return response


@router.get("/dashboard/recovery-email.css", include_in_schema=False)
def recovery_email_css() -> FileResponse:
    response = FileResponse(ASSET_DIR / "recovery_email.css", media_type="text/css")
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@router.get("/dashboard/recovery-email.js", include_in_schema=False)
def recovery_email_js() -> FileResponse:
    response = FileResponse(ASSET_DIR / "recovery_email.js", media_type="text/javascript")
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
