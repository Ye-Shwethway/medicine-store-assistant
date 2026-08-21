# F2 Schema Decisions

Status: **approved and locked 2026-08-22**

Purpose: record the minimum domain, identity, access, and correction semantics approved before PostgreSQL migrations in Slice F2. These decisions intentionally stay small and avoid speculative enterprise complexity.

## Approved v1 decisions

### 1. Opening-balance representation

Use one explicit `OPENING_BALANCE` ledger transaction per migrated pre-existing lot at initial database migration/canonicalization only.

Do **not** create a new stock-movement opening transaction every month. Monthly opening balance is a frozen/derived field in the month snapshot, carried from the prior closing state for reporting and reconciliation.

### 2. Operational lot granularity

For v1, treat **local product + expiry date** as the normal operational lot boundary.

Multiple receipts/transfers for the same product and same expiry may feed the same operational lot while every receipt line remains separately preserved with its source transfer, quantity, source price, date, catalogue context, and provenance.

Create a distinct lot when expiry differs or stronger evidence establishes a genuinely meaningful physical/identity distinction that must not be merged.

### 3. Product rename vs new identity

`product_id` is stable and `local_name` is mutable operational/display metadata.

Spelling cleanup, abbreviation changes, or preferred local naming changes do not create a new product. Create a new identity only for a clinically/operationally meaningful difference such as medicine/device, strength, formulation, size, gauge, adult/child type, or another identity-sensitive distinction. Rename history remains auditable.

### 4. Quantity storage and precision

Store canonical quantities as fixed-point decimal values using PostgreSQL `NUMERIC(18,3)`, never floating point.

Unit policy determines whether an operation must be whole-number only. Discrete units normally reject fractional quantities; future volume/weight units may allow decimals without changing the database type.

No implicit unit conversion in v1. Source/local unit mismatches require an explicit verified conversion rule before commitment.

### 5. Negative-stock policy

Normal operational writes must not silently create negative stock.

- normal staff flows that would create an invalid negative balance are blocked;
- migration/reconciliation may preserve an already-observed negative source state when required for source truth;
- privileged Owner/Admin correction may explicitly permit a temporary negative state only with reason, audit, warning, and reconciliation requirement.

Never invent receipts or rewrite history to hide a negative balance.

### 6. Historical correction policy

Use correction-safe history rather than destructive mutation.

Open month: correct committed movement through explicit reversal and replacement/corrective transaction where appropriate.

Closed month: keep the original snapshot immutable and create a linked amendment with actor, reason, effective period, and audit trail.

Migration opening errors before canonical promotion are corrected through repeatable migration reconciliation while preserving migration evidence.

Catalogue mapping corrections that do not change physical movement update/version the mapping with audit history and do not fabricate stock movement.

### 7. Minimal v1 human roles

Use four roles:

- `OWNER` — full system authority, user/admin management, high-risk approvals, canonical promotion/month-close authority.
- `ADMIN` — operational administration and approved inventory management; cannot implicitly become Owner.
- `STAFF` — routine inventory reads and approved normal operational entry; no privileged historical correction, role management, or system configuration.
- `READ_ONLY` — inventory/history/report reads only.

Use a small static permission matrix in backend policy. No arbitrary permission editor in v1.

### 8. User identity model

Use stable backend `user_id` as canonical human identity.

Core concepts include `users`, `user_roles`, `external_identities`, and authentication/session records as required by clients. Deactivate/revoke identities rather than deleting users that own historical records.

### 9. Telegram identity linkage

Telegram numeric user ID is a unique external identity linked to canonical `user_id`. Telegram username/display name is mutable metadata only.

Unknown/unlinked Telegram users receive no operational access by default.

### 10. Flutter authentication baseline

Flutter uses a native MSA account independent of Telegram:

- user-chosen login name;
- password hashed with a modern password hashing algorithm, with Argon2id preferred when credentials are implemented;
- short-lived access token plus revocable refresh/session token;
- server-side account status and role checks for protected operations.

Email/phone remain optional profile/recovery metadata in v1.

### 11. Service identities and API keys

Non-human integrations use separate service principals, not human user rows.

Examples include the private MSA Custom GPT, future Google Sheets sync, and internal adapters. Credentials are revocable and scoped. Store only hashed/verifier-safe credential material where feasible; never plaintext API keys in canonical logs or Git.

### 12. Audit actor model

Every protected domain operation resolves actor context containing at least:

- human `user_id` or service-principal ID;
- client/channel;
- operation/idempotency ID;
- timestamp;
- authorization role/scope context where useful;
- reason/approval metadata for privileged operations.

Historical attribution remains intact after an account or credential is disabled.

## Deferred beyond F2

F2 does not require OAuth/social login, MFA, password-reset email, custom role editor, SSO, multi-organization tenancy, complex teams/departments, offline Flutter credential synchronization, biometrics, or Telegram invitation UX.

## Authorization boundary

Approval of these decisions authorizes the F2 migration/schema foundation only. It does **not** authorize live inventory import, canonical database promotion, production stock writes, Custom GPT write Actions, Telegram/Flutter rollout, or Google Sheet mirror conversion.
