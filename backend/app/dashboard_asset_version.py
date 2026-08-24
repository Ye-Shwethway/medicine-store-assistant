from __future__ import annotations

from hashlib import sha256
from pathlib import Path


def asset_bundle_version(asset_dir: Path, *names: str) -> str:
    """Return a stable short hash derived from the exact files served to browsers."""
    digest = sha256()
    for name in names:
        path = asset_dir / name
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()[:12]
