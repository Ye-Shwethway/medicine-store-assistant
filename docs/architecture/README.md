# Medicine Store Assistant — Architecture Index

Status: **F7.2A/B/C, F7.2D0 custom MCP/schema/acceptance, F7.2D2 named Agent Management/session topology, F7.2D3 Provider Registry/saved-model catalog, F7.2D4A external MCP named-agent binding, native internal-agent runtime, single-agent AI Workspace, bounded native tools, and attachment UX are verified/manual accepted; D4.8 shared work/review substrate + Owner-only native REVIEW backend + Owner REVIEW UI are deployed; one provided-evidence REVIEW manual acceptance and per-participant read-tool hardening are current; PostgreSQL remains non-canonical**

This directory defines the canonical architecture for Medicine Store Assistant beyond the current spreadsheet-operating skill. The Git-backed `$msa` skill remains canonical at `skills/medicine-store-assistant/`.

## Core decision

MSA evolves toward a ledger-backed multi-client inventory system in which PostgreSQL is planned future canonical operational storage but is **not canonical yet**; Google Sheets remains operationally authoritative until explicit promotion; all clients/runtimes use typed application contracts; humans, AI agents, external clients, provider connections, models, assignments, conversations, work items, artifacts, reviews, and sessions remain separate concepts; deterministic backend code owns authorization/validation/idempotency/transactions/read-back/audit semantics.

## Critical execution-path invariant

Canonical contract: [F7_2D_EXECUTION_PATH_SEPARATION.md](F7_2D_EXECUTION_PATH_SEPARATION.md).

MSA has one shared typed backend/authority core and multiple **peer** execution paths.

### External MCP

`ChatGPT model -> MCP action -> authority intersection -> typed MSA backend operation -> result`

The external model is the reasoning engine and may directly invoke implemented MCP actions within its effective authority. Internal agents are not a mandatory intermediary.

### Native internal agents

`MSA Web chat / future Telegram / Flutter / automation -> native INTERNAL_MODEL runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

Native internal agents operate independently of ChatGPT and independently of the public MCP transport.

### Shared-core rule

MCP actions, Web/API endpoints, internal-agent tools, and Multi-Agent orchestration reuse shared backend domain/service functions. Do not chain transports merely to reach the same operation.

`msa_agent_invoke` remains an optional delegation/orchestration bridge, not the gateway for ordinary direct MCP actions.

## Verified MCP external access

F7.2D0 is verified complete.

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> typed MSA backend`

Verified external scopes: `mcp:connect`, `mcp:read`, `offline_access`; propose/write/control remain disabled.

Final schema identity:

- version `2026-08-23.v2.1`
- 106 actions
- stable manifest/hash enforced by CI

MCP provides typed backend operations, not arbitrary SQL/table editing, DB credentials, shell/filesystem, or unrestricted infrastructure access.

Several long-lived v2.1 tools intentionally use open `action: str` selectors with backend allowlists. D4.8 federation should reuse these existing tool names/slots where the bounded work/review contract fits before considering any schema-name expansion. A separate MSA MCP backend server is not required.

## Named Agent Management + Provider foundation

Durable named AI agents have immutable `agent_id`, editable display/call names, server-owned canonical identity, lifecycle/capability/location/authority/execution/confirmation policy, and Owner-only management.

Persistent multi-agent topology supports `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`, ordered participants and display role labels.

Provider Registry supports OpenAI, Google Gemini, OpenRouter, NanoGPT, and generic OpenAI-compatible providers. Provider secrets remain write-only/server-side and Owner-saved healthy models are assignment candidates for `INTERNAL_MODEL` agents.

Changing provider/model never changes agent identity or authority.

## External MCP named-agent binding

A live MCP OAuth grant may be explicitly bound to a named `EXTERNAL_MCP_CLIENT` agent. Effective MCP authority is the live client/OAuth capability intersected with the named-agent policy and system gates.

This external binding is inbound identity/authority attribution only. It does not turn ChatGPT into a provider-backed internal runtime and does not create a callback channel from MSA into ChatGPT.

## Native AI Workspace — verified

The native path is live independently of MCP:

`MSA Web -> INTERNAL_MODEL agent -> assigned provider/model -> authorized native typed read -> grounded response + provenance`

Verified/manual-accepted single-agent behavior includes durable conversations, agent selection, provider/model/fallback provenance, bounded native reads, hybrid deterministic + model-driven tool calling, clean Chat lifecycle UX, photo/file evidence persistence, image previews, and explicit no-vision/OCR boundary until provider byte processing is implemented.

## D4.8 Multi-Agent Review + federation — deployed REVIEW foundation

Canonical contract: [F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md](F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md).

Runtime checkpoint: `../checkpoints/F7_2D48_NATIVE_REVIEW_RUNTIME_2026-08-24.md`.

Deployment anchors:

- PR #100 shared substrate: `4a9f54e17f2b386dfdd390af5850be2100986aac`
- PR #101 native REVIEW backend: `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e`
- PR #103 Owner REVIEW UI: `c980446a7df27a352721115599a5ecf704797097`
- production migration head: `0021_review_orchestration_roles`
- latest REVIEW UI deploy run: `32660684770`, `status=success`
- REVIEW UI asset version: `f72d48-review-ui-1`

### Native-only is first-class

A Multi-Agent preset may consist entirely of internal agents. External ChatGPT/MCP participation is optional, never mandatory.

### Native vs federated participants

