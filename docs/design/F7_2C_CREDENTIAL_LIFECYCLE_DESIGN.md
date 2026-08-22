# F7.2C — Credential Lifecycle Design

Status: **VERIFIED COMPLETE — 2026-08-23**

F7.2C now includes the final production credential/recovery refinements deployed after the original credential-lifecycle slice: self-service username/password maintenance, password confirmation, verified recovery email, automated Resend delivery, username-or-email forgotten-password recovery, and recovery-email verification during Request Access.

## Verification anchors

Original credential lifecycle:

- PR #40, merge `a910658efc3cbc214b30a1f5ed946fdd34ffe4a2`;
- deploy run `32589571152`, job `97071112514`;
- Alembic `0006_user_management -> 0007_credential_lifecycle`.

Final recovery/account refinements:

- Account recovery-email placement and UI refinements: PR #43;
- recovery-token cleanup/schema compatibility: PR #44;
- Resend Cloudflare/urllib transport compatibility: PR #45;
- username-or-email recovery identifier + password confirmation backend/UI: PR #46;
- Account security cache-bust for Confirm new password UI: PR #47;
- Request Access recovery-email capture + pending verification: PR #48;
- runtime-contract compatibility hotfix: PR #49;
- final verified deployment source SHA `371936e0c7088c76f692292d31318cfd972a1a46`;
- deployment status issue #26 reported `status=success` for that SHA.

Throughout these refinements:

- `database_canonical=false`;
- `migration_baseline_accepted=false`;
- F6B remains test-only;
- Google Sheet remains operationally authoritative;
- no inventory import/write/mutation was authorized or executed.

Use together with:

- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`
- `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`

## Goal

Normal account and recovery maintenance must be product-native and must not require VPS, Termux, Bamboo/Bamboo Claw, or ad-hoc secure pages after runtime secrets are provisioned.

F7.2C changes human sign-in credentials and recovery channels only. It does **not** change human roles, account state policy, inventory authority, AI-agent policy, operational Audit, store/location rules, or PostgreSQL canonicality.

## Canonical identity

The stable human identity remains `users.user_id`.

Username, password, and recovery email are mutable account credentials/recovery attributes. None of them replace the stable `user_id` or confer inventory/control-plane authority.

Canonical human roles remain:

- `OWNER`
- `ADMIN`
- `STAFF`
- `READ_ONLY`

Canonical account states remain:

- `PENDING`
- `ACTIVE`
- `DISABLED`

## Username lifecycle

Authenticated username change requires:

1. active canonical user session;
2. current-password re-authentication;
3. valid 3–64 character username;
4. case-insensitive uniqueness;
5. atomic canonical update;
6. `credential_version` increment;
7. prior-session revocation;
8. `USERNAME_CHANGED` account-security event;
9. sign-in again with the new username.

Changing username never changes `user_id`, role, state, or inventory authority.

The original bootstrap username `owner` is not permanent. The canonical Owner may replace it through Account while retaining the `OWNER` role and stable `user_id`.

## Authenticated password change

Requires:

1. active canonical session;
2. current-password re-authentication;
3. new password satisfying the password policy;
4. explicit `Confirm new password` value matching the new password;
5. one-way password-hash replacement only;
6. `credential_version` increment;
7. all prior sessions revoked;
8. outstanding reset requests/tokens cancelled;
9. `PASSWORD_CHANGED` account-security event;
10. sign-in again using the new credential.

The Web Account surface performs mismatch feedback near the field, and the backend confirmed-password endpoint also rejects mismatches so the check cannot be bypassed by browser manipulation.

## Recovery email lifecycle

All active human accounts have an Account → Recovery email card.

Setting/changing a recovery email requires:

1. authenticated active session;
2. current-password re-authentication;
3. valid email syntax;
4. short-lived verification token;
5. token digest/verifier only at rest;
6. Resend delivery through the verified MSA sending domain;
7. inbox verification before the address becomes an active recovery destination.

When changing an already verified address, the existing verified recovery email remains active until the replacement address is verified.

Verification tokens are short-lived and single-use. Consumed/cancelled tokens have verifier material cleared.

## Resend delivery

Production email delivery uses Resend with dedicated sending domain:

`msamail.drthorne.uk`

Current sender address:

`no-reply@msamail.drthorne.uk`

Runtime secrets remain outside Git in the protected VPS runtime environment:

- `RESEND_API_KEY`
- `MSA_RECOVERY_EMAIL_FROM`

Canonical `deploy/docker-compose.yml` maps these environment variables into the API container; no local compose override is required.

The sending domain is verified in Resend/Cloudflare. DKIM/SPF/Return-Path DNS records are deployed under the dedicated mail subdomain. Parent-domain DMARC was intentionally not added merely for this slice because the Resend-suggested `_dmarc` record would apply at the parent-domain policy boundary.

The Resend HTTP helper uses an explicit application `User-Agent` and `Accept: application/json`. This was required because Cloudflare in front of Resend rejected the default `Python-urllib/3.12` request fingerprint with Cloudflare error 1010 while equivalent curl/normal-client requests succeeded.

## Forgotten-password request

The public Forgot password flow supports two explicit identifier modes:

- Username
- Verified recovery email

The public response remains enumeration-safe regardless of whether the supplied identifier exists or is eligible.

Email-mode recovery resolves only a verified recovery address associated with exactly one eligible active account. Ambiguous shared-address matches do not select an arbitrary user.

For an eligible account with verified recovery email and configured email delivery, the backend may automatically issue the existing short-lived single-use reset lifecycle and send the reset link through Resend.

The reset request itself never grants access or changes roles/account state.

## Owner-assisted fallback

Owner-assisted reset issuance remains available in User Management as a fallback for exceptional cases, users without a usable verified recovery channel, or delivery failures.

Only authenticated `OWNER` may review/issue those fallback links.

Plaintext reset token material is shown only at issuance. Persistent reset storage retains keyed digest/verifier material only.

## Reset link and completion

Reset URLs use a browser fragment:

`/dashboard/login#reset=<token>`

