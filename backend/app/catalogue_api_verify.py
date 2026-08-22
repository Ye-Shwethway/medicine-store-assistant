from __future__ import annotations

from app.main import app

REQUIRED_GET_PATHS = {
    "/v1/catalogue/versions",
    "/v1/catalogue/current",
    "/v1/catalogue/items",
    "/v1/catalogue/diff",
}


def main() -> None:
    schema = app.openapi()
    paths = schema.get("paths", {})

    missing = sorted(path for path in REQUIRED_GET_PATHS if path not in paths or "get" not in paths[path])
    if missing:
        raise AssertionError(f"missing catalogue read endpoints: {missing}")

    forbidden_methods: list[str] = []
    for path in REQUIRED_GET_PATHS:
        for method in ("post", "put", "patch", "delete"):
            if method in paths[path]:
                forbidden_methods.append(f"{method.upper()} {path}")
    if forbidden_methods:
        raise AssertionError(f"unexpected catalogue write surface: {forbidden_methods}")

    print("F5.1 authenticated catalogue read surface verification PASS")
    print("versions_read=pass current_read=pass items_read=pass diff_read=pass no_catalogue_write_surface=pass")


if __name__ == "__main__":
    main()
