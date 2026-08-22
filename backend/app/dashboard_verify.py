from __future__ import annotations

from app.dashboard_auth import make_password_hash, password_hash_shape_valid, require_roles, verify_password_hash


def main() -> None:
    password = "f7-2a-verification-password"
    password_hash = make_password_hash(password, salt=b"0123456789abcdef")

    assert password_hash_shape_valid(password_hash)
    assert verify_password_hash(password, password_hash)
    assert not verify_password_hash("wrong-password", password_hash)
    assert callable(require_roles("OWNER"))
    assert callable(require_roles("ADMIN", "STAFF", "READ_ONLY"))

    try:
        require_roles("SUPERUSER")
    except ValueError:
        pass
    else:
        raise AssertionError("non-canonical role unexpectedly accepted")

    print("F7.2A auth primitive verification PASS")
    print("password_hash=pass role_policy_factory=pass canonical_roles=pass")


if __name__ == "__main__":
    main()
