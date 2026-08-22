# F7.2C — Credential Lifecycle Design

Status: **VERIFIED COMPLETE — 2026-08-23**

Verification anchors:

- implementation PR #40;
- merge SHA `a910658efc3cbc214b30a1f5ed946fdd34ffe4a2`;
- automatic deploy run `32589571152`;
- deploy job `97071112514` — success;
- Alembic upgraded `0006_user_management -> 0007_credential_lifecycle`;
- runtime acceptance: username change, current-password re-authentication, password change, forgotten-password enumeration safety, Owner reset review/issuance, digest-only token persistence, single-use reset, credential/session revocation, security events, and reset notifications — pass;
- public private/User Management gates remain 401 when anonymous;
- `database_canonical=false`, `migration_baseline_accepted=false`, F6B test-only status, and read-only inventory boundary preserved;
- no live workbook import and no inventory mutation occurred.

Use together with:

- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`

## Goal

Move normal username/password maintenance into the Medicine Store Assistant Web product so the Owner and staff do not need VPS, terminal, Bamboo/Bamboo Claw, or ad-hoc secure pages for routine credential changes.

F7.2C changes human sign-in credentials only. It does **not** change human roles, account state policy, inventory authority, AI-agent policy, operational Audit, store/location rules, or PostgreSQL canonicality.

## Username lifecycle

The canonical stable identity remains `users.user_id`. Username is a mutable sign-in/display credential and is not the authority label.

Authenticated username change requires:

1. active canonical user session;
2. current-password re-authentication;
3. a valid new username using the existing 3–64 character username contract;
4. case-insensitive uniqueness;
5. successful atomic update;
6. `credential_version` increment;
7. revocation of prior sessions;
8. `USERNAME_CHANGED` account-security event;
9. user signs in again with the new username.

Changing the username never changes `user_id`, role, account state, or inventory authority.

The initial bootstrap username `owner` is not a permanent product identity requirement. The existing canonical Owner may replace it through this self-service flow while retaining the `OWNER` role.

## Authenticated password change

Requires:

1. active canonical user session;
2. current-password re-authentication;
3. new password satisfying the existing minimum-length contract;
4. new password differs from the existing password;
5. password stored only as a one-way hash;
6. `credential_version` increment;
7. all prior sessions revoked;
8. outstanding reset requests/tokens cancelled;
9. `PASSWORD_CHANGED` account-security event;
10. user signs in again with the new password.

## Forgotten-password request

Public request accepts only the username and always returns the same generic accepted response whether the account exists or is eligible.

For an eligible `ACTIVE` account the backend may create one durable pending reset request. The request itself grants no access and does not change the credential.

Create:

- `PASSWORD_RESET_REQUESTED` account-security event;
- reusable `PASSWORD_RESET_REQUESTED` notification event for later Web/Telegram/Flutter delivery.

No verified-email recovery is introduced in this slice.

## Owner-assisted reset issuance

Only an authenticated `OWNER` may review pending reset requests and issue a reset link.

Issuance creates a cryptographically random short-lived token. The API returns plaintext token material exactly at issuance so the Owner can deliver the link to the user, but persistent storage contains only a keyed token digest/verifier.

v1 reset lifetime: **30 minutes**, runtime-configurable only within a bounded 5–60 minute range.

The returned reset URL uses a browser fragment:

`/dashboard/login#reset=<token>`

The fragment keeps plaintext token material out of ordinary HTTP request URLs/server access logs.

Issuance creates:

- `PASSWORD_RESET_ISSUED` account-security event;
- reusable `PASSWORD_RESET_ISSUED` notification event.

Issuing a reset cannot change roles, account state, or inventory authority.

## Reset completion

Reset completion requires:

1. matching stored token digest;
2. `ISSUED` request state;
3. active target account;
4. unexpired token;
5. new password satisfying password policy and differing from the existing credential.

On success:

- password is replaced with a one-way hash;
- `credential_version` increments;
- all prior sessions are revoked;
- the used reset is marked `CONSUMED`;
- other outstanding reset requests for that user are cancelled;
- plaintext/digest verifier material is removed after the lifecycle boundary;
- `PASSWORD_RESET_COMPLETED` account-security event is recorded.

Consumed, expired, cancelled, malformed, or unknown tokens fail generically. A token is single-use.

## Product UI

Follow Dashboard v2.4 and the pinned UI/UX Pro Max guidance: visible labels, inline errors, keyboard focus, ~44 px touch targets, responsive layout, no color-only meaning, and no fake controls.

### Signed-in Account surface

All active human roles receive an `Account` surface with separate cards for:

- Change username;
- Change password.

Both forms use explicit current-password fields. Successful changes explain that existing sessions are invalidated and return the user to sign-in.

### Login page

The deployed page includes:

- `Forgot password?` entry;
- generic reset-request acknowledgement;
- reset form activated only by a valid `#reset=...` fragment supplied by the Owner-issued link.

### Owner User Management

A separate password-reset request queue exists inside User Management. It shows textual request status and permits issuance only for an eligible `PENDING` request.

After issuance, the Owner receives the one-time reset link in a copyable field with the expiry timestamp. Plaintext reset-token material is shown only at issuance and is not persisted.

## Verified runtime contract

Deployment acceptance with a temporary non-Owner account proved:

- wrong current password blocks username change — pass;
- successful username change invalidates old sessions and old username login — pass;
- new username authenticates with unchanged password — pass;
- wrong current password blocks password change — pass;
- successful password change invalidates old sessions and old password login — pass;
- forgotten-password response is enumeration-safe — pass;
- non-Owner cannot list reset requests — pass;
- Owner can see and issue a pending reset — pass;
- database stores token digest, not plaintext token — pass;
- reset completion invalidates existing sessions — pass;
- reset token reuse fails — pass;
- old password fails and reset password authenticates — pass;
- required account-security/notification events exist — pass;
- `database_canonical=false`, `migration_baseline_accepted=false`, read-only inventory boundary, and F6B test-only status remain unchanged — pass.

## Explicit non-scope

- profile-image upload/editing;
- Owner creation/promotion flow;
- AI Agent Management;
- global Settings;
- operational/store Audit implementation;
- inventory writes or AI inventory writes;
- transfers or Smart Calculator deductions;
- Telegram/Flutter stock mutation;
- Sheet mirror conversion;
- PostgreSQL canonical promotion.

## Next authorized slice

F7.2C is complete. The next authorized implementation slice is **F7.2D — AI Agent Management & delegated authority**. Do not pull F7.3 operational Audit, inventory writes, AI writes, store transfers, Calculator deductions, Telegram/Flutter stock mutation, Sheet mirror conversion, or canonical promotion into F7.2D unless a strict prerequisite is separately authorized.
