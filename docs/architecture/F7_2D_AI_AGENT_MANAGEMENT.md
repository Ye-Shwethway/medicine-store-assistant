# F7.2D — AI Agent Management, MCP Access, Provider Registry & Delegated Authority

Status: **F7.2D0/F7.2D2/F7.2D3/F7.2D4A verified; replacement ChatGPT MCP v2.1 acceptance verified; F7.2D4 native internal-agent runtime continues next; broad AI/production writes remain unauthorized**

## Purpose

MSA supports multiple AI execution paths without tying the system to one vendor, model, transport, or client. Custom MCP, native provider-backed agents, future Telegram/Flutter AI, scheduled/system jobs, optional Action clients, and ordinary Web/API calls reuse the same typed backend domain services and authority engine.

AI Agent Management is an **Owner-only** control plane. Human users, named AI agents, external clients, provider connections, models, assignments, conversations, and multi-agent sessions are distinct concepts.

Canonical rules:

- `full transport/schema != full current authority`
- `agent identity != provider != model != client transport != human user`
- `MCP adapter != native internal-agent runtime`

Canonical execution-path contract: `F7_2D_EXECUTION_PATH_SEPARATION.md`.

## Canonical separation

- **Human user** — canonical person/account with stable `user_id`, credentials, role, state, sessions.
- **AI agent** — named durable principal with stable `agent_id`, canonical identity, capability/location/authority/execution policy.
- **External client/runtime** — transport/runtime such as ChatGPT custom MCP or optional Action client.
- **Provider connection** — outbound model API configuration plus protected credential reference.
- **Model** — provider-local model resource with discovered/configured capability metadata.
- **Assignment** — provider/model/fallback configuration used by an `INTERNAL_MODEL` agent.
- **Conversation** — MSA-owned native chat history between a human/client and one selected internal agent.
- **Multi-agent session** — reusable topology/execution context of selected named agents.

Changing provider/model never changes `agent_id` or authority. Multi-agent sessions never union participant privileges.

## Runtime modes

Supported conceptual modes:

1. `EXTERNAL_MCP_CLIENT`
2. `INTERNAL_MODEL`
3. `EXTERNAL_ACTION_CLIENT`
4. `SYSTEM_AUTOMATION`

Runtime mode is never authority by itself.

## Canonical peer execution paths

### External MCP / ChatGPT

`ChatGPT model -> HTTPS/OAuth MCP -> typed MCP action -> MCP authority intersection -> typed MSA backend operation -> data/service -> result`

This is a direct execution path. The external reasoning model performs the reasoning and may directly invoke any implemented MCP action for which it has effective authority. It does **not** need an internal provider-backed agent as an intermediary.

Production proof already exists:

`ChatGPT/SOL -> msa_shadow_read_rows -> shadow-read backend -> PostgreSQL shadow rows -> result`

The corresponding Audit evidence recorded `IANEO -> msa_shadow_read_rows -> SUCCESS` under `EXTERNAL_MCP` / `EXTERNAL_MCP_CLIENT` / `mcp:read`.

MCP is typed backend access, not arbitrary database access. The backend operation may query PostgreSQL internally, but MCP never receives raw SQL/table access, DB credentials, shell/filesystem, or unrestricted infrastructure access.

### Native internal-agent runtime

`MSA Web chat / future Telegram / Flutter / automation -> native agent runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

An `INTERNAL_MODEL` agent is a first-class MSA runtime. It must work independently of ChatGPT and independently of the MCP transport. ChatGPT unavailability must not disable native MSA agents.

### Direct Web/API runtime

`MSA Web/API -> authenticated typed backend API -> authority gate -> typed MSA operation`

Ordinary product workflows do not need an AI hop merely because AI capability exists.

### System automation

`SYSTEM_AUTOMATION -> configured policy/runtime -> typed MSA operation`

System jobs remain distinct principals and do not inherit authority from MCP or another agent by accident.

## Shared backend rule

MCP actions, Web/API endpoints, and internal-agent tools should reuse shared domain/service functions. Do not chain adapters merely to reach the same operation.

Forbidden drift:

- internal agents must not call the public MCP endpoint as their normal MSA tool/data gateway;
- MCP must not call an internal agent merely to execute an action the external model can already execute directly;
- Web/API must not route through MCP for ordinary typed backend operations;
- business rules/authorization must not be duplicated independently in every adapter.

## `msa_agent_invoke` semantics

`msa_agent_invoke` is an **optional delegation/orchestration bridge** exposed in the long-lived MCP schema. It is not the central gateway for MSA actions.

Appropriate flow:

`External MCP model -> msa_agent_invoke -> selected INTERNAL_MODEL agent -> independent specialist analysis/result`

Use cases include independent review, specialist delegation, cross-model comparison, or starting an internal multi-agent workflow.

Do **not** use:

`External MCP model -> msa_agent_invoke -> internal agent -> direct MSA action`

when the external model already has authority for that MSA action and no independent internal reasoning is required.

## F7.2D0 — custom MCP — VERIFIED COMPLETE

Verified live architecture:

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> authenticated client context -> authority gates -> typed backend`

