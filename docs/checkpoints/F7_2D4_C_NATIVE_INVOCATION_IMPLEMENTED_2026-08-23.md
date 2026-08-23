# F7.2D4C — Native Internal-Agent Invocation

Status: CI VERIFIED + PRODUCTION DEPLOYED; LIVE AGENT ACCEPTANCE PENDING
Date: 2026-08-23

## Purpose

Provide the first real `INTERNAL_MODEL` execution path that is owned by the MSA backend and does not depend on ChatGPT or the public MCP transport.

Canonical path:

`MSA authenticated Web/API caller -> native agent runtime -> ordered saved-model chain -> provider API -> normalized response`

## Implemented boundary

- Owner-authenticated `POST /dashboard/api/agents/{agent_id}/invoke`;
- only ACTIVE `INTERNAL_MODEL` agents may run;
- server loads PRIMARY then ordered FALLBACK assignments from PostgreSQL;
- disabled/unhealthy/stale/not-discovered assignments are skipped with provenance;
- provider credentials remain server-side and are resolved only through opaque credential references;
- OpenAI-compatible providers use `/chat/completions`;
- Gemini uses `generateContent`;
- identity, role and current policy are injected by the server, not trusted to caller text;
- provider/model/latency/fallback-attempt provenance is returned;
- response is explicitly marked `transport=NATIVE_MSA_BACKEND`, `mcp_used=false`;
- native typed MSA tools are still disabled in this slice and the system prompt forbids claiming store/database execution;
- production inventory writes remain closed.

## Verification evidence

- PR #85 merged as `4c9614b98c0ab99cdb3c9c8a068afed256f22190`;
- dedicated `Validate native internal agent runtime` CI passed;
- backend, saved-model, assignment, MCP binding/audit and broad-read regression workflows also passed;
- production deploy run `32644544986` completed successfully for the native runtime;
- PR #86 added a Dashboard `Test native runtime` acceptance surface and merged as `187971fe2bfd29cf41b6cc3d7dffc0f6299e6e8f`;
- production deploy run `32644738010` completed successfully for the acceptance UI.

## Dashboard acceptance surface

Active `INTERNAL_MODEL` agent cards now expose **Test native runtime**. The modal invokes the MSA native backend directly and shows:

- configured-agent response;
- selected provider/model;
- fallback used or not;
- latency;
- attempt provenance;
- `MCP used: no`;
- typed tools status.

This is deliberately not the final chat interface.

## Not yet included

- durable conversations/messages;
- Web AI Chat UI;
- native typed-tool adapter;
- operation-ledger persistence for native inference;
- multi-agent session execution;
- MCP -> native-agent delegation.

These remain subsequent F7.2D4 slices.

## Remaining live acceptance

Use a configured internal agent with a healthy saved PRIMARY model and run the Dashboard native-runtime test. Pass requires a real provider response through the MSA backend, stable configured agent identity, provider/model provenance, `mcp_used=false`, and `tool_execution_enabled=false` for this slice.

A later fallback acceptance must deliberately make the primary unavailable while leaving a healthy fallback configured, then verify deterministic fallback selection.
