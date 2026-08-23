# F7.2D4B — Internal Agent Assignment/Fallback Contract

Status: VERIFIED
Date: 2026-08-23

This checkpoint records the bounded D4.1 slice that turns the existing single PRIMARY model binding into an explicit ordered native-agent assignment chain.

Canonical rules:

- applies only to `INTERNAL_MODEL` agents;
- one PRIMARY model is required for an executable chain;
- zero or more FALLBACK models may follow in deterministic order;
- duplicate saved-model IDs are rejected across the chain;
- each assigned saved model must be ACTIVE, HEALTHY, currently discovered, and owned by an ENABLED provider;
- revoked agents cannot receive assignments;
- chain replacement is atomic;
- existing singular `/model-assignment` endpoints remain compatibility helpers over the same `ai_agent_model_assignments` table;
- assignment state does not grant inventory authority;
- production inventory writes remain closed.

Implemented API contract:

- `GET /dashboard/api/agents/{agent_id}/model-assignments`
- `PUT /dashboard/api/agents/{agent_id}/model-assignments`
- `DELETE /dashboard/api/agents/{agent_id}/model-assignments`

Verification evidence:

- dedicated `Validate internal agent model assignments` workflow passed on PR #84 and again on subsequent native-runtime PRs;
- generic backend validation also passed;
- the assignment API is wired through the production backend and uses the existing `ai_agent_model_assignments` PRIMARY/FALLBACK schema;
- production deployment subsequently advanced through native-runtime releases without regression.

The ordered chain exposes provider/model health metadata so native invocation can select deterministically without consulting MCP.
