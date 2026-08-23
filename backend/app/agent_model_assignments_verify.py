from __future__ import annotations

from pathlib import Path

from app.main import app


def main() -> None:
    paths = set(app.openapi()["paths"])
    required = {
        "/dashboard/api/agents/{agent_id}/model-assignments",
        "/dashboard/api/agents/{agent_id}/model-assignment",
    }
    missing = required - paths
    if missing:
        raise SystemExit(f"missing assignment API paths: {sorted(missing)}")

    source = Path(__file__).with_name("agent_model_assignments.py").read_text(encoding="utf-8")
    required_fragments = (
        "MAX_FALLBACK_MODELS = 5",
        "assignment_kind WHEN 'PRIMARY' THEN 0 ELSE 1 END",
        "'FALLBACK'",
        "currently_discovered",
        "Only internal model agents can receive provider/model assignments",
        "duplicate saved models",
        "DELETE FROM ai_agent_model_assignments",
    )
    for fragment in required_fragments:
        if fragment not in source:
            raise SystemExit(f"assignment contract fragment missing: {fragment}")

    print("agent_model_assignment_chain=pass")


if __name__ == "__main__":
    main()
