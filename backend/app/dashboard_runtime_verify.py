from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from app.dashboard_auth import SESSION_COOKIE, create_session_token


def _get_json(base_url: str, path: str, cookie: str) -> dict:
    request = urllib.request.Request(
        f"{base_url}{path}",
        headers={"Cookie": f"{SESSION_COOKIE}={cookie}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"dashboard runtime read failed: {path} -> HTTP {exc.code}: {body[:240]}") from exc


def main() -> None:
    base_url = os.environ.get("MSA_DASHBOARD_VERIFY_BASE_URL")
    if not base_url:
        port = os.environ.get("MSA_API_HOST_PORT", "8088")
        base_url = f"http://127.0.0.1:{port}"
    base_url = base_url.rstrip("/")

    cookie = create_session_token()

    overview = _get_json(base_url, "/dashboard/api/overview", cookie)
    batch = overview.get("batch")
    if not batch:
        raise SystemExit("dashboard runtime verification failed: overview has no test-only batch")
    if int(batch.get("row_count") or 0) <= 0:
        raise SystemExit("dashboard runtime verification failed: overview row_count is zero")
    if overview.get("database_canonical") is not False or overview.get("migration_baseline_accepted") is not False:
        raise SystemExit("dashboard runtime verification failed: authority flags changed")

    rows = _get_json(base_url, "/dashboard/api/rows?limit=5&offset=0", cookie)
    if int(rows.get("count") or 0) <= 0 or not rows.get("items"):
        raise SystemExit("dashboard runtime verification failed: authenticated rows endpoint returned no rows")
    if rows.get("database_canonical") is not False or rows.get("migration_baseline_accepted") is not False:
        raise SystemExit("dashboard runtime verification failed: row authority flags changed")

    reasons = _get_json(base_url, "/dashboard/api/review-reasons", cookie)
    if reasons.get("database_canonical") is not False or reasons.get("migration_baseline_accepted") is not False:
        raise SystemExit("dashboard runtime verification failed: review authority flags changed")

    print(
        "dashboard_authenticated_runtime=pass "
        f"row_count={int(batch.get('row_count') or 0)} "
        f"sample_rows={int(rows.get('count') or 0)} "
        f"review_reason_groups={int(reasons.get('count') or 0)} "
        "database_canonical=false migration_baseline_accepted=false"
    )


if __name__ == "__main__":
    main()
