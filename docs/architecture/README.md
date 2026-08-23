# Medicine Store Assistant — Architecture Index

Status: **F7.2A/B/C, F7.2D0 custom MCP/schema/acceptance, F7.2D2 named Agent Management/session topology, F7.2D3 Provider Registry/saved-model catalog, and F7.2D4A external MCP named-agent binding are verified; execution-path separation is now explicitly canonical; F7.2D4 native internal-agent runtime is next; PostgreSQL remains non-canonical**

This directory defines the canonical architecture for Medicine Store Assistant beyond the current spreadsheet-operating skill. The Git-backed `$msa` skill remains canonical at `skills/medicine-store-assistant/`.

## Core decision

MSA evolves toward a ledger-backed multi-client inventory system in which PostgreSQL is planned future canonical operational storage but is **not canonical yet**; Google Sheets remains operationally authoritative until explicit promotion; all clients/runtimes use typed application contracts; humans, AI agents, external clients, provider connections, models, assignments, conversations, and sessions remain separate concepts; deterministic backend code owns authorization/validation/idempotency/transactions/read-back/audit semantics.

## Critical execution-path invariant

Canonical contract: [F7_2D_EXECUTION_PATH_SEPARATION.md](F7_2D_EXECUTION_PATH_SEPARATION.md).

MSA has one shared typed backend/authority core and multiple **peer** execution paths.

### External MCP

`ChatGPT model -> MCP action -> authority intersection -> typed MSA backend operation -> result`

The external model is the reasoning engine and may directly invoke implemented MCP actions within its effective authority. Internal agents are not a mandatory intermediary.

Verified proof already exists through `msa_shadow_read_rows` and the corresponding `IANEO -> msa_shadow_read_rows -> SUCCESS` Audit event.

### Native internal agents

`MSA Web chat / future Telegram / Flutter / automation -> native INTERNAL_MODEL runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

Native internal agents must operate independently of ChatGPT and independently of the public MCP transport.

### Shared-core rule

MCP actions, Web/API endpoints, and internal-agent tools reuse shared backend domain/service functions. Do not chain transports merely to reach the same operation.

`msa_agent_invoke` is an optional delegation/orchestration bridge into a selected native internal agent; it is not the central gateway for ordinary direct MCP actions.

## Verified MCP external access

F7.2D0 is verified complete.

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> typed MSA backend`

Verified external scopes: `mcp:connect`, `mcp:read`, `offline_access`; propose/write/control remain disabled.

Final schema identity:

- version `2026-08-23.v2.1`
- 106 actions
- stable manifest/hash enforced by CI

Replacement-client acceptance is complete. MCP provides typed backend operations, not arbitrary SQL/table editing, DB credentials, shell/filesystem, or unrestricted infrastructure access.

## F7.2D2 — verified Agent Management foundation

Durable named AI agents have immutable `agent_id`, editable display/call names, server-owned canonical identity, lifecycle/capability/location/authority/execution/confirmation policy, and Owner-only management.

Persistent multi-agent topology supports `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`, ordered participants and role labels.

Detailed design: [F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md](F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md).

## F7.2D3 — verified Provider Registry/model catalog

Supported provider types:

- OpenAI
- Google Gemini
- OpenRouter
- NanoGPT
- generic `OPENAI_COMPATIBLE`

Provider secrets are write-only/server-side and PostgreSQL stores only opaque references. Test connection/model ping proves connectivity only; it does not create a native internal-agent workflow.

Owner-saved healthy models are the assignment candidates for `INTERNAL_MODEL` agents.

## F7.2D4A — verified external MCP named-agent binding

A live MCP OAuth grant may be explicitly bound to a named `EXTERNAL_MCP_CLIENT` agent. Effective MCP authority is the live client/OAuth capability intersected with the named-agent policy and system gates.

This external binding is inbound identity/authority attribution only. It does not turn ChatGPT into a provider-backed internal runtime and does not create a callback channel from MSA into ChatGPT.

## Canonical separation

