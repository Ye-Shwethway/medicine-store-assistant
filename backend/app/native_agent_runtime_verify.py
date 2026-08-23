from __future__ import annotations

from pathlib import Path

from app.main import app
from app.native_agent_runtime import _extract_gemini_text, _extract_openai_text, _identity_prompt


def main() -> None:
    paths = set(app.openapi()["paths"])
    required = {"/dashboard/api/agents/{agent_id}/invoke"}
    missing = required - paths
    if missing:
        raise SystemExit(f"missing native invocation path: {sorted(missing)}")

    source = Path(__file__).with_name("native_agent_runtime.py").read_text(encoding="utf-8")
    required_fragments = (
        'runtime_mode"] != "INTERNAL_MODEL"',
        'transport": "NATIVE_MSA_BACKEND"',
        '"mcp_used": False',
        '"tool_execution_enabled": False',
        "assignment_kind WHEN 'PRIMARY' THEN 0 ELSE 1 END",
        '"fallback_used": chain_index > 0',
        '"NATIVE_AGENT_CHAIN_EXHAUSTED"',
        "read_provider_secret",
        "systemInstruction",
        '"/chat/completions"',
    )
    for fragment in required_fragments:
        if fragment not in source:
            raise SystemExit(f"native runtime contract fragment missing: {fragment}")

    openai_text = _extract_openai_text({"choices": [{"message": {"content": "  OK openai  "}}]})
    if openai_text != "OK openai":
        raise SystemExit("OpenAI-compatible response normalization failed")

    gemini_text = _extract_gemini_text({"candidates": [{"content": {"parts": [{"text": "OK "}, {"text": "gemini"}]}}]})
    if gemini_text != "OK gemini":
        raise SystemExit("Gemini response normalization failed")

    prompt = _identity_prompt(
        {
            "display_name": "Verifier",
            "agent_id": "00000000-0000-0000-0000-000000000001",
            "call_name": "Verifier",
            "description": "Independent test agent",
            "authority_ceiling": "READ",
            "execution_policy": "DELEGATED",
            "confirmation_policy": "READ_ONLY",
        }
    )
    if "independently of ChatGPT" not in prompt or "no MSA typed tools attached yet" not in prompt:
        raise SystemExit("native identity/boundary prompt is incomplete")

    print("native_internal_agent_runtime=pass")


if __name__ == "__main__":
    main()
