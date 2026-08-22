# F7.3 — Actor-Aware Audit & Operation Ledger Architecture

Status: **approved architecture direction; implementation follows F7.2A/B/C**

## Purpose

Medicine Store Assistant will be operated by both humans and AI/service actors across Web, Telegram, Flutter, Custom GPT, internal AI Assistant, scheduled jobs, and future integrations. Operational history therefore must answer not only *what changed*, but also *who or what initiated it, through which client, under whose authority, and with what result*.

The Audit surface is reserved for store/database operational history. User Management remains a separate product surface.

## Canonical actor model

Every audited operation must resolve to an actor identity and a client/source context.

Actor types:

- `HUMAN` — canonical user account with stable `user_id`.
- `AI_AGENT` — named AI/service principal such as internal MSA Assistant or Custom GPT integration.
- `SYSTEM` — scheduled/background system process.
- `INTEGRATION` — non-AI external service principal when applicable.

Human identity and AI identity are distinct. An AI action may additionally carry an `authorized_by_user_id` / delegated human authority reference when the action was requested by a signed-in user.

## Operation provenance

Representative audit fields:

- `operation_id` — stable UUID for the logical operation;
- `idempotency_key` where applicable;
- `actor_type`;
- `actor_id` — `user_id` or service/agent principal ID;
- `authorized_by_user_id` when an agent acts on behalf of a human;
- `client_source` — `WEB`, `TELEGRAM`, `FLUTTER`, `CUSTOM_GPT`, `INTERNAL_AI`, `SYSTEM_JOB`, or future registered client;
- `action_type` — typed domain operation, not free-form SQL;
- `target_type` / `target_id` where useful;
- request/operation metadata safe for audit storage;
- `started_at`, `committed_at` / `completed_at`;
- `outcome` — success/failure/rejected/reversed as appropriate;
- validation/authorization result reference;
- relevant before/after state references or immutable snapshots where appropriate;
- reversal/correction linkage;
- sync/mirror result references when Google Sheet synchronization is part of the operation.

Secrets, plaintext passwords, bearer tokens, session cookies, and unrestricted prompt transcripts must never be stored in the operational audit ledger.

## Human + AI collaboration rule

An AI system does not receive direct database credentials and does not become an invisible superuser.

AI execution path:

`Human/agent request -> authenticated client/agent principal -> typed API operation -> RBAC/delegation check -> validation -> idempotency -> DB transaction -> audit event -> readback/sync result`

This makes it possible to distinguish:

- a Staff member entering usage through Web;
- the same Staff member asking the internal AI Assistant to prepare or execute an authorized typed operation;
- an Owner invoking a Custom GPT action;
- an autonomous scheduled analysis job;
- a backend system synchronization task.

## Audit UI

The Audit product surface should support filtering and drill-down by:

- date/time range;
- human user;
- AI/service actor;
- client/source;
- operation type;
- product/lot/target;
- success/failure/reversal state;
- operation ID.

Representative detail view should show:

- operation summary;
- actor and delegated authority;
- source client;
- timestamps;
- typed inputs that are safe to expose;
- validation/result summary;
- affected records;
- before/after or ledger movement references;
- linked reversal/correction;
- Sheet sync/mirror status when relevant.

## Immutability and correction semantics

Inventory/ledger history is not edited by silently overwriting or physically deleting committed history. Corrections use typed reversal/correction operations that create new linked records.

Administrative metadata may be mutable where the domain allows it, but the audit record of the change remains append-only.

## Relationship to other slices

- **F7.2A/B/C** establishes canonical human identity, roles, sessions, User Management, and credential lifecycle.
- **F7.3** establishes the actor-aware audit/operation ledger and Audit UI.
- **F7.4 Smart Analysis** consumes deterministic database projections and may generate read-only analysis events; it must not silently mutate inventory.
- **F7.5 AI Assistant** runs as an identifiable `AI_AGENT` and uses the same typed read APIs initially.
- **F7.6 Alerts & Notifications** records system/agent provenance for generated alerts and notification delivery attempts where operationally useful.
- **F9+ writes** must attach complete actor/client provenance to every committed operation.

## Acceptance direction

Before broad AI or multi-client writes are authorized, representative test operations must prove that Audit can answer:

1. What operation occurred?
2. Which human, AI agent, integration, or system initiated it?
3. If AI acted for a human, who authorized/delegated it?
4. Which client/source was used?
5. What data/records were affected?
6. Did it succeed, fail, or get reversed?
7. What operation ID links the entire transaction/readback/sync trail?