- **Human user** — canonical person/account + role/session authority.
- **AI agent** — named durable identity + capability/location/execution policy.
- **External client/runtime** — transport such as custom MCP.
- **Provider connection** — outbound model API configuration + protected credential reference.
- **Model** — provider-local model resource/capability metadata.
- **Assignment** — provider/model/fallback policy for an internal agent.
- **Conversation** — MSA-owned native chat state for selected internal agents.
- **Multi-agent session** — reusable topology/execution context of selected agents.

Changing provider/model never changes agent identity or authority.

## F7.2D4 — next architecture slice

F7.2D4 now explicitly builds the **native MSA internal-agent runtime**, not an MCP-dependent runtime.

Order:

1. primary + ordered fallback assignment contract;
2. MCP-independent native backend invocation service;
3. canonical server-owned identity/policy injection;
4. real provider-backed single-agent inference;
5. durable conversation/message persistence;
6. MSA Web AI Chat with agent selection;
7. internal typed-tool adapter over shared MSA domain services, not public MCP;
8. deterministic provider failover + provenance;
9. actual `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` execution;
10. optional MCP -> native-agent delegation through already-published MCP schema slots.

Required survival proof:

`MSA Web -> selected INTERNAL_MODEL agent -> provider/model -> authorized typed MSA read -> response + audit`

ChatGPT must be completely out of this acceptance path.

## Immediate order

1. F7.2D0 — custom MCP connectivity/schema/acceptance — **VERIFIED**
2. F7.2D2 — named Agent Management/session topology — **VERIFIED**
3. F7.2D3 — Provider Registry/saved model catalog — **VERIFIED**
4. F7.2D4A — external MCP named-agent binding — **VERIFIED**
5. F7.2D4 — native internal-agent runtime/assignment/chat/tools/multi-agent execution — **NEXT**
6. F7.3 — actor-aware operational Audit
7. later operational/AI Assistant slices
8. production writes only in later explicitly authorized stages

No production inventory write becomes authorized merely because provider/model capability or write-capable MCP schema slots exist.

## Web design/implementation rule

Default Web workflow:

`UI/UX Pro Max -> repo design system -> authenticated API contract -> direct implementation -> responsive/accessibility/runtime verification`

Figma is optional unless explicitly requested.

## Key documents

- [CANONICAL_INVENTORY_ARCHITECTURE.md](CANONICAL_INVENTORY_ARCHITECTURE.md)
- [INVENTORY_DATA_MODEL.md](INVENTORY_DATA_MODEL.md)
- [INVENTORY_INTEGRITY_AND_AUDIT.md](INVENTORY_INTEGRITY_AND_AUDIT.md)
- [API_AND_CLIENT_ARCHITECTURE.md](API_AND_CLIENT_ARCHITECTURE.md)
- [MIGRATION_AND_SHADOW_VALIDATION.md](MIGRATION_AND_SHADOW_VALIDATION.md)
- [F7_WEB_DASHBOARD.md](F7_WEB_DASHBOARD.md)
- [F7_2D_AI_AGENT_MANAGEMENT.md](F7_2D_AI_AGENT_MANAGEMENT.md)
- [F7_2D_EXECUTION_PATH_SEPARATION.md](F7_2D_EXECUTION_PATH_SEPARATION.md)
- [F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md](F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md)
- [F7_2D0_MCP_SCHEMA_FINALIZATION_V2.md](F7_2D0_MCP_SCHEMA_FINALIZATION_V2.md)
- [F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md](F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md)
- [F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md](F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md)
- [F7_2D4A_EXTERNAL_MCP_AGENT_BINDING.md](F7_2D4A_EXTERNAL_MCP_AGENT_BINDING.md)
- [F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md](F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md)
- `../checkpoints/F7_2D0_MCP_SCHEMA_V2_VERIFIED_2026-08-23.md`
- `../checkpoints/F7_2D4A_MCP_AGENT_BINDING_VERIFIED_2026-08-23.md`

## Design rule

Do not implement from one document in isolation. `AGENTS.md`, `NEW_CHAT_BOOTSTRAP.md`, `ROADMAP.md`, `IMPLEMENTATION_PLAN.md`, active architecture/design docs, and current repository/runtime evidence together form the implementation contract.
