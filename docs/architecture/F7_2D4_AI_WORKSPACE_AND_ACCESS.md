# F7.2D4 — AI Workspace and Access-Control Architecture

Status: CANONICAL DESIGN — APPROVED 2026-08-23

## Purpose

Separate AI configuration from day-to-day AI work while keeping MSA's native internal-agent runtime independent of ChatGPT/public MCP.

The Owner-only **AI Agent Management** area remains the configuration/control plane. Actual conversations run in a separate top-level **AI Workspace** work surface.

## Product surfaces

### AI Agent Management — Owner only

Owner-only configuration includes:

- named agent create/edit/disable/revoke;
- runtime mode and authority/capability policy;
- provider registry and saved-model assignment/fallback;
- reusable multi-agent session definitions/presets;
- global non-owner AI Workspace enable/disable control;
- future workspace defaults and administrative policy.

Owner-only means both **UI restriction and backend authorization**. Hiding controls is never sufficient.

### AI Workspace — operational work surface

Top-level workspace contains:

1. **Chat** — single selected `INTERNAL_MODEL` agent; Owner plus authorized users.
2. **Multi-Agent** — `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` execution; Owner only for the current product phase.

Normal users must not see or access Multi-Agent execution. Backend endpoints for session execution must independently enforce Owner authorization even if called directly.

## Single-agent Chat UX

The Chat surface includes:

- internal-agent selector;
- new/resume conversation;
- durable conversation history;
- message thread and composer;
- selected agent identity/state;
- compact response provenance, with richer runtime details available to Owner;
- no direct provider/model choice for ordinary users.

Agent identity remains stable when provider/model assignments change.

## Multi-Agent UX

`AI Agent Management` stores reusable session definitions/presets. Actual execution occurs in `AI Workspace -> Multi-Agent`.

The workspace may expose:

- session preset selector;
- mode (`GROUP`, `COMPARE`, `REVIEW`, `DEBATE`);
- ordered participants and role labels;
- run transcript/results;
- per-agent identity/provenance;
- final synthesis where the mode requires one.

Never union participant privileges. Each agent retains its own policy and effective authority.

## AI Workspace access policy

### Owner

The Owner always retains AI Workspace access. The global staff/user switch does not disable Owner access.

### Global non-owner gate

AI Agent Management exposes an Owner-only global setting:

`AI Workspace for non-owner users: ENABLED | DISABLED`

When disabled:

- all non-owner AI Chat requests are denied before provider invocation;
- no provider API call is made;
- no model tokens/cost are consumed;
- the backend returns a deterministic access-denied response;
- Multi-Agent remains Owner-only regardless.

### Per-user entitlement

User Management stores a per-user Chat entitlement:

- `INHERIT`
- `ALLOW`
- `BLOCK`

Current effective rule:

1. Owner -> allow.
2. Non-owner + global gate disabled -> deny.
3. Non-owner + global gate enabled + per-user `BLOCK` -> deny.
4. Non-owner + global gate enabled + `INHERIT` or `ALLOW` -> eligible to continue.

The global OFF state is a hard kill switch for all non-owner users; per-user `ALLOW` does not override it.

Future allowed-agent selection may further restrict which agents a user can select.

## Backend-first authorization

Every AI Workspace request must authorize before provider invocation.

Canonical order:

`authenticated user -> Owner bypass or global gate -> per-user entitlement -> selected-agent eligibility -> later user/agent/location/tool authority intersection -> provider/runtime invocation`

A denied request must terminate before calling the provider.

UI visibility/disabled state is convenience only. Backend authorization is authoritative.

## Future typed-tool authority

When native typed tools are attached, effective permission must never come from agent policy alone. It is bounded by the intersection of relevant constraints, including:

- system gate;
- authenticated human/user authority;
- selected agent capability and authority ceiling;
- location scope;
- operation class and confirmation policy.

Provider/model choice never grants or expands authority.

## Navigation contract

Preferred product navigation:

- Dashboard / operational areas
- **AI Workspace**
  - Chat
  - Multi-Agent (Owner only)
- Audit
- Settings / management
  - **AI Agent Management** (Owner only)

The exact visual navigation may evolve, but configuration and operational chat must remain separate surfaces.

## Implementation order

1. AI Workspace access-policy foundation: global gate + per-user entitlement + backend Owner enforcement.
2. Durable conversation/message persistence.
3. Top-level AI Workspace shell with Chat tab and internal-agent selector.
4. Native runtime hookup using the existing MCP-independent invocation service.
5. Clear access-denial UX with zero provider call on denied requests.
6. Owner-only Multi-Agent workspace execution in a later D4 slice.
7. Native typed tools and user/agent/location authority intersection after the chat foundation is stable.

## Security invariants

- AI Agent Management is Owner-only in both frontend and backend.
- Multi-Agent execution is Owner-only in both frontend and backend during this phase.
- Ordinary user Chat requires global + per-user eligibility.
- Denied users never trigger provider calls.
- Internal agents never depend on public MCP for ordinary operation.
- No production inventory write authority is enabled by AI Workspace access.
