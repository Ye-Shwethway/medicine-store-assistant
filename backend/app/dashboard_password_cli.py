from __future__ import annotations

import getpass

from app.dashboard_auth import make_password_hash


def main() -> None:
    password = getpass.getpass("Dashboard owner password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        raise SystemExit("Passwords do not match")
    print(make_password_hash(password))


if __name__ == "__main__":
    main()
