# F7.2D4C — Native Internal-Agent Invocation

Status: IMPLEMENTED CANDIDATE; CI + PRODUCTION ACCEPTANCE PENDING
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

## Not yet included

- durable conversations/messages;
- Web AI Chat UI;
- native typed-tool adapter;
- operation-ledger persistence for native inference;
- multi-agent session execution;
- MCP -> native-agent delegation.

These remain subsequent F7.2D4 slices.

## Acceptance target

A configured internal agent with a healthy saved PRIMARY model must answer a bounded prompt through the MSA backend without any MCP/ChatGPT dependency. The response must preserve the configured agent identity and disclose selected provider/model provenance. A deliberately unavailable primary with a valid fallback must select the fallback deterministically.