This keeps plaintext token material out of ordinary HTTP request URLs/server access logs.

Reset completion requires:

1. matching stored token digest;
2. `ISSUED` request state;
3. active target account;
4. unexpired token;
5. valid new password distinct from the existing credential.

On success:

- password hash is replaced;
- `credential_version` increments;
- prior sessions are revoked;
- reset becomes `CONSUMED`;
- outstanding sibling resets are cancelled;
- verifier material is removed at the lifecycle boundary;
- security/notification events are recorded.

Consumed, expired, cancelled, malformed, reused, or unknown tokens fail generically.

## Request Access email verification

The public Request Access form now collects:

- Display name
- Username
- Recovery email
- Password
- Confirm password

A successful new request creates only a `PENDING` human account/request. It does **not** assign a role or grant protected access.

The supplied email is stored as an unverified recovery address and a verification message is sent immediately when delivery is configured.

Pending-access verification uses a dedicated fragment and endpoint:

`/dashboard/login#verify-access-email=<token>`

Verification may complete while the user is still `PENDING`. It only marks the recovery email verified; it does not approve the access request.

If Owner approval happens before the user opens the verification link, the same valid link may still complete for the now-`ACTIVE` account. If the request is rejected/disabled before verification, the link is no longer eligible.

If email delivery fails after a request is created, the request remains pending and the address remains unverified; after approval the user may verify/change the address from Account security.

## Product UI

All credential/recovery UI follows Dashboard v2.4 and the pinned UI/UX Pro Max guidance:

- visible labels;
- inline errors near the affected field;
- keyboard focus support;
- approximately 44 px minimum touch targets;
- responsive mobile/desktop layout;
- no color-only status meaning;
- no fake controls.

### Signed-in Account surface

All active human roles receive an Account surface containing:

- Change username;
- Change password;
- Recovery email.

Change password includes Current password, New password, and Confirm new password.

Recovery email shows explicit `Not set` / `Unverified` / `Verified` state and supports replacement without dropping the existing verified address prematurely.

### Login page

The deployed login experience includes:

- Sign in;
- Request access;
- Forgot password;
- username/recovery-email recovery selector;
- recovery-email verification completion;
- pending-access email verification completion;
- one-time password-reset completion.

### Owner User Management

User Management remains Owner-only and separate from operational Audit. It provides human account approval/rejection/role/state/session management plus fallback reset review/issuance.

## Security/event invariants

- public recovery responses do not reveal account existence;
- email verification never grants a role or protected access;
- password/recovery tokens are cryptographically random, short-lived, single-use, and digest-only at rest;
- account credentials never enter Git/browser storage/logs;
- Resend receives only the minimum delivery payload;
- provider/API failure never weakens account-state or authorization policy;
- account/security events remain separate from later operational/store Audit;
- session revocation follows credential-version changes;
- AI/inventory authority is unaffected by this slice.

## Verified production result

Production/user acceptance established:

- Owner username change through Account — pass;
- Account password-change confirmation field visible and backend-enforced — pass;
- recovery email verification through Resend — pass;
- verified email displayed as active recovery destination — pass;
- Forgot password by username — pass;
- Forgot password by verified recovery email — pass;
- Resend direct diagnostic — HTTP 200 and delivered message;
- in-app Resend transport after User-Agent fix — functional;
- automated reset email delivery — functional;
- recovery-email provider failures surface without the prior DB cleanup 500 masking bug;
- Request Access now captures email and deploy/runtime validation is green;
- final deployment issue #26 source SHA `371936e0c7088c76f692292d31318cfd972a1a46` — success;
- health/readiness remain green;
- inventory remained read-only/non-canonical.

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

Telegram recovery delivery remains a future channel after Telegram identity linking exists. It must reuse the same canonical `user_id`, recovery policy, token/security lifecycle, and notification-event model rather than inventing a second credential authority.

## Next authorized slice

F7.2C is complete. The next authorized implementation slice is **F7.2D — AI Agent Management & delegated authority**.

Do not pull F7.3 operational Audit, production inventory writes, AI writes, store transfers, Calculator deductions, Telegram/Flutter stock mutation, Sheet mirror conversion, or canonical promotion into F7.2D unless a strict prerequisite is separately authorized.
