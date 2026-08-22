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
7. `docs/design/F7_2C_CREDENTIAL_LIFECYCLE_DESIGN.md`
8. `docs/checkpoints/F7_2C_FINAL_RECOVERY_2026-08-23.md`
9. `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
10. `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
11. task-relevant F7 architecture/design docs
12. current repository/runtime/deployment evidence

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
- Deployment status is published to GitHub issue #26 (`MSA deployment status`).
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
- F7.2B User Management and signed-in drawer profile
- F7.2C Credential Lifecycle, Account security, verified recovery email, and automated password recovery

F7.2A anchor:

- PR #36;
- merge `c3aa75d65e0bc6d1836227fe8450b0b3de5b2651`;
- deploy run `32586385336` / job `97063270146` — success;
- canonical Owner identity/session/RBAC — verified;
- `database_canonical=false`, `migration_baseline_accepted=false` preserved;
- no inventory mutation.

F7.2B anchor:

- PR #38;
- merge `e4671c75ab2ece2a6f5065a78779413ef3e9f38b`;
- deploy run `32588170791`, job `97067607202` — success;
- pending-only Request access, Owner approval/rejection, exact role assignment, non-Owner 403, Owner-account ordinary-flow guard, role-change session revocation, disable/reactivate, explicit session revoke, security/notification events, and drawer profile UI — verified;
- no inventory mutation.

F7.2C base anchor:

- PR #40;
- merge `a910658efc3cbc214b30a1f5ed946fdd34ffe4a2`;
- deploy run `32589571152`, job `97071112514` — success;
- Alembic `0006_user_management -> 0007_credential_lifecycle`;
- username/password self-service, current-password re-authentication, credential-version/session invalidation, enumeration-safe reset request, Owner fallback reset issuance, digest-only token persistence, one-use reset — verified.

F7.2C final recovery/account refinements:

- PR #43 — Recovery email moved into Account security;
- PR #44 — recovery-token cleanup/schema compatibility so provider failure no longer becomes masked HTTP 500;
- PR #45 — Resend transport compatibility: explicit application User-Agent + `Accept: application/json` after Cloudflare error 1010 blocked Python urllib default fingerprint;
- PR #46 — Forgot password can use Username or Verified recovery email; Confirm new password backend/UI support;
- PR #47 — Account JS cache-bust so Confirm new password appears reliably on Android Chrome;
- PR #48 — Request Access captures recovery email and issues pending-access email verification;
- PR #49 — runtime-contract compatibility hotfix;
- final runtime source SHA `371936e0c7088c76f692292d31318cfd972a1a46`;
- issue #26 `status=success`, deploy run `32596093790`;
- recovery-email verification via Resend — verified in production;
- automated reset email delivery — verified in production;
- username/recovery-email Forgot password modes — working;
- Request Access email field and pending verification flow — deployed;
- read-only/non-canonical boundaries preserved.

## F6B test-only snapshot

- batch ID `be13d127-5045-4284-a088-0a0b9b024d76`
- rows 1646
- SAFE 1417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7
- `migration_baseline_accepted=false`
- `database_canonical=false`

## Current human account model

### Roles

- `OWNER`
- `ADMIN`
- `STAFF`
- `READ_ONLY`

### States

- `PENDING`
- `ACTIVE`
- `DISABLED`

Stable identity is canonical UUID `user_id`.

Username is mutable. Password is one-way hashed. Recovery email is mutable and requires verification before it becomes a recovery destination.

The former password-only Owner bridge is superseded. The original bootstrap username `owner` is not permanent and may be changed from Account without changing the `OWNER` role or stable `user_id`.

## User Management — current deployed truth

User Management is Owner-only and separate from operational Audit.

- Request access creates a `PENDING` human account/request only;
- pending account receives no role/protected inventory access;
- Owner may approve as `ADMIN`, `STAFF`, or `READ_ONLY`, or reject;
- ordinary User Management cannot assign/promote/mutate the existing `OWNER` account;
- active non-Owner role changes revoke sessions;
- disable/reactivate and explicit session revocation are supported;
- account/security events and reusable notification events are persisted;
- drawer profile card shows initials fallback, canonical username, and role;
- profile-image upload/edit remains deferred.

Request Access currently asks for:

1. Display name
2. Username
3. Recovery email
4. Password
5. Confirm password

The recovery email may be verified while the account is still `PENDING`. Verification never approves the account or assigns a role. If the Owner rejects/disables the account before verification, the pending verification is not eligible to activate access.

## Account security — current deployed truth

All active human roles have an Account surface.

### Change username

Requires current password. Preserves stable `user_id`, role, and state. Increments credential version and revokes prior sessions. User signs in again with the new username.

### Change password

Requires:

- current password;
- new password;
- Confirm new password.

Mismatch is rejected in both UI and backend. Successful change replaces only the one-way hash, increments credential version, revokes sessions, and requires sign-in again.

### Recovery email

Account contains a Recovery email card with `Not set` / `Unverified` / `Verified` state.

Setting/changing the address requires current-password re-authentication plus inbox verification. A currently verified address remains active until a replacement is verified.

## Resend production recovery delivery

Dedicated sending domain:

`msamail.drthorne.uk`

Sender:

`no-reply@msamail.drthorne.uk`

Runtime variables:

- `RESEND_API_KEY`
- `MSA_RECOVERY_EMAIL_FROM`

They remain in protected VPS runtime secrets and are mapped by canonical `deploy/docker-compose.yml`. No local compose override is required.