- **Native participants** are MSA-controlled `INTERNAL_MODEL` agents that can take bounded live turns.
- **Federated participants** are external systems such as bound ChatGPT/MCP that exchange persisted work/review artifacts asynchronously.

Do not fake a live external turn when MSA cannot directly invoke the external runtime.

### REVIEW — first executable mode

Deployed native-only flow:

`Owner task/evidence -> DRAFT -> REVIEWING -> ordered native participants -> WAITING_OWNER`

Stable orchestration roles are stored separately from Owner display labels:

- `ANALYST`
- `REVIEWER`
- `SYNTHESIZER`

Roles never grant authority.

Canonical lifecycle:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

`WAITING_EXTERNAL` is optional. `APPROVED` is review state, not inventory mutation.

### Shared work substrate — deployed

D4.8 persists durable Work Items, versioned Artifacts, version-bound Reviews, immutable Events, and a shared Attention Queue. Actor identity distinguishes Owner/User/Internal Agent/External MCP Agent/System.

Artifact/review persistence never mutates store data by itself. Only an authorized typed operation can do that after applicable gates pass; current production write gates remain closed.

Reviewer findings are bound to the exact prior Artifact ID/version reviewed. Participant provider/model/fallback/latency provenance is persisted separately for each native participant.

### Owner REVIEW UI — deployed

The AI Workspace Multi-Agent tab now exposes real Owner-only REVIEW controls:

- REVIEW preset selection;
- stable orchestration-role configuration + optional display labels;
- Work title/task submission;
- optional references to saved ownership-validated Chat attachment metadata;
- native REVIEW execution;
- reload-safe Recent Review Work Items;
- Artifact / Review / provenance / Attention / Event inspection;
- WAITING_OWNER return-for-revision.

GROUP / COMPARE / DEBATE remain deferred and are not presented as active fake workflows.

### Current REVIEW tool boundary

The first REVIEW executor currently uses the plain native provider invocation path. It does **not yet use the D4.7A model-driven native read-tool loop**.

Therefore the current manual acceptance is explicitly a **provided-evidence/native-reasoning REVIEW**. Do not represent REVIEW participant outputs as current-store grounded tool reads yet.

Before relying on REVIEW for live/current operational reasoning, add bounded per-participant native read-tool integration. Each participant must independently pass READ capability/authority checks; session membership must never union tool authority.

### Current acceptance gap

Backend, UI, CI, and deployment are present. D4.8 REVIEW is not fully verified until one real Owner browser run reaches `WAITING_OWNER`, exposes persisted Artifacts/Reviews/provenance, survives reload through Recent Review work, can be returned to REVIEWING with a persisted instruction, performs no inventory mutation, and requires no ChatGPT/MCP.

### Telegram attention layer

Telegram is planned as notification/lightweight attention delivery over the same persisted backend workflow state. It is not the orchestrator or source of truth.

Target UX:

`native review completes -> attention item / optional WAITING_EXTERNAL -> Telegram notifies Owner -> Owner stays in ChatGPT -> MCP opens work item -> external review submitted -> MSA continues`

Web, MCP, and Telegram must point to the same Attention Queue. Notification failure must not lose or advance workflow state.

### GROUP / COMPARE / DEBATE

- GROUP: bounded shared-context native agentic loop with Owner observation/steering and optional federated checkpoints.
- COMPARE: same task, independent participant answers until comparison.
- DEBATE: bounded native argument/counterargument rounds followed by synthesis; federation can be added later through explicit checkpoints.

## Canonical separation

- **Human user** — canonical person/account + role/session authority.
- **AI agent** — named durable identity + capability/location/execution policy.
- **External client/runtime** — transport/reasoning runtime such as custom MCP-bound ChatGPT.
- **Provider connection** — outbound model API configuration + protected credential reference.
- **Model** — provider-local model resource/capability metadata.
- **Assignment** — provider/model/fallback policy for an internal agent.
- **Conversation** — MSA-owned native single-agent chat state.
- **Multi-agent session/preset** — reusable orchestration topology.
- **Work item** — durable task lifecycle.
- **Artifact** — versioned evidence/work product/proposal.
- **Review** — version-bound assessment of an artifact/work item.
- **Attention item** — durable Owner/external attention signal shared across channels.

## Immediate order

1. Manually accept one provided-evidence/native-reasoning REVIEW through the deployed Owner UI.
2. Add bounded per-participant D4.7A native read-tool integration for REVIEW and re-accept a tool-using Review.
3. Add optional MCP federated `WAITING_EXTERNAL` work/review exchange with exact artifact-version binding.
4. Add Telegram attention notifications over persisted events/queue.
5. Add GROUP native loops + Owner steering + optional external checkpoints.
6. Add COMPARE / DEBATE execution.
7. Later controlled writes only after authority/audit/location/idempotency/canonicality prerequisites.

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
- [F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md](F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md)
- [F7_2D4_AI_WORKSPACE_AND_ACCESS.md](F7_2D4_AI_WORKSPACE_AND_ACCESS.md)
- [F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md](F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md)
- [F7_2D4A_EXTERNAL_MCP_AGENT_BINDING.md](F7_2D4A_EXTERNAL_MCP_AGENT_BINDING.md)
- [F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md](F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md)

## Design rule

Do not implement from one document in isolation. `AGENTS.md`, `NEW_CHAT_BOOTSTRAP.md`, `ROADMAP.md`, `IMPLEMENTATION_PLAN.md`, active architecture/design docs, and current repository/runtime evidence together form the implementation contract.
