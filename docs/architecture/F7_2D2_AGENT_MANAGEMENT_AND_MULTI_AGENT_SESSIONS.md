# F7.2D2 — Agent Management, Named Identity & Multi-Agent Sessions

Status: **approved implementation contract**

## Purpose

F7.2D2 creates the Owner-only control plane for durable AI-agent identities and reusable multi-agent sessions before provider/model assignment is implemented.

The slice must support agents as named participants rather than anonymous model slots. A future internal agent must know its canonical name because MSA injects that identity from server-side configuration into every runtime invocation. Provider/model assignment may change later without changing the agent's identity.

Canonical separation:

`agent identity != provider != model != client transport != human user`

## Agent identity

Each AI agent has:

- stable UUID `agent_id`;
- Owner-editable `display_name`;
- unique case-insensitive `call_name` used for human-friendly selection/addressing;
- optional description/purpose;
- runtime mode;
- lifecycle state `ACTIVE`, `DISABLED`, or `REVOKED`;
- typed capability grants;
- location scope;
- authority ceiling;
- execution policy;
- confirmation policy;
- created/updated provenance.

`agent_id` is immutable. Renaming an agent changes presentation/addressing but not identity, audit history, provider assignment, session membership, or authority.

### Self-identity contract

The model must not be expected to remember its own name from conversation history alone. MSA owns the durable truth.

For every internal-agent invocation, the runtime context will include canonical identity metadata derived from `agent_id`, including at minimum:

`You are <display_name>. Your stable MSA agent identity is <agent_id>. Respond as this configured agent and do not claim another agent identity.`

The exact runtime prompt/instruction assembly belongs to F7.2D4, but F7.2D2 persists the canonical identity required to generate it.

The API/UI may expose a deterministic `identity_context` preview for Owner inspection. It contains no secret/provider credential material.

## Human-friendly names

- `display_name`: presentation name, 1–80 characters.
- `call_name`: concise selectable/addressable name, 1–64 characters.
- `call_name` is unique case-insensitively among non-revoked agents.
- the Owner may rename either value.
- name resolution for future chat/session orchestration uses canonical stored `call_name`, never fuzzy model invention.

Examples: `Mira`, `Inventory Analyst`, `Reconciliation Reviewer`.

## Multi-agent session foundation

MSA supports reusable sessions that contain one or more selected agents.

A session has:

- stable `session_id`;
- Owner-defined `session_name`;
- optional objective/description;
- mode;
- lifecycle state;
- ordered participant membership;
- creator/update provenance.

Initial session modes:

- `GROUP` — selected agents participate in one shared orchestration context;
- `COMPARE` — the same task can later be sent independently to selected agents/models and results compared;
- `REVIEW` — participants can later act as proposer/reviewer/critic roles;
- `DEBATE` — reserved orchestration mode for later turn-based comparison.

F7.2D2 persists session topology only. It does **not** call providers/models yet.

## Session participants

Each session participant records:

- `session_id`;
- `agent_id`;
- stable order/position;
- optional role label such as `Primary`, `Reviewer`, `Analyst`, `Critic`;
- active membership state.

One agent may belong to many sessions. One session may include many agents. The same agent cannot appear twice in one session.

Disabled/revoked agents remain historically referential but cannot be newly activated for execution.

## Multi-model future compatibility

F7.2D3/F7.2D4 may assign different providers/models to each agent. Therefore one session can later contain agents backed by:

- different models from one provider;
- models from multiple providers;
- primary/fallback chains;
- a mixture of internal model agents and future specialized runtime types where policy permits.

A session never grants extra authority. For every participant:

`effective_authority = participant_agent_policy ∩ invoking_human_or_session_policy ∩ location_scope ∩ operation_policy ∩ system_write_gate`

Comparison/debate orchestration cannot union privileges across agents.

## Initial capability policy

F7.2D2 must not authorize production inventory writes.

Canonical capability classes are stored explicitly, initially including:

- `mcp:read`
- `mcp:propose`
- `mcp:write`
- `mcp:control`

