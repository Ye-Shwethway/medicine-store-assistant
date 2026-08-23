# F7.2D — AI Agent Management, MCP Access, Provider Registry & Delegated Authority

Status: **F7.2D0 and F7.2D2 verified complete; F7.2D3 Provider Registry + model catalog next; broad AI/production writes remain unauthorized**

## Purpose

MSA supports multiple AI execution paths without tying identity or authority to one vendor/model/client. The same backend authority engine governs:

- ChatGPT through custom MCP;
- internal provider-backed agents;
- optional Custom GPT Actions;
- future Telegram/Flutter AI features;
- scheduled/system jobs;
- other typed integrations.

AI Agent Management is an **Owner-only** control plane. Human users, AI agents, external clients, provider connections, models, assignments, and multi-agent sessions remain separate concepts.

Canonical rule:

`full transport/schema != full current authority`

## Canonical separation

### Human user

Canonical person/account with stable `user_id`, credentials, human role, state, and sessions.

### AI agent

Named `AI_AGENT` principal with stable `agent_id`, canonical name, capabilities, location scope, authority ceiling, execution/confirmation policy, and lifecycle state.

The agent is the durable identity/policy boundary. It is not the provider/model.

### External client/runtime

Transport/runtime such as ChatGPT custom MCP, optional Action client, Web AI Chat, future Telegram/Flutter client, or system integration.

External client identity answers **who/what connected**, not **which model is the agent**.

### Provider connection

Outbound model API configuration: vendor/endpoint/compatibility settings plus protected credential reference.

### Model

Provider-local model resource with discovered/configured capability metadata.

### Assignment

Which provider/model an internal agent currently uses, including future primary/fallback ordering.

Changing assignment never changes `agent_id` or authority.

### Multi-agent session

Reusable topology of selected named agents for future group/compare/review/debate orchestration. Session topology never unions participant privileges.

## Runtime modes

Supported conceptual modes:

1. `EXTERNAL_MCP_CLIENT`
2. `INTERNAL_MODEL`
3. `EXTERNAL_ACTION_CLIENT`
4. `SYSTEM_AUTOMATION`

Runtime mode is never authority by itself.

## F7.2D0 — custom MCP — VERIFIED COMPLETE

Live architecture:

`ChatGPT Developer Mode -> HTTPS/OAuth -> custom MSA MCP -> authenticated client context -> capability/location/operation/system gates -> typed MSA backend`

Verified runtime:

- remote MCP live at the MSA public HTTPS origin;
- OAuth authorization code + PKCE S256;
- protected-resource/authorization-server metadata;
- dynamic client registration;
- rotating refresh tokens + `offline_access`;
- ChatGPT Developer Mode connection successful;
- fresh ChatGPT chat successfully called MSA identity/system reads;
- current scopes `mcp:connect`, `mcp:read`, `offline_access`;
- propose/write/control disabled;
- anonymous `/mcp` = 401;
- source SHA `611918572717058882849ede7a4cc2a39dd2e3ac`;
- deploy run `32618376291`.

The MCP service remains a protocol adapter, not a second business-logic implementation or raw database gateway.

### Full-schema policy

The MCP catalog is designed once for durable typed MSA capabilities across read/propose/future-write/User Management/Agent Management/Provider Registry/Audit/Settings domains.

A discoverable tool is not authorized merely because it exists. Execution always depends on live backend policy and project-level gates.

Never expose:

- arbitrary SQL;
- raw table/column editing;
- PostgreSQL credentials;
- VPS shell/SSH/filesystem;
- Google Sheet credentials;
- plaintext provider API keys;
- unrestricted environment editing;
- generic arbitrary HTTP proxying.

## F7.2D2 — Agent Management & multi-agent sessions — VERIFIED COMPLETE

Canonical design:

`F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`

Verified checkpoint:

`../checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`

Runtime anchor:

- PR #58;
- merge `3b385a37b95c1ff79f76883381d8268fa6c49db2`;
- deploy run `32620386876`, job `97147568336`;
- migration `0010_mcp_oauth -> 0011_ai_agents`.

### Agent identity model

Each agent has:

- immutable stable UUID `agent_id`;
- Owner-editable `display_name`;
- case-insensitive unique `call_name` for human-friendly addressing/selection;
- optional purpose/description;
- runtime mode;
- `ACTIVE` / `DISABLED` / `REVOKED` state;
- capability scopes;
- location scope;
- authority ceiling;
- delegated/autonomous execution policy;
- confirmation policy;
- provenance/timestamps.

Renaming preserves `agent_id`.

### Self-identity rule

The model must not be expected to remember its own name from chat history.

MSA owns canonical identity. Future internal-agent runtime invocation must inject a server-generated identity context derived from current canonical agent configuration, including at least the agent display name and stable `agent_id`.

Representative context:

`You are <display_name>. Your stable MSA agent identity is <agent_id>. Respond as this configured agent and do not claim another agent identity.`

F7.2D2 already exposes deterministic identity-context preview; F7.2D4 will use it in real model invocation assembly.

### Multi-agent session model

Persistent session topology supports:

- stable `session_id`;
- session name/objective;
- modes `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`;
- ordered participant list;
- optional participant role labels;
- open/closed lifecycle.

One agent may participate in many sessions. One session may contain many agents. Same agent cannot occur twice in one session.

