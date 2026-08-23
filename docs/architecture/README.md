# Medicine Store Assistant — Architecture Index

Status: **F7.2A/B/C, F7.2D0 custom MCP connectivity, F7.2D2 named Agent Management/multi-agent sessions, and F7.2D3 Provider Registry/model catalog are verified; F7.2D4 internal model assignment/fallback/runtime identity is next; PostgreSQL remains non-canonical**

This directory defines the canonical architecture for Medicine Store Assistant beyond the current spreadsheet-operating skill.

The Git-backed `$msa` skill remains canonical at `skills/medicine-store-assistant/`.

## Core decision

MSA evolves toward a ledger-backed multi-client inventory system in which PostgreSQL is planned future canonical operational storage but is **not canonical yet**; Google Sheets remains operationally authoritative until explicit promotion; all clients use typed application contracts; humans, AI agents, external clients, provider connections, models, and assignments remain separate concepts; deterministic backend code owns authorization/validation/idempotency/transactions/read-back; AI may later act only through Owner-authorized typed capabilities; actor-aware Audit remains a later independent control-plane slice.

## Verified MCP-first external access

F7.2D0 is verified complete.

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> typed MSA backend -> deterministic reads`

Verified scopes: `mcp:connect`, `mcp:read`, `offline_access`. Propose/write/control remain disabled. Custom GPT Actions are optional/fallback only. The MCP surface is full-schema/policy-gated: discoverability does not confer execution permission.

## F7.2D2 — verified Agent Management foundation

Runtime anchor: PR #58; merge `3b385a37b95c1ff79f76883381d8268fa6c49db2`; deploy run `32620386876` / job `97147568336`; migration `0010_mcp_oauth -> 0011_ai_agents`.

Verified model:

- durable named AI agents with immutable `agent_id`;
- editable `display_name` + unique `call_name`;
- server-owned canonical self-identity context;
- lifecycle/capability/location/authority/execution/confirmation policy;
- Owner-only management;
- persistent `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` multi-agent topology with ordered participants/role labels.

Detailed design: `F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`.

## F7.2D3 — verified Provider Registry/model catalog

Runtime anchor: PR #60; merge `882c67b0134edb59156c17e948128de0ca8c3365`; deploy run `32621925138` / job `97151213410`; migration `0011_ai_agents -> 0012_providers`; issue #26 `status=success`.

Verified Provider Registry:

- Owner-only OpenAI / Google Gemini / OpenRouter / NanoGPT / generic `OPENAI_COMPATIBLE` connections;
- provider secret material stored in dedicated server-side `msa_provider_secrets` volume;
- PostgreSQL stores opaque `credential_ref`, never plaintext provider keys;
- saved provider credentials are write-only and never read back to the browser;
- server-side Test connection and Fetch models operations;
- normalized persisted model catalog with bounded provider metadata and explicit unknown capability states;
- provider enable gate requires credential + healthy test + successful model fetch;
- provider health/model catalog/agent health remain separate;
- custom-provider SSRF protections require public HTTPS, reject private/loopback/link-local/reserved destinations, block redirects, and bound responses;
- deployment verification does not call a real provider API and performs no inventory mutation/workbook import.

Agent Management presentation now separates `External / MCP agents` from `Internal / provider-backed agents` and exposes Agent name / Origin / Model fields. Internal agents remain `Not assigned` until F7.2D4.

Verified checkpoint: `../checkpoints/F7_2D3_PROVIDER_REGISTRY_VERIFIED_2026-08-23.md`.

## Canonical separation

- **Human user** — canonical person/account + human role.
- **AI agent** — named identity + capability/location/execution policy.
- **External client** — transport/runtime such as custom MCP.
- **Provider connection** — outbound model API configuration + protected secret reference.
- **Model** — provider-local model resource/capability metadata.
- **Assignment** — selected provider/model/fallback policy for an internal agent.
- **Multi-agent session** — reusable topology of selected named agents.

Changing provider/model never changes agent identity or authority.

## F7.2D4 — next architecture slice

Internal model assignment/fallback/runtime identity is next:

- assign primary enabled provider/model to an `INTERNAL_MODEL` agent;
- optional ordered fallbacks;
- validate known capability compatibility and explicitly preserve unknown capability states;
- timeout/output and optional usage/cost policy;
- inject current canonical agent identity into every internal model invocation;
- preserve agent ID/call name/authority independently from model assignment;
- prove a narrow real inference only after Owner configures provider credentials through Web UI;
- prepare existing multi-agent session topology for later cross-model comparison/review/debate.

The existing custom MCP client is an external runtime. Do not auto-invent its named AI-agent identity; any binding should be explicit and Owner-controlled.

## Immediate F7.2D order

1. **F7.2D0 — custom MCP full-schema/OAuth connectivity — VERIFIED COMPLETE**
2. **F7.2D2 — named Agent Management + multi-agent sessions — VERIFIED COMPLETE**
3. **F7.2D3 — Provider Registry + model catalog — VERIFIED COMPLETE**
4. **F7.2D4 — internal model assignment/fallback/runtime identity — NEXT**
5. optional **F7.2D1 — Custom GPT Action proof** only for a concrete standalone-GPT need
6. **F7.3 — actor-aware operational Audit**

No production inventory write becomes authorized merely because provider/model capability metadata or write-capable MCP tools exist.

## Web design/implementation rule

Default Web workflow:

`UI/UX Pro Max -> repo design system -> authenticated API contract -> direct implementation -> responsive/accessibility/runtime verification`

Figma is optional and used only when explicitly requested by the Owner or genuinely required by a specific task.

Canonical UI sources:

- `../design/UI_UX_PRO_MAX_INTEGRATION.md`
- `../../design-system/medicine-store-assistant/MASTER.md`
- `../../design-system/medicine-store-assistant/pages/dashboard.md`

## Key documents

- [CANONICAL_INVENTORY_ARCHITECTURE.md](CANONICAL_INVENTORY_ARCHITECTURE.md)
- [INVENTORY_DATA_MODEL.md](INVENTORY_DATA_MODEL.md)
- [INVENTORY_INTEGRITY_AND_AUDIT.md](INVENTORY_INTEGRITY_AND_AUDIT.md)
- [API_AND_CLIENT_ARCHITECTURE.md](API_AND_CLIENT_ARCHITECTURE.md)
- [MIGRATION_AND_SHADOW_VALIDATION.md](MIGRATION_AND_SHADOW_VALIDATION.md)
- [F7_WEB_DASHBOARD.md](F7_WEB_DASHBOARD.md)
- [F7_2D_AI_AGENT_MANAGEMENT.md](F7_2D_AI_AGENT_MANAGEMENT.md)
- [F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md](F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md)
- [F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md](F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md)
- [F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md](F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md)
- [F7_2D1_CUSTOM_GPT_ACTION_PROOF.md](F7_2D1_CUSTOM_GPT_ACTION_PROOF.md)
- [F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md](F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md)
- `../checkpoints/F7_2D0_MCP_CONNECTIVITY_VERIFIED_2026-08-23.md`
- `../checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`
- `../checkpoints/F7_2D3_PROVIDER_REGISTRY_VERIFIED_2026-08-23.md`

## Design rule

Do not implement from one document in isolation. `AGENTS.md`, `NEW_CHAT_BOOTSTRAP.md`, `ROADMAP.md`, `IMPLEMENTATION_PLAN.md`, active architecture/design docs, and current repository/runtime evidence together form the implementation contract.