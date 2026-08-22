from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["dashboard"])
ASSET_DIR = Path(__file__).resolve().parent / "dashboard_assets"


@router.get("/dashboard/login", include_in_schema=False)
def dashboard_login_page() -> FileResponse:
    response = FileResponse(ASSET_DIR / "login.html", media_type="text/html")
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@router.get("/dashboard/login.css", include_in_schema=False)
def dashboard_login_css() -> FileResponse:
    response = FileResponse(ASSET_DIR / "login.css", media_type="text/css")
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@router.get("/dashboard/login.js", include_in_schema=False)
def dashboard_login_js() -> FileResponse:
    response = FileResponse(ASSET_DIR / "login.js", media_type="text/javascript")
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
