# Medicine Store Assistant — New Chat Bootstrap

Use this file for project-development continuity and memory reconciliation in a fresh chat.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Mandatory reconciliation order

Before changing code/config/schema/runtime in a fresh chat, read and reconcile in this order:

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `IMPLEMENTATION_PLAN.md`
5. `docs/architecture/README.md`
6. `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
7. `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
8. `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
9. task-relevant F7 architecture/design docs
10. current repository/runtime/deployment evidence

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Current authority boundary

The live Google workbook/source documents remain operationally authoritative. PostgreSQL is deployed but **not canonical**.

The current F6B staged dataset remains **test-only** and is not an accepted migration baseline.

No production inventory write, DB promotion, Telegram/Flutter stock mutation, Sheet mirror conversion, or Custom GPT/AI write Action is authorized merely by this bootstrap.

## Delivery / owner-interaction policy

Canonical flow: `test -> pull request -> main -> automatic VPS deployment for relevant runtime changes`.

- Do not require the Owner to use Termux, SSH, tmux, shell commands, Bamboo/Bamboo Claw, or manual GitHub Actions for normal continuation.
- Prefer connected tools, repository automation, repo-scoped self-hosted runner `msa-vps-runner-01`, and durable browser/admin mechanisms.
- Runtime secrets stay on the VPS.
- Normal backend deploy does not read/import the live workbook.
- Deployment status is published to GitHub issue #26 (`MSA deployment status`) so connected tooling can inspect source SHA/run/job evidence directly.
- Dashboard deployment verification checks localhost and `https://inventory.drthorne.uk`.

## Verified checkpoints

Verified complete:

- F0 VPS inspection
- F1 runtime skeleton
- Cloudflare public HTTPS route
- F2 PostgreSQL foundation
- F3 authenticated read-only API
- F4 synthetic ledger foundation
- F5 CMS catalogue versioning
- F5.1 authenticated catalogue read API
- F6A synthetic shadow migration adapter
- F6C authenticated shadow read API
- F7.1 read-only Web Dashboard foundation
- F7.2A canonical multi-user identity and sessions

F7.2A verification anchor:

- implementation PR #36;
- merge SHA `c3aa75d65e0bc6d1836227fe8450b0b3de5b2651`;
- automatic deploy run `32586385336` / job `97063270146` — success;
- Alembic upgraded `0004_shadow -> 0005_identity`;
- canonical Owner bootstrap resolved stable `user_id` and username `owner` without plaintext credential exposure;
- username + password authentication — pass;
- DB-bound durable/revocable session — pass;
- backend Owner RBAC — pass;
- explicit authenticated `403 / Access denied` — pass;
- disabled-user protected-access denial — pass;
- public dashboard private gate — 401 when anonymous;
- `database_canonical=false` and `migration_baseline_accepted=false` preserved;
- no live workbook import and no inventory mutation occurred.

F6B remains test-only:

- batch ID `be13d127-5045-4284-a088-0a0b9b024d76`
- rows 1646
- SAFE 1417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7
- `migration_baseline_accepted=false`
- `database_canonical=false`

The former password-only Owner bridge is superseded by the canonical F7.2A human account/session model. The existing password hash was reused as bootstrap evidence; plaintext credentials were never written to Git or logs.

## Product direction

MSA is a multi-client intelligent store-operations platform.

Humans, AI agents, integrations, and system jobs will collaborate through the same typed backend across Web, Telegram, Flutter, internal AI, Custom GPT, and scheduled jobs.

Preserve these invariants:

- canonical human identity;
- separately managed AI/service principals;
- backend-enforced RBAC, delegation, capability, and location scope;
- deterministic database/business truth;
- actor-aware operation provenance;
- no arbitrary SQL/client DB credentials;
- no AI claim of successful mutation before committed-state read-back;
- no silent replacement of source-document truth with AI assumptions.

## Existing `$msa` workflow parity

The new DB architecture must preserve the useful existing MSA workflow:

1. inspect issue/supply/price/source evidence;
2. reconcile against current authoritative inventory data;
3. classify identity/confidence as `SAFE`, `REVIEW`, `CONFLICT`, or `NEW_UNMAPPED`;
4. execute only workflow classes already authorized by Owner policy;
5. return material ambiguity/high-risk cases for human review rather than guessing;
6. commit through typed operations;
7. read affected state back;
8. record operation/audit provenance;
9. report success only after verification.

A narrow SAFE workflow may later run without asking for confirmation on every obvious row when the Owner has pre-authorized that workflow. REVIEW/CONFLICT/NEW_UNMAPPED and high-risk/control-plane cases remain review boundaries.

## Current management/control-plane direction

### Human roles

- `OWNER`
- `ADMIN`
- `STAFF`
- `READ_ONLY`

### Human states

- `PENDING`
- `ACTIVE`
- `DISABLED`

### F7.2A — Canonical human identity — **VERIFIED COMPLETE**

Current deployed model:

- stable canonical UUID `user_id`;
- username + password login;
- one canonical role per user from the approved role set;
- canonical account states above;
- opaque DB-bound sessions stored as server-side token digests with expiry/revocation/credential-version binding;
- backend role-policy helpers;
- authenticated 403 behavior;
- disabled users fail protected-session resolution;
- inventory remains read-only.

