# F7.3 — Actor-Aware Audit & Operation Ledger Architecture

Status: **approved architecture direction; implementation follows F7.2A/B/C/D**

## Purpose

Medicine Store Assistant will be operated by humans, AI agents, integrations, and system jobs across Web, Telegram, Flutter, Custom GPT, internal AI Assistant, and future clients. Operational history must answer not only *what changed*, but also *who or what initiated it, through which client, under whose authority, at which location, and with what result*.

The Audit surface is reserved for store/database operational history. `User Management`, `AI Agent Management`, and global `Settings` are separate product/control-plane surfaces.

## Canonical actor model

Actor types:

- `HUMAN` — canonical human account with stable `user_id`.
- `AI_AGENT` — Owner-registered named AI/service principal with stable `agent_id`.
- `SYSTEM` — scheduled/background system process.
- `INTEGRATION` — non-AI external service principal when applicable.

Human identity and AI identity are distinct. An AI action may carry `authorized_by_user_id` when requested under a signed-in human's authority. Autonomous/scheduled AI action instead carries a reference to the Owner-configured agent/policy authority that permitted it.

## Operation provenance

Representative audit fields:

- `operation_id` — stable UUID for the logical operation;
- `idempotency_key` where applicable;
- `actor_type`;
- `actor_id` — `user_id`, `agent_id`, system principal, or integration principal;
- `authorized_by_user_id` when delegated by a human;
- configured authority/policy reference for autonomous execution;
- `client_source` — `WEB`, `TELEGRAM`, `FLUTTER`, `CUSTOM_GPT`, `INTERNAL_AI`, `SYSTEM_JOB`, or future registered client;
- `action_type` — registered typed domain operation, never free-form SQL;
- store/location scope and target where relevant;
- reconciliation classification such as `SAFE`, `REVIEW`, `CONFLICT`, or `NEW_UNMAPPED` where relevant to an evidence-matching workflow;
- target/affected-record references;
- safe request/operation metadata;
- `started_at`, `committed_at` / `completed_at`;
- `outcome` — success/failure/rejected/reversed as appropriate;
- authorization/validation/review result reference;
- relevant before/after state references or immutable ledger movements;
- reversal/correction linkage;
- read-back verification result;
- Sheet sync/mirror result references when synchronization is part of the operation.

Secrets, plaintext passwords, bearer tokens, session cookies, private credentials, and unrestricted prompt transcripts must never be stored in the operational audit ledger.

## Human + AI collaboration rule

AI execution uses the same controlled backend boundary as every other client:

`Human/agent request -> authenticated identity -> typed operation -> RBAC/delegation + agent capability/location check -> validation/reconciliation policy -> idempotency -> atomic transaction -> audit -> committed-state readback -> sync/result`

For delegated AI action:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

This makes it possible to distinguish:

- a Staff member acting directly through Web;
- the same Staff member asking AI Chat to perform an allowed read or later typed operation;
- an Owner asking an agent to operate on Main Store inside an explicitly granted capability;
- a Custom GPT acting under delegated Owner authority;
- an autonomous Owner-configured scheduled agent;
- a backend synchronization job.

AI agents are never invisible superusers and cannot self-escalate through Agent Management or Settings.

## MSA reconciliation/approval parity

Audit must support the established evidence-driven MSA workflow when those operations migrate to typed DB commands:

- `SAFE` — strong match/evidence compatibility; may be eligible for low-friction execution when that workflow class is Owner-preauthorized;
- `REVIEW` — material uncertainty; human review required before identity-sensitive mutation;
- `CONFLICT` — incompatible/recycled/contradictory evidence; automatic propagation blocked;
- `NEW_UNMAPPED` — creation/mapping decision required.

Owner preauthorization may remove repetitive per-row confirmation for a narrow SAFE workflow, but it never removes backend validation, capability/location enforcement, idempotency, audit, or read-back verification.

## Audit UI

The Audit product surface should support filtering/drill-down by:

- date/time range;
- human user;
- AI agent/service principal;
- delegated human authority;
- autonomous policy source;
- client/source;
- operation type;
- Main/Sub Store location;
- product/lot/target;
- reconciliation classification where relevant;
- success/failure/reversal state;
- operation ID.

Representative detail view should show operation summary, actor/delegation, source client, location, timestamps, safe typed inputs, validation/review result, affected records, before/after or ledger movements, read-back result, linked reversal/correction, and Sheet sync/mirror status where relevant.

## Immutability and correction semantics

Inventory/ledger history is not corrected by silently overwriting or physically deleting committed history. Corrections use typed reversal/correction operations that create new linked records.

Administrative metadata may be mutable where the domain permits it, but the audit record of that change remains append-only.

## Relationship to other slices

- **F7.2A/B/C** — canonical human identity, User Management, credentials.
- **F7.2D** — Owner-only AI Agent Management and delegated authority policy.
- **F7.3** — actor-aware operation ledger and Audit UI.
- **F7.4** — Main/Sub Store location model, settings, and user preferences.
- **F7.5–F7.8** — Calculator, analysis, AI Chat, and alerts consume the same identities/operation provenance.
- **F9+ writes** — every committed typed operation attaches complete actor/client/authority/location provenance and read-back evidence.

## Acceptance direction

Before broad AI or multi-client writes are authorized, representative test operations must prove Audit can answer:

1. What operation occurred?
2. Which human, AI agent, integration, or system initiated it?
3. If AI acted for a human, who delegated/authorized it?
4. If autonomous, which configured policy allowed it?
5. Which client/source and store/location were involved?
6. What data/records were affected?
7. What validation/review classification applied?
8. Did it succeed, fail, get rejected, or get reversed?
9. Did committed-state read-back verify the intended result?
10. What operation ID links transaction, audit, reversal, and sync evidence?