Provider/model inference is intentionally disabled in F7.2D2.

## Effective authority

Human-delegated:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_write_gate`

External client without live human session:

`effective_authority = registered_client_scope ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_write_gate`

Autonomous/system:

`effective_authority = owner_configured_autonomous_policy ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_write_gate`

Provider/model choice never multiplies authority.

Multi-agent sessions evaluate each participant independently and never union permissions.

## F7.2D3 — Provider Registry + model catalog — NEXT

Provider Registry is Owner-only.

Built-in presets:

- OpenAI
- Google Gemini
- OpenRouter
- NanoGPT

Generic adapter:

- `OPENAI_COMPATIBLE`

### Canonical Owner workflow

`Add provider -> provision credential -> Test connection -> Fetch models -> inspect normalized capabilities -> Save/enable`

### Provider connection data

Persist only non-secret configuration and a protected secret/credential reference:

- stable `provider_id`;
- display name;
- provider kind;
- base URL where applicable;
- `credential_ref`/secret status metadata, never plaintext API key;
- non-secret compatibility settings;
- enabled/disabled state;
- connection/model-fetch status and timestamps;
- created/updated provenance.

### Provider secret policy

- API keys are write-only from Owner UI.
- Browser never receives plaintext key read-back.
- DB does not store plaintext provider keys.
- Logs/errors redact Authorization headers/tokens/secrets.
- Provider credentials are distinct from inbound MCP OAuth/client credentials and must never be reused.

### Generic provider SSRF protections

For custom base URLs:

- HTTPS by default in production;
- reject loopback/link-local/cloud-metadata/private destinations unless explicitly authorized by architecture;
- validate redirects against forbidden destinations;
- re-resolve/check targets where practical for DNS rebinding mitigation;
- bound response size/count/field lengths;
- treat provider responses/model metadata as untrusted input.

### Model catalog

Dynamic model discovery should retain, where actually known:

- provider-local model ID;
- display name;
- fetched/refreshed timestamps;
- availability;
- text capability;
- vision capability;
- tool/function calling;
- structured output/JSON;
- context/output limits;
- verified provider metadata.

Unknown capability remains unknown. Never grant an agent capability merely because fetched provider metadata claims or implies support.

Provider health, model health, and agent health are separate concepts.

## F7.2D4 — model assignment/fallbacks

After Provider Registry:

- assign primary provider/model to named internal agent;
- optional ordered fallback models;
- required-capability compatibility checks;
- timeout/output policy;
- optional usage/cost ceilings/metadata;
- canonical agent identity injection every invocation;
- future execution of multi-agent sessions across same-provider or cross-provider agents.

Fallback never expands agent authority and must not silently use incompatible semantics.

## Owner-only control plane

Only `OWNER` may manage:

- AI agents/principals;
- external MCP clients/grants;
- provider connections/credentials;
- model discovery/testing/assignment;
- agent capability/location/authority/execution policy;
- multi-agent session configuration;
- optional Action clients;
- shared AI-feature policy;
- global Settings.

An agent/client can never self-escalate or edit its own security/control-plane policy.

## MSA workflow parity

Preserve:

1. inspect source evidence;
2. reconcile against authoritative/current truth;
3. classify `SAFE`, `REVIEW`, `CONFLICT`, `NEW_UNMAPPED`;
4. execute only within Owner-authorized typed scope;
5. surface ambiguity;
6. commit through deterministic backend operations;
7. read committed state back;
8. record actor/operation provenance;
9. report success only after verification.

## Canonicality/write boundary

Google Sheets remains operationally authoritative and PostgreSQL remains non-canonical.

Agent/provider/model/MCP capability work does **not** authorize:

- production stock mutation;
- AI inventory writes;
- transfers;
- Smart Calculator deductions;
- Sheet mirror conversion;
- DB canonical promotion.

System production-write gates remain closed.

## Web implementation workflow

For MSA Web UI, canonical default is:

`UI/UX Pro Max -> repo design system -> authenticated API contract -> direct code implementation -> responsive/accessibility/runtime verification`

Figma is optional and only used when the Owner explicitly requests it or a specific task genuinely requires it.

## Implementation order

1. F7.2D0 — custom MCP connectivity — **VERIFIED COMPLETE**
2. F7.2D2 — named Agent Management + multi-agent sessions — **VERIFIED COMPLETE**
3. F7.2D3 — Provider Registry + model catalog — **NEXT**
4. F7.2D4 — model assignment/fallbacks + runtime identity
5. optional F7.2D1 — Custom GPT Action proof only for concrete standalone-GPT need
6. F7.3 — actor-aware Audit / operation ledger
7. later AI Assistant/richer integrations
8. controlled writes only in later explicitly authorized slices

## F7.2D exit criteria

F7.2D is complete only when:

- custom MCP authorized reads and revocation are proven;
- named agents are managed separately from humans;
- canonical self-identity survives provider/model changes;
- multi-agent session topology exists;
- Owner can configure built-in/custom OpenAI-compatible providers without hard-coded model IDs;
- model fetch/test/save/assign works;
- provider/model changes do not alter authority;
- non-Owner cannot use Agent Management/Provider Registry;
- no AI principal self-escalates;
- no production inventory write is enabled merely by F7.2D completion.