Current external scopes: `mcp:connect`, `mcp:read`, `offline_access`; propose/write/control disabled. Anonymous `/mcp` returns 401.

Final long-lived schema: `2026-08-23.v2.1`, 106 actions. Replacement client acceptance is complete. Direct row-level `NEW_UNMAPPED` read and named-agent Audit proof are verified.

Schema visibility never grants execution authority. New action names are exceptional; prefer enabling existing schema slots, backend-allowlisted action values, or backward-compatible optional inputs.

## F7.2D2 — Agent Management & multi-agent sessions — VERIFIED COMPLETE

Runtime anchor: PR #58; merge `3b385a37b95c1ff79f76883381d8268fa6c49db2`; deploy run `32620386876`; migration `0010_mcp_oauth -> 0011_ai_agents`.

Each agent has immutable `agent_id`, editable `display_name`, unique `call_name`, purpose, runtime mode, lifecycle, capability/location/authority/execution/confirmation metadata, and provenance.

MSA owns canonical self-identity. Every native internal invocation must inject current server-generated identity rather than relying on model memory/chat history.

Persistent sessions already support `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`, ordered participants, role labels, and lifecycle. F7.2D2 established topology; execution is later.

Canonical design: `F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`.

## Authority model

Human-delegated internal agent:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_gate`

External MCP named agent:

`effective_authority = OAuth/client_scope ∩ external_agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_gate`

Autonomous/system:

`effective_authority = owner_configured_autonomous_policy ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_gate`

Provider/model choice never multiplies authority.

External and internal agents may intentionally have different permissions even when their display names/purposes are similar.

## F7.2D3 — Provider Registry + model catalog — VERIFIED COMPLETE

Runtime anchor: PR #60; merge `882c67b0134edb59156c17e948128de0ca8c3365`; deploy run `32621925138`; migration `0011_ai_agents -> 0012_providers`.

Supported provider kinds:

- OpenAI
- Google Gemini
- OpenRouter
- NanoGPT
- generic `OPENAI_COMPATIBLE`

Provider credentials are write-only from Owner UI, stored server-side with opaque DB references, and never read back to browser/chat. Custom provider URLs are SSRF-bounded and responses are sanitized/bounded.

The flow separates discovery from approved use:

`Add provider -> credential -> Test connection -> Fetch models -> inspect/test -> Save approved model -> Enable`

Provider setup/test ping proves connectivity only. It does **not** create a native agent workflow or grant authority.

## F7.2D4A — external MCP named-agent binding — VERIFIED COMPLETE

The Owner can bind/rebind/unbind a live OAuth grant to a named `EXTERNAL_MCP_CLIENT` agent without reconnecting ChatGPT. Effective MCP authority is the live OAuth/client capability intersected with live agent policy and system gates.

Current production migration head is `0016_revoke_stale_chatgpt_oauth` after PR #80 removed stale duplicate ChatGPT grants/tokens/bindings while preserving the newest active replacement grant.

The external binding is inbound attribution/authority only; it does not turn ChatGPT into an internal provider-backed runtime and does not give MSA a callback channel into ChatGPT.

## F7.2D4 — Native internal-agent runtime — NEXT

F7.2D4 now explicitly builds the **native MSA provider-backed agent runtime**, independent of MCP.

### A. Assignment/fallback contract

Required data:

- stable assignment ID;
- `agent_id` for `INTERNAL_MODEL` agent;
- primary enabled provider + Owner-saved healthy model;
- ordered optional fallbacks;
- capability expectations;
- timeout/output policy;
- optional usage/cost budget metadata;
- enabled/disabled state and provenance.

Rules:

- only `INTERNAL_MODEL` agents receive provider/model assignments;
- provider must be enabled;
- model must be Owner-saved and healthy;
- known incompatibility fails closed;
- unknown capability stays explicit and may require Owner acknowledgement;
- fallback never expands authority;
- provider/model/fallback changes never alter `agent_id` or authority;
- no silent arbitrary model substitution.

### B. Native invocation service

Create a backend service callable without MCP:

`native caller -> resolve agent -> resolve assignment -> inject identity/policy -> provider call -> normalize -> audit -> response`

The runtime must remain usable when ChatGPT is unavailable.

### C. Canonical identity injection

Every native invocation injects at least current `display_name`, `call_name`, stable `agent_id`, runtime identity, and bounded policy context from server-owned configuration.

### D. Native conversation persistence + Web AI Chat

MSA must support its own chat interface and durable conversations/messages.

Expected product capabilities:

- multiple internal agents can be created;
- chat page has an agent selector;
- new/resume conversation;
- conversation history;
- selected agent identity/state/provider/model visibility;
- native message execution through the selected internal agent;
- later streaming and richer UX as appropriate.

This is the survival path: MSA-owned UI -> MSA-owned native runtime -> configured provider API, with no ChatGPT dependency.

### E. Internal typed-tool execution

Internal agents must access MSA functions through internal typed-tool adapters over shared domain services, not by calling the public MCP server.

The internal tool surface may mirror MCP/domain semantics where useful, but authority is evaluated under the internal agent's own context.

### F. Provider failover/provenance

Fallback execution must record selected provider/model, whether fallback occurred, reason, latency, and available usage/cost metadata. Fail clearly when the approved chain is exhausted.

### G. Multi-agent execution

Activate the existing session topology incrementally for `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`. Each participant keeps separate identity/assignment/authority; privileges never union.

### H. Optional MCP -> native-agent delegation

After native runtime exists, `msa_agent_invoke` / session MCP actions may become adapters into it for explicit delegation. This remains optional orchestration, not the normal direct-MCP data/action path.

### F7.2D4 acceptance

Pass when:

1. Owner can assign primary + ordered fallback models to internal agents;
2. multiple internal agents retain stable identities across assignment/model changes;
3. native backend invocation works without MCP;
4. canonical identity is injected server-side;
5. MSA Web AI Chat can select an internal agent and obtain a real provider-backed response;
6. conversation/message state is durable;
7. at least one authorized internal typed MSA read works through shared backend services, not public MCP;
8. provider failover behaves deterministically and records provenance;
9. later/optional MCP delegation can invoke a selected native internal agent without becoming the core runtime;
10. acceptance is explicitly proven with ChatGPT out of the loop: `MSA Web -> selected internal agent -> provider/model -> authorized typed MSA read -> response/audit`;
11. provider/model changes do not change authority;
12. no production inventory mutation, workbook import, or DB canonical promotion occurs.

## Owner-only control plane

Only `OWNER` may manage AI agents/principals, external MCP clients/grants, provider connections/credentials, model discovery/testing/assignment, agent policy, multi-agent session configuration, and shared AI-feature/global settings.

An agent/client may never self-escalate or edit its own security/control-plane policy.

## Canonicality/write boundary

Google Sheets remains operationally authoritative and PostgreSQL remains non-canonical. Agent/provider/model/MCP work does **not** authorize production stock mutation, transfers, Smart Calculator deductions, Sheet mirror conversion, or DB canonical promotion. System production-write gates remain closed.

## Implementation order

1. F7.2D0 — custom MCP connectivity/schema/acceptance — **VERIFIED**
2. F7.2D2 — named Agent Management + session topology — **VERIFIED**
3. F7.2D3 — Provider Registry + saved model catalog — **VERIFIED**
4. F7.2D4A — external MCP named-agent binding — **VERIFIED**
5. F7.2D4 — native internal-agent runtime, assignment/fallback, conversation/chat, tools, multi-agent execution — **NEXT**
6. F7.3 — full actor-aware Audit / operation ledger
7. F7.4+ operational product slices
8. controlled production writes only in later explicitly authorized slices
