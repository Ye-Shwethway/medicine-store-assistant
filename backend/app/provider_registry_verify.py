from __future__ import annotations

from fastapi import HTTPException, Response
from sqlalchemy import text

from app.dashboard_auth import _engine, ensure_bootstrap_owner
from app.provider_registry import (
    ProviderCreate,
    ProviderCredential,
    _normalize_gemini_model,
    _normalize_openai_model,
    _set_provider_state,
    create_provider,
    list_providers,
    provision_credential,
    remove_credential,
)
from app.provider_secrets import read_provider_secret


def main() -> None:
    owner = ensure_bootstrap_owner()
    response = Response()
    created = create_provider(
        ProviderCreate(display_name="F7.2D3 Runtime Verifier", provider_kind="OPENAI"),
        response,
        owner,
    )
    provider_id = created["provider_id"]
    engine = _engine()
    credential_ref: str | None = None
    try:
        assert created["credential_configured"] is False
        assert created["state"] == "DISABLED"

        provisioned = provision_credential(
            provider_id,
            ProviderCredential(api_key="msa-provider-runtime-verifier-not-a-real-key"),
            Response(),
            owner,
        )
        assert provisioned["credential_configured"] is True
        with engine.connect() as connection:
            row = connection.execute(
                text("SELECT credential_ref FROM ai_providers WHERE provider_id=CAST(:provider_id AS uuid)"),
                {"provider_id": provider_id},
            ).mappings().one()
            credential_ref = row["credential_ref"]
        assert credential_ref
        assert credential_ref != "msa-provider-runtime-verifier-not-a-real-key"
        assert read_provider_secret(credential_ref) == "msa-provider-runtime-verifier-not-a-real-key"

        listed = list_providers(Response())
        item = next(x for x in listed["items"] if x["provider_id"] == provider_id)
        assert item["credential_configured"] is True
        assert "credential_ref" not in item
        assert "api_key" not in item

        try:
            _set_provider_state(provider_id, "ENABLED")
        except HTTPException as exc:
            assert exc.status_code == 409
        else:
            raise AssertionError("provider enabled before test/fetch gate")

        removed = remove_credential(provider_id, Response(), owner)
        assert removed["credential_configured"] is False
        if credential_ref:
            assert read_provider_secret(credential_ref) is None

        openai = _normalize_openai_model({
            "id": "vendor/model-a",
            "name": "Model A",
            "context_length": 128000,
            "architecture": {"input_modalities": ["text", "image"]},
            "supported_parameters": ["tools", "response_format"],
        })
        assert openai and openai["model_id"] == "vendor/model-a"
        assert openai["supports_text"] is True
        assert openai["supports_vision"] is True
        assert openai["supports_tools"] is True
        assert openai["supports_structured_output"] is True

        gemini = _normalize_gemini_model({
            "name": "models/gemini-verifier",
            "displayName": "Gemini Verifier",
            "inputTokenLimit": 1000000,
            "outputTokenLimit": 65536,
            "supportedGenerationMethods": ["generateContent", "countTokens"],
        })
        assert gemini and gemini["model_id"] == "gemini-verifier"
        assert gemini["supports_text"] is True
        assert gemini["context_window"] == 1000000

        print(
            "F7.2D3 provider_registry_runtime=pass credential_write_only=pass "
            "db_plaintext_secret=absent enable_gate=pass model_normalization=pass"
        )
    finally:
        try:
            with engine.begin() as connection:
                connection.execute(
                    text("DELETE FROM ai_providers WHERE provider_id=CAST(:provider_id AS uuid)"),
                    {"provider_id": provider_id},
                )
        finally:
            engine.dispose()


if __name__ == "__main__":
    main()
