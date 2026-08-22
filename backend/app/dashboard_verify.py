from __future__ import annotations

import app.dashboard_auth as dashboard_auth


def main() -> None:
    original_hash = dashboard_auth.PASSWORD_HASH
    original_secret = dashboard_auth.SESSION_SECRET
    try:
        password = "f7-verification-password"
        dashboard_auth.PASSWORD_HASH = dashboard_auth.make_password_hash(password, salt=b"0123456789abcdef")
        dashboard_auth.SESSION_SECRET = "f7-verification-session-secret-with-sufficient-entropy"

        assert dashboard_auth.dashboard_auth_configured()
        assert dashboard_auth.verify_password(password)
        assert not dashboard_auth.verify_password("wrong-password")

        token = dashboard_auth.create_session_token()
        assert dashboard_auth.validate_session_token(token)
        assert not dashboard_auth.validate_session_token(token + "tampered")

        print("F7 dashboard auth foundation verification PASS")
        print("password_hash=pass session_signature=pass tamper_guard=pass")
    finally:
        dashboard_auth.PASSWORD_HASH = original_hash
        dashboard_auth.SESSION_SECRET = original_secret


if __name__ == "__main__":
    main()