### F7.2B — User Management — **NEXT**

Separate human-account surface for pending access requests, Owner approval/rejection, allowed role assignment, disable/reactivate/revoke, and security events. ADMIN cannot grant/promote OWNER.

F7.2B must reuse F7.2A canonical `user_id`, roles, states, sessions, and backend authorization. It must not introduce credential lifecycle, AI Agent Management, operational Audit UI, inventory writes, or canonical DB promotion.

### F7.2C — Credential lifecycle

Change password, Owner-assisted forgotten-password reset v1, short-lived single-use reset, and session revocation after reset/disable.

### F7.2D — AI Agent Management

Dedicated **Owner-only** control plane for named `AI_AGENT` principals.

Owner configures:

- typed capabilities;
- Main Store / selected Sub Stores / all-store scope;
- authority ceiling;
- delegated vs autonomous policy;
- read-only / propose-only / confirm-before-write / autonomous-within-preauthorized-scope behavior;
- active/disabled/revoked state;
- which human users/roles may use shared AI features such as AI Chat.

AI agents are not ordinary human accounts and cannot self-escalate. `AI Agent Management` and global `Settings` are Owner-only.

Agents are **not Sub-Store-only**. Future Main Store typed operations may be granted by Owner after the corresponding controlled-write/canonicality slices are authorized.

For a delegated AI action:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

### F7.3 — Actor-aware Audit / Operation Ledger

Audit is operational/store/database history, separate from User Management, AI Agent Management, and Settings.

Actor classes: `HUMAN`, `AI_AGENT`, `SYSTEM`, `INTEGRATION`.

Operations retain actor/client/authority/location/outcome/affected-record provenance, delegated `user_id` where applicable, autonomous policy reference where applicable, reconciliation class where relevant, and read-back/sync result linkage.

## Store / product direction after identity + audit

### F7.4 — Inventory Locations, Store Policy & Preferences

- exactly one Main Store;
- Owner may create unlimited Sub Stores;
- product/lot balances are location-aware;
- initial transfer direction Main -> selected Sub Store;
- current `Daily Usage` is future Stock Transfer evidence where source truth supports it;
- Owner-only reorder policy: `MAIN_STORE_ONLY` initially/default or `TOTAL_ACTIVE_STOCK`;
- cross-client preferences include default Calculator Sub Store, card/table view, columns, filters, and receipt/calculator defaults.

### F7.5 — Smart Calculator / Receipts

Calculation-only first. DB-backed item/lot/location search, no separate Excel upload/mapping, same-name disambiguation, quantity/price, multiple items, fees, receiver/issuer/note, saved calculations, receipt history, print/PDF/export/share.

Future Sub Store stock deduction is a later typed write.

### F7.6 — Smart Analysis

Deterministic professional charts/KPIs for Stock Health, Transfer/Usage Trends, Expiry Risk, Reorder Outlook, Price Movement, and Data Quality.

### F7.7 — Internal AI Assistant

Read-only first. Owner may enable AI Chat for Staff/Admin users, but effective authority remains bounded by human role + agent capability + location + operation policy.

### F7.8 — Alerts & Notifications

Deterministic events first, optional AI explanation second, reusable across Web/Telegram/Flutter.

## Later sequence

- **F8** — external/Custom GPT read-only integration using Owner-managed agent/service identity.
- **F9** — controlled typed writes after identity/Agent Management/Audit/location/idempotency are verified. Future AI Main Store writes and Sub Store writes are possible only inside Owner-granted scopes.
- **F10** — real workflow + fresh migration + Google Sheet sync/mirror validation. Validate the existing `$msa` reconciliation/approval/read-back behavior against typed DB operations.
- **F11** — explicit canonical DB promotion after parity, backup/restore, location-aware workflow, AI/actor audit, sync, and rollback proof.
- Telegram/Flutter rollout reuses the same backend contracts; Flutter cache is never a second canonical DB.

## Immediate implementation boundary

Start the next implementation chat with **F7.2B User Management**.

Then continue in order:

1. F7.2C credential lifecycle
2. F7.2D AI Agent Management
3. F7.3 actor-aware Audit

Do not jump ahead to production stock writes, AI writes, store transfers, Smart Calculator deduction, Telegram/Flutter mutation, or canonical promotion.

## New-chat readiness checklist

A fresh implementation chat is ready when it can establish all of the following from repository evidence without remembered chat context:

- current SOT boundary: Sheet authoritative, PostgreSQL non-canonical;
- verified F7.2A canonical identity/session checkpoint and PR #36/deploy #32586385336 evidence;
- test-only F6B status and counts;
- delivery policy and issue #26 deployment evidence path;
- next slice = F7.2B;
- F7.2C/D and F7.3 order;
- Owner-only AI Agent Management and Settings;
- AI may eventually operate on Main Store or Sub Stores only inside Owner-granted typed scopes;
- `$msa` SAFE/REVIEW/CONFLICT/NEW_UNMAPPED + read-back/audit workflow parity;
- no production inventory write authority yet.

If these are all recovered, implementation may begin without another architecture reconciliation round.

## Continuity rule

After significant architecture, implementation, deployment, migration, design-system, or next-work changes, update `ROADMAP.md`, this file, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.
