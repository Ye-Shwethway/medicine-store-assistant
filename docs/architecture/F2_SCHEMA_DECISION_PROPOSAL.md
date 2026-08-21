# F2 Schema Decision Proposal

Status: **proposal for user approval — not yet locked**

Purpose: resolve the minimum domain, identity, access, and correction semantics needed before creating PostgreSQL migrations in Slice F2. This proposal intentionally stays small and avoids speculative enterprise complexity.

## Proposed v1 decisions

### 1. Opening-balance representation

Use one explicit `OPENING_BALANCE` ledger transaction per migrated pre-existing lot at initial database migration/canonicalization only.

Do **not** create a new stock-movement opening transaction every month. Monthly opening balance is a frozen/derived field in the month snapshot, carried from the prior closing state for reporting and reconciliation.

Rationale: preserves a lifetime movement ledger without double-counting month transitions while still reproducing monthly opening/closing reports.

### 2. Operational lot granularity

For v1, treat **local product + expiry date** as the normal operational lot boundary, matching the existing store workflow.

Multiple receipts/transfers for the same product and same expiry may feed the same operational lot while every receipt line remains separately preserved with its source transfer, quantity, source price, date, catalogue context, and provenance.

Create a distinct lot when expiry differs or when later evidence establishes a genuinely meaningful physical/identity distinction that must not be merged.

Rationale: keeps the human model familiar and avoids needless row/lot explosion while preserving forensic receipt history.

### 3. Product rename vs new identity

`product_id` is stable and `local_name` is mutable display/operational metadata.

A harmless rename, spelling cleanup, abbreviation change, or preferred local naming change does not create a new product.

Create a new product identity only when clinically/operationally meaningful identity changes, such as different medicine/device, strength, formulation, size, gauge, adult/child type, or another existing MSA identity-sensitive distinction.

Rename/history changes must remain auditable.

### 4. Quantity storage and precision

Store canonical quantities using fixed-point decimal numeric storage (proposed PostgreSQL `NUMERIC(18,3)`) rather than floating point.

Unit policy determines whether a particular operation must be whole-number only. Discrete units such as tablets, ampoules, pairs, pieces, bottles, etc. should normally reject fractional values. Future volume/weight units may allow decimals without a schema migration.

No implicit unit conversion in v1. Source/local unit mismatches require an explicit verified conversion rule before commitment.

### 5. Negative-stock policy

Normal operational writes must not silently create negative stock.

Default policy:
- normal Staff usage/receipt flows that would create an invalid negative balance are blocked;
- reconciliation/migration may preserve an already-observed negative source state when necessary for truth preservation;
- a privileged Owner/Admin correction/override path may explicitly permit a temporary negative state only with reason, audit event, warning, and subsequent reconciliation requirement.

Never auto-correct a negative balance by inventing receipts or changing historical usage.

### 6. Historical correction policy

Use correction-safe history rather than destructive mutation.

Open month:
- incorrect committed movement is corrected through explicit reversal and replacement/corrective transaction where appropriate.

Closed month:
- original closed snapshot remains immutable;
- create a linked amendment/correction record with actor, reason, effective period, and audit trail;
- regenerated reports must be able to show original close plus approved amendment semantics.

Migration opening error before canonical promotion:
- fix through repeatable migration reconciliation/correction evidence; do not hide the original migration batch/result.

Catalogue mapping correction that did not change physical movement:
- update/version the mapping with audit history; do not fabricate a stock movement.

### 7. Minimal v1 human roles

Use four roles:

- `OWNER` — full system authority, user/admin management, high-risk approvals, canonical promotion/month-close authority.
- `ADMIN` — operational administration, staff management within policy, receipts/usage/reconciliation/approved adjustments; cannot implicitly become Owner.
- `STAFF` — normal day-to-day stock reads and approved routine operational entry; no privileged historical correction, role management, or system configuration.
- `READ_ONLY` — inventory/history/report reads only.

Start with a small static permission matrix in backend code/database policy metadata. Do not build a custom arbitrary permission editor in v1.

### 8. User identity model

Use stable backend `user_id` as canonical human identity.

Proposed core tables/concepts:
- `users`
- `user_roles`
- `external_identities`
- authentication credential/session records as required by client

Deactivate/revoke users rather than deleting identities that already own historical audit/transaction records.

### 9. Telegram identity linkage

Telegram numeric user ID is stored as a unique external identity linked to canonical `user_id`.

Telegram username/display name is mutable metadata only and never sufficient authentication identity.

The eventual bot should reject unlinked/unapproved users. Exact invitation/link UX can be implemented later without changing the core schema.

### 10. Flutter authentication baseline

Provide a native MSA account credential independent of Telegram so Flutter does not depend on Telegram availability.

Proposed v1 baseline:
- user-chosen username or login name;
- strong password hashed with a modern password hashing algorithm (Argon2id preferred at implementation time);
- short-lived access token + revocable refresh/session token;
- server-side account status/role checks on every protected operation.

Email/phone is optional profile/recovery metadata rather than mandatory identity in v1 unless the user later wants it.

A Telegram identity may link to the same backend user account.

### 11. Service identities and API keys

Non-human integrations use separate service principals, not human user rows pretending to be users.

Examples:
- private MSA Custom GPT
- future Google Sheets sync service
- Telegram backend adapter if service-to-service authentication is needed

Use revocable scoped credentials. Store only hashed/verifier-safe API credential material where feasible; never plaintext API keys in canonical database logs or Git.

Initial scopes should remain narrow, for example read-only GPT scopes before any write capability.

### 12. Audit actor model

Every protected domain operation must resolve an actor context containing at least:

- human `user_id` or service principal ID;
- client/channel (`flutter`, `telegram`, `custom_gpt`, `sheet_sync`, admin/internal);
- operation/idempotency ID;
- timestamp;
- authorization outcome/role or scope context where useful;
- reason/approval metadata for privileged operations.

Historical records retain actor attribution even after an account/service credential is disabled.

## Deferred — not required for F2

Do not block F2 on:

- OAuth/social login;
- MFA;
- password reset email service;
- fine-grained custom role editor;
- SSO;
- multi-organization tenancy;
- complex staff departments/teams;
- offline Flutter credential synchronization;
- biometric authentication;
- Telegram invitation UX details.

These can be added later without changing the stable `user_id` / external-identity / service-principal foundation.

## Approval effect

If approved, these decisions should be merged into the canonical data/access documents and `DECISIONS_AND_OPEN_QUESTIONS.md`, then Slice F2 can be explicitly authorized for migration tooling and the initial schema only. Approval does not authorize live inventory import, production stock writes, Custom GPT write Actions, or database canonical promotion.
