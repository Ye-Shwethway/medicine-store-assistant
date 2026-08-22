from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    client = TestClient(app)

    login = client.get("/dashboard/login", follow_redirects=False)
    if login.status_code != 200:
        raise SystemExit(f"dedicated login route failed: {login.status_code}")
    if "Secure dashboard access" not in login.text or ">Username<" not in login.text or ">Password<" not in login.text:
        raise SystemExit("dedicated canonical login page content missing")

    dashboard = client.get("/dashboard", follow_redirects=False)
    if dashboard.status_code != 307 or dashboard.headers.get("location") != "/dashboard/login":
        raise SystemExit(
            f"unauthenticated dashboard gate failed: status={dashboard.status_code} location={dashboard.headers.get('location')}"
        )

    print("F7.2A dedicated username/password login verification PASS")


if __name__ == "__main__":
    main()
