# F7.2D — AI Agent Management, MCP Access, Provider Registry & Delegated Authority

Status: **F7.2D0, F7.2D2, and F7.2D3 verified complete; F7.2D4 model assignment/fallback/runtime identity next; broad AI/production writes remain unauthorized**

## Purpose

MSA supports multiple AI execution paths without tying identity or authority to one vendor/model/client. The same backend authority engine governs custom MCP, internal provider-backed agents, optional Custom GPT Actions, future Telegram/Flutter AI features, scheduled/system jobs, and other typed integrations.

AI Agent Management is an **Owner-only** control plane. Human users, AI agents, external clients, provider connections, models, assignments, and multi-agent sessions remain separate concepts.

Canonical rule: `full transport/schema != full current authority`.

## Canonical separation

- **Human user** — canonical person/account with stable `user_id`, credentials, human role, state, sessions.
- **AI agent** — named durable principal with stable `agent_id`, canonical name, capability/location/authority/execution policy.
- **External client/runtime** — transport/runtime such as ChatGPT custom MCP or optional Action client.
- **Provider connection** — outbound model API configuration plus protected credential reference.
- **Model** — provider-local model resource with discovered/configured capability metadata.
- **Assignment** — provider/model/fallback configuration currently used by an internal agent.
- **Multi-agent session** — reusable topology of selected named agents.

Changing provider/model never changes `agent_id` or authority. Multi-agent sessions never union participant privileges.

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

Verified current scopes: `mcp:connect`, `mcp:read`, `offline_access`; propose/write/control disabled. Anonymous `/mcp` returns 401. Custom GPT Actions are optional/fallback only.

The MCP catalog is full-schema/policy-gated. Never expose arbitrary SQL/table edits, database credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, unrestricted environment editing, or generic arbitrary HTTP proxying.

## F7.2D2 — Agent Management & multi-agent sessions — VERIFIED COMPLETE

Runtime anchor: PR #58; merge `3b385a37b95c1ff79f76883381d8268fa6c49db2`; deploy run `32620386876`, job `97147568336`; migration `0010_mcp_oauth -> 0011_ai_agents`.

Each agent has immutable `agent_id`, editable `display_name`, unique `call_name`, purpose, runtime mode, lifecycle, capability/location/authority/execution/confirmation metadata, and provenance.

MSA owns canonical self-identity. Internal model invocations must inject server-generated identity from current agent configuration, including at least display name and stable agent ID, rather than relying on chat history.

Persistent sessions support stable session ID, name/objective, `GROUP` / `COMPARE` / `REVIEW` / `DEBATE`, ordered participants, role labels, and open/closed lifecycle.

Canonical design: `F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`.

## Effective authority

