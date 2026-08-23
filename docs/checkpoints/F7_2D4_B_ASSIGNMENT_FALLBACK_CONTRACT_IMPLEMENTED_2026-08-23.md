# F7.2D4B — Internal Agent Assignment/Fallback Contract

Status: IMPLEMENTATION IN PROGRESS
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
- production inventory writes remain closed;
- this slice does not yet invoke provider inference. Native invocation is the next slice.

Expected API contract:

- `GET /dashboard/api/agents/{agent_id}/model-assignments`
- `PUT /dashboard/api/agents/{agent_id}/model-assignments`
- `DELETE /dashboard/api/agents/{agent_id}/model-assignments`

The response exposes the ordered chain and enough provider/model health metadata for the next native invocation runtime to select deterministically without consulting MCP.
