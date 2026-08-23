from __future__ import annotations

import os
import re
import secrets
from pathlib import Path

SECRET_DIR = Path(os.getenv("MSA_PROVIDER_SECRET_DIR", "/var/lib/msa/provider-secrets"))
REF_RE = re.compile(r"^provider-[A-Za-z0-9_-]{32,120}\.key$")


def _ensure_dir() -> None:
    SECRET_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        SECRET_DIR.chmod(0o700)
    except OSError:
        pass


def store_provider_secret(value: str) -> str:
    secret = value.strip()
    if len(secret) < 8 or len(secret) > 8192:
        raise ValueError("provider credential has an invalid length")
    _ensure_dir()
    ref = f"provider-{secrets.token_urlsafe(32)}.key"
    path = SECRET_DIR / ref
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(secret)
            handle.write("\n")
    except Exception:
        try:
            path.unlink(missing_ok=True)
        finally:
            raise
    return ref


def read_provider_secret(ref: str | None) -> str | None:
    if not ref or not REF_RE.fullmatch(ref):
        return None
    _ensure_dir()
    path = SECRET_DIR / ref
    try:
        value = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None
    return value or None


def delete_provider_secret(ref: str | None) -> None:
    if not ref or not REF_RE.fullmatch(ref):
        return
    try:
        (SECRET_DIR / ref).unlink(missing_ok=True)
    except OSError:
        pass