Resend domain verification is complete. DKIM/SPF/Return-Path records are deployed under the dedicated mail subdomain. Parent-domain DMARC was intentionally not added merely for this slice because the suggested `_dmarc` record would operate at the parent-domain policy boundary.

## Forgot password — current deployed truth

The login page offers an explicit selector:

- Username
- Recovery email

Public responses remain enumeration-safe.

Recovery-email mode requires a verified recovery email associated with exactly one eligible active account. Ambiguous matches do not select an arbitrary account.

Eligible recovery automatically issues the existing short-lived single-use reset token and sends the reset link through Resend.

Owner-assisted reset issuance remains available in User Management as fallback for exceptional cases/no usable verified recovery channel/delivery failure.

Reset tokens remain cryptographically random, short-lived, single-use, and digest-only at rest. Reset URLs use:

`/dashboard/login#reset=<token>`

Successful reset changes only the password credential, increments credential version, revokes existing sessions, consumes the reset, and records security/notification events.

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

The new DB architecture must preserve the existing MSA operating model:

1. inspect issue/supply/price/source evidence;
2. reconcile against current authoritative inventory data;
3. classify as `SAFE`, `REVIEW`, `CONFLICT`, or `NEW_UNMAPPED`;
4. execute only workflow classes already authorized by Owner policy;
5. return material ambiguity/high-risk cases for human review;
6. commit through typed operations;
7. read affected state back;
8. record operation/audit provenance;
9. report success only after verification.

A narrow SAFE workflow may later run without confirmation on every obvious row when Owner has pre-authorized that workflow. REVIEW/CONFLICT/NEW_UNMAPPED and high-risk/control-plane cases remain review boundaries.

## F7.2D — AI Agent Management — NEXT

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

Agents are **not Sub-Store-only**. Future Main Store typed operations may be granted by Owner after corresponding controlled-write/canonicality slices are authorized.

For delegated action:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

## F7.3 — Actor-aware Audit / Operation Ledger

Audit is operational/store/database history, separate from User Management, AI Agent Management, and Settings.

Actor classes: `HUMAN`, `AI_AGENT`, `SYSTEM`, `INTEGRATION`.

Operations retain actor/client/authority/location/outcome/affected-record provenance, delegated `user_id` where applicable, autonomous policy reference where applicable, reconciliation class where relevant, and read-back/sync result linkage.

## Later sequence

- **F7.4** — Inventory Locations / Store Policy / Preferences: exactly one Main Store, Owner-created Sub Stores, location-aware balances, initial Main→Sub transfer semantics, Owner reorder policy, cross-client preferences.
- **F7.5** — Smart Calculator / Receipts: calculation-only first, DB-backed lookup, no Excel re-upload for normal use, future Sub Store deduction only after controlled-write authorization.
- **F7.6** — deterministic Smart Analysis.
- **F7.7** — internal read-only AI Assistant using typed backend tools.
- **F7.8** — Alerts & Notifications. Resend is already proven for credential recovery; broader email/Telegram alert delivery comes later. Telegram recovery delivery requires secure Telegram identity linking and must not create a second credential authority.
- **F8** — external/Custom GPT read-only integration through scoped/revocable agent/service identity.
- **F9** — controlled typed writes after identity/Agent Management/Audit/location/idempotency are verified.
- **F10** — real workflow + fresh migration + Sheet sync/mirror validation.
- **F11** — explicit canonical DB promotion after parity, backup/restore, location-aware workflow, AI/actor audit, sync, and rollback proof.
- Telegram/Flutter rollout reuses the same backend contracts; local Flutter cache is never a second canonical DB.

## Immediate implementation boundary

Start the next implementation chat with **F7.2D AI Agent Management & delegated authority**.

Then continue in order:

1. F7.3 actor-aware Audit
2. F7.4 Inventory Locations / Store Policy / Preferences

Do not jump ahead to production stock writes, AI inventory writes, store transfers, Smart Calculator deduction, Telegram/Flutter mutation, Sheet mirror conversion, or canonical promotion.

## New-chat readiness checklist

A fresh implementation chat is ready when it can establish all of the following from repository evidence:

- Sheet authoritative / PostgreSQL non-canonical;
- F6B test-only counts and no accepted migration baseline;
- verified F7.2A/F7.2B/F7.2C checkpoints;
- issue #26 deployment evidence path;
- User Management is Owner-only and separate from operational Audit;
- signed-in profile box behavior;
- username/password/recovery-email Account behavior;
- Confirm new password is UI + backend enforced;
- Resend recovery domain/sender and runtime-secret boundary;
- Forgot password supports username or verified email with generic public response;
- automated reset email is deployed, Owner-assisted reset remains fallback;
- Request Access captures and can verify recovery email while account remains pending;
- initial `owner` username can be replaced without changing stable `user_id` / `OWNER` role;
- next slice = F7.2D;
- F7.2D/F7.3 order;
- Owner-only AI Agent Management and Settings;
- AI may eventually operate on Main Store or Sub Stores only inside Owner-granted typed scopes;
- `$msa` SAFE/REVIEW/CONFLICT/NEW_UNMAPPED + read-back/audit workflow parity;
- no production inventory write authority yet.

If these are recovered, implementation may begin without another architecture reconciliation round.

## Continuity rule

After significant architecture, implementation, deployment, migration, design-system, or next-work changes, update `ROADMAP.md`, this file, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.