Human-delegated:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_write_gate`

External client without live human session:

`effective_authority = registered_client_scope ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_write_gate`

Autonomous/system:

`effective_authority = owner_configured_autonomous_policy ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_write_gate`

Provider/model choice never multiplies authority.

## F7.2D3 — Provider Registry + model catalog — VERIFIED COMPLETE

Runtime anchor:

- PR #60;
- merge `882c67b0134edb59156c17e948128de0ca8c3365`;
- deploy run `32621925138`, job `97151213410`;
- migration `0011_ai_agents -> 0012_providers`;
- issue #26 `status=success`.

Provider Registry is Owner-only.

Built-in presets:

- OpenAI
- Google Gemini
- OpenRouter
- NanoGPT

Generic adapter:

- `OPENAI_COMPATIBLE`

### Verified Owner workflow surface

`Add provider -> provision credential -> Test connection -> Fetch models -> inspect normalized capabilities -> Enable`

A real provider API was intentionally not invoked by deployment verification because no Owner credential is supplied through CI. The first real provider test occurs from the Owner Web UI.

### Provider connection data

Persistent provider records include stable provider ID, display name, kind, base URL/compatibility mode, opaque credential reference/status, enabled/disabled state, connection/model-fetch state/timestamps/errors, and provenance.

### Provider secret policy — VERIFIED

- Provider API keys are write-only from Owner UI.
- Browser never receives saved-key read-back.
- PostgreSQL does not store plaintext provider keys.
- Secret material lives in dedicated server-side `msa_provider_secrets` volume; DB stores opaque `credential_ref` only.
- Provider credentials are distinct from inbound MCP OAuth/client credentials.
- Deploy verifier proved dummy secret plaintext was absent from the DB and deleted with credential removal.

### Generic provider security — VERIFIED FOUNDATION

Custom base URLs require public HTTPS. Backend rejects credentials embedded in URL, query/fragment, private/loopback/link-local/multicast/reserved/unspecified destinations, and redirects. Destination resolution is rechecked before provider call. Responses are bounded in size/model count and normalized provider metadata is sanitized.

### Model catalog — VERIFIED FOUNDATION

Dynamic discovery persists provider-local model ID, display name, availability, nullable/unknown text/vision/tool/structured-output capability, context/output limits when supplied, bounded sanitized provider metadata, and fetch timestamps.

Unknown capability remains unknown. Provider health, model-fetch health, and agent health remain separate concepts.

### Provider enable gate

Provider enablement requires:

1. configured credential;
2. successful connection test;
3. successful model fetch.

Provider setup never grants AI authority.

### Web presentation refinements delivered with F7.2D3

- Create agent/New session use the dashboard secondary-control style.
- Agents are grouped as `External / MCP agents` and `Internal / provider-backed agents`.
- Agent cards expose `Agent name`, `Origin`, and `Model` primary fields.
- Unassigned internal agents show `Not assigned`.
- External runtime model identity remains `Client-managed` unless explicitly known; no model is guessed.
- Provider Registry is colocated in the same Owner-only AI control-plane page.

Verified checkpoint: `../checkpoints/F7_2D3_PROVIDER_REGISTRY_VERIFIED_2026-08-23.md`.

## F7.2D4 — model assignment/fallback/runtime identity — NEXT

F7.2D4 connects durable internal-agent identity to provider/model implementation.

Required capabilities:

- primary provider/model assignment for `INTERNAL_MODEL` agents;
- optional ordered fallback chain;
- enabled-provider/current-model validation;
- required-capability compatibility checks;
- unknown capability represented explicitly and requiring Owner acknowledgement where appropriate;
- timeout/output policy and optional cost/usage metadata;
- canonical identity injection on every internal invocation;
- agent cards show actual assigned provider/model;
- provider/model/fallback changes never alter agent authority or `agent_id`;
- prepare narrow real inference and future cross-model multi-agent execution.

Fallback never expands authority and must not silently substitute incompatible semantics.

### Existing MCP client relationship

The existing ChatGPT MCP connection is an external runtime/client, not automatically a named AI agent. Do not invent a name or silently bind it to an `AI_AGENT`. If the Owner wants the connected ChatGPT/MCP runtime represented as a named external agent, implement an explicit Owner-controlled binding between registered external client/grant and named external agent principal.

## Owner-only control plane

Only `OWNER` may manage AI agents/principals, external MCP clients/grants, provider connections/credentials, model discovery/testing/assignment, agent capability/location/authority/execution policy, multi-agent session configuration, optional Action clients, shared AI-feature policy, and global Settings.

An agent/client can never self-escalate or edit its own security/control-plane policy.

## Canonicality/write boundary

Google Sheets remains operationally authoritative and PostgreSQL remains non-canonical. Agent/provider/model/MCP capability work does **not** authorize production stock mutation, AI inventory writes, transfers, Smart Calculator deductions, Sheet mirror conversion, or DB canonical promotion. System production-write gates remain closed.

## Web implementation workflow

Canonical default:

`UI/UX Pro Max -> repo design system -> authenticated API contract -> direct code implementation -> responsive/accessibility/runtime verification`

Figma is optional only when explicitly requested.

## Implementation order

1. F7.2D0 — custom MCP connectivity — **VERIFIED COMPLETE**
2. F7.2D2 — named Agent Management + multi-agent sessions — **VERIFIED COMPLETE**
3. F7.2D3 — Provider Registry + model catalog — **VERIFIED COMPLETE**
4. F7.2D4 — model assignment/fallback/runtime identity — **NEXT**
5. optional F7.2D1 — Custom GPT Action proof only for concrete standalone-GPT need
6. F7.3 — actor-aware Audit / operation ledger
7. later AI Assistant/richer integrations
8. controlled writes only in later explicitly authorized slices

## F7.2D exit criteria

F7.2D is complete only when custom MCP authorized reads/revocation are proven; agents are distinct from humans/providers/models; canonical self-identity survives assignment changes; multi-agent topology exists; Owner can configure providers and dynamic models; model test/fetch/assignment works; provider/model choice does not alter authority; non-Owner is denied Agent/Provider control planes; no AI principal self-escalates; and production inventory writes remain independently gated.