# F7.2D — AI Agent Management & Delegated Authority

Status: **approved architecture direction; implement after F7.2A/B/C and before broad AI writes**

## Purpose

Medicine Store Assistant already behaves as an evidence-driven operational assistant: it reads source documents, reconciles them against inventory truth, classifies confidence, performs low-friction routine writes when the Owner has already authorized that class of work, surfaces ambiguous cases for review, verifies committed writes by read-back, and records significant reconciliation/audit evidence.

The database architecture must preserve that operating model while adding durable identity, multi-user control, deterministic validation, actor-aware audit, location-aware stock, and safer AI execution.

AI Agent Management is therefore a separate **Owner-only control plane** for configuring named AI/service principals. AI agents are not ordinary human accounts and do not inherit unrestricted Owner power merely because the Owner invokes them.

## Canonical principal model

AI agents use `AI_AGENT` principals distinct from human `user_id` accounts.

Representative fields/configuration:

- stable `agent_id`;
- display name and agent type/provider metadata;
- `ACTIVE` / `DISABLED` state;
- allowed typed capabilities;
- allowed store/location scope;
- authority ceiling;
- execution mode;
- delegation rules;
- write-confirmation policy;
- revocable client/service credential where applicable;
- created/updated/disabled audit provenance.

Human roles remain `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`. AI agents do not receive those roles as if they were staff accounts. Instead, their executable authority is capability-based.

## Owner-only control plane

Only `OWNER` may:

- create/register an AI agent principal;
- enable/disable/revoke an AI agent;
- grant/remove agent capabilities;
- change agent store/location scope;
- change authority ceiling or execution mode;
- decide whether writes require explicit confirmation;
- allow or revoke autonomous execution within a pre-authorized scope;
- grant access to Main Store operations;
- grant access to selected/all Sub Stores;
- configure which human roles/users may use a shared AI feature such as AI Chat;
- change global Settings that affect reorder policy, store policy, or agent-control policy.

`AI Agent Management` and global `Settings` are Owner-only product surfaces. An AI agent may never modify its own capability grant, authority ceiling, control-plane policy, Owner/security configuration, or the Agent Management configuration of another agent.

## Location scope

AI agents are not limited to Sub Stores.

The Owner may grant:

- Main Store read access;
- Main Store typed write capabilities when the corresponding production-write slice is authorized;
- selected Sub Store access;
- all active Sub Store access;
- all-store analytical reads.

Examples of future Main Store capabilities may include typed operations for CMS price updates, approved batch intake/reconciliation, receiving, metadata correction, or other Owner-authorized workflows. These are allowed only through registered typed operations and the current canonicality/write policy.

## Effective authority rule

When an agent acts for a signed-in human:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

Therefore:

- an Owner can use a powerful agent without turning it into an unrestricted superuser;
- a Staff user cannot use AI Chat to bypass Staff permissions;
- an agent configured for Main Store price reconciliation cannot silently gain user-management or Settings authority;
- an agent configured for read-only analysis cannot commit stock operations.

When an autonomous/scheduled agent acts without a live human request, it uses only the Owner-configured autonomous policy bound to that agent principal. The audit trail records the configured authority source rather than inventing a human delegate.

## MSA skill workflow parity

The existing MSA operating model is preserved conceptually:

1. inspect source evidence;
2. reconcile against current authoritative data;
3. classify identity/confidence;
4. execute only within the Owner-authorized operation scope;
5. surface ambiguity instead of guessing;
6. commit through typed backend operations;
7. read back committed state;
8. record operation/audit provenance;
9. report success only after verification.

Canonical reconciliation classes may retain the established concepts:

- `SAFE` — strong identity/evidence compatibility;
- `REVIEW` — meaningful uncertainty requiring human review before identity-sensitive mutation;
- `CONFLICT` — incompatible/recycled/contradictory evidence; automatic propagation blocked;
- `NEW_UNMAPPED` — no acceptable existing match; creation/mapping requires explicit workflow.

UI may render these classes with green/yellow/red-style status treatment, but color is presentation only; the stored classification is explicit text/state.

## Pre-authorized vs review-required execution

Owner authorization does not mean every routine operation must ask for a fresh Yes/No confirmation.

### Pre-authorized routine scope

The Owner may configure a narrow, deterministic workflow class that the agent may execute without per-row confirmation when all required conditions pass.

Example direction:

- SAFE CMS price synchronization for strongly reconciled items;
- approved metadata updates within an allowlisted field set;
- another low-risk typed operation after its production-write slice is authorized.

Such execution must still pass backend validation, capability/location checks, idempotency, transaction controls, audit, and read-back verification.

### Review-required scope

Human review/approval is required when the operation is outside the pre-authorized policy or carries material ambiguity/risk, including representative `REVIEW`, `CONFLICT`, `NEW_UNMAPPED`, identity-changing, destructive-looking, high-impact, or security/control-plane changes.

The Owner may edit the proposed resolution before authorizing commit.

## Shared AI Chat

`AI Chat` / Internal AI Assistant is a normal operational feature, not the Agent Management control plane.

The Owner may grant Staff/Admin users access to AI Chat. When they use it:

- the signed-in human identity remains the delegation context;
- the AI principal remains separately identifiable;
- effective authority is the intersection rule above;
- location and feature permissions are respected;
- audit can distinguish a direct human action from an AI-assisted action.

Read-only AI Chat is introduced before write tools. Future AI write tools require the same typed operation, confirmation/policy, idempotency, audit, and read-back guarantees as any other client.

## Canonicality boundary

At the current checkpoint Google Sheets remains operationally authoritative and PostgreSQL is non-canonical.

This document defines the future execution contract; it does not authorize production DB writes now.

After explicit canonical promotion, PostgreSQL may become the operational source of truth for the approved scope. At that point AI agents may perform Main Store or Sub Store writes only where the Owner has granted capability/location authority and the typed write path is explicitly authorized.

## Audit requirements

Every meaningful AI operation should allow Audit to answer:

- which `agent_id` acted;
- whether it acted autonomously or for a human;
- `authorized_by_user_id` when delegated by a human;
- client/source (Web AI Chat, Custom GPT, Telegram, Flutter, system job, etc.);
- capability/action invoked;
- location scope/target;
- reconciliation classification where relevant;
- validation/approval result;
- affected records;
- transaction/read-back outcome;
- reversal/correction relationship if later corrected.

## Implementation dependency

Recommended order:

1. F7.2A canonical human identity/sessions;
2. F7.2B User Management;
3. F7.2C credential lifecycle;
4. F7.2D AI Agent Management principal/control-plane foundation;
5. F7.3 actor-aware Audit / operation ledger;
6. later read-only AI Assistant and external agent integrations;
7. write capabilities only through F9+ controlled typed-write authorization.