The product may show all classes, but current system write gates remain authoritative. Granting a future-looking capability in Agent Management does not bypass the project-level write/canonicality gate.

For this slice, newly created internal agents default to read-only authority unless the Owner explicitly configures a narrower/different non-write policy permitted by the backend.

## External MCP client relationship

The already verified ChatGPT custom MCP OAuth client remains a transport/client identity. It must not be silently converted into a human user or model provider.

F7.2D2 may surface external MCP client/grant state alongside agents for Owner visibility, but the durable conceptual separation remains:

- external MCP client = who/what connected;
- AI agent = named reasoning/execution principal;
- provider/model = how an internal agent reasons.

A later explicit binding may associate an external client with an agent policy; that binding must be visible and revocable.

## Owner-only API/control plane

Required Owner-only operations:

- list agents;
- create agent;
- read agent detail;
- rename/update identity metadata;
- update permitted policy fields;
- disable/reactivate agent;
- revoke agent;
- list sessions;
- create session;
- update session name/objective/mode;
- select/add/remove/reorder session participants;
- close/reopen session where permitted.

Non-Owner access returns authenticated `403 / Access denied`.

No AI agent may call Agent Management to change its own identity, grants, authority, lifecycle state or session policy.

## Web UI contract

Default implementation workflow is UI/UX Pro Max + MSA repo design system direct-to-code. Figma is not required unless explicitly requested by the Owner.

Add an Owner-only `AI Agent Management` surface following Dashboard v2.4.

Desktop composition:

1. page header with concise purpose and current write-boundary notice;
2. agent summary metrics;
3. agent list/cards with name, call name, runtime mode, state and capability summary;
4. create/edit agent drawer or modal;
5. multi-agent sessions section with session mode and participant chips/list;
6. session builder for selecting agents and ordering participants.

Interaction rules:

- visible labels for all fields;
- minimum ~44 px primary controls;
- keyboard accessible;
- explicit text state labels, never color-only;
- destructive/revoke actions require confirmation;
- disabled future provider/model fields explain that assignment arrives in F7.2D3/F7.2D4;
- no fake provider/model calls;
- no production inventory-write affordance;
- responsive mobile layout stacks cards/forms without page-level horizontal overflow.

## Data model

Suggested tables:

### `ai_agents`

- `agent_id uuid primary key`
- `display_name`
- `call_name`
- `description`
- `runtime_mode`
- `state`
- `capability_scopes text[]`
- `location_scope jsonb`
- `authority_ceiling`
- `execution_policy`
- `confirmation_policy`
- `created_by_user_id`
- `created_at`
- `updated_at`
- `disabled_at`
- `revoked_at`

### `ai_agent_sessions`

- `session_id uuid primary key`
- `session_name`
- `objective`
- `mode`
- `state`
- `created_by_user_id`
- `created_at`
- `updated_at`
- `closed_at`

### `ai_agent_session_participants`

- `session_id`
- `agent_id`
- `position`
- `role_label`
- `is_active`
- `joined_at`

Unique `(session_id, agent_id)`.

## Explicit non-scope

- provider API keys;
- Provider Registry implementation;
- model discovery/testing;
- model assignment/fallback execution;
- actual multi-agent inference/orchestration;
- production inventory writes;
- raw SQL/database access;
- canonical DB promotion.

## Acceptance criteria

F7.2D2 passes when:

1. Owner can create a named AI agent with stable `agent_id`;
2. case-insensitive `call_name` uniqueness is enforced;
3. agent rename preserves `agent_id`;
4. API returns deterministic self-identity context/preview from canonical agent data;
5. Owner can disable/reactivate/revoke agents;
6. non-Owner Agent Management returns 403;
7. Owner can create a multi-agent session;
8. Owner can select multiple agents, order them and assign optional role labels;
9. session membership survives restart/deploy;
10. session mode supports at least `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` as topology metadata;
11. no provider/model inference occurs;
12. no production inventory mutation occurs;
13. `database_canonical=false`, `migration_baseline_accepted=false`, and F6B test-only boundaries remain preserved.
