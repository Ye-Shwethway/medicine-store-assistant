from __future__ import annotations


def provider_failure_detail(status_code: int | None) -> str:
    if status_code is None:
        return "email provider delivery failed"
    return f"email provider delivery failed with HTTP {status_code}"
