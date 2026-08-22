# F7.2C Final Recovery Checkpoint — 2026-08-23

Status: **VERIFIED PRODUCTION CHECKPOINT**

This checkpoint records the final credential/recovery refinements completed after the original F7.2C implementation.

## Production result

Final runtime source SHA:

`371936e0c7088c76f692292d31318cfd972a1a46`

GitHub issue #26 reported:

- `status=success`
- workflow run `32596093790`
- publisher `deploy-f5.yml`

## Final human-account behavior

- canonical stable identity remains `user_id`;
- username can be changed from Account after current-password re-authentication;
- password can be changed from Account with Current password + New password + Confirm new password;
- password confirmation is checked in both UI and backend;
- credential changes revoke prior sessions through credential-version/session semantics;
- recovery email is managed from Account and becomes active only after inbox verification;
- current verified recovery email remains active until a replacement is verified;
- Forgot password supports Username or Verified recovery email;
- public recovery responses remain enumeration-safe;
- automated reset delivery uses Resend;
- Owner-assisted reset issuance remains as fallback;
- Request Access collects Display name, Username, Recovery email, Password, Confirm password;
- Request Access email can be verified while account state remains `PENDING`;
- pending email verification never grants a role or protected dashboard access;
- Owner approval/rejection remains the sole ordinary access decision.

## Resend runtime

Dedicated sending domain:

`msamail.drthorne.uk`

Sender:

`no-reply@msamail.drthorne.uk`

Runtime variables are stored only in the protected VPS environment and mapped by canonical `deploy/docker-compose.yml`:

- `RESEND_API_KEY`
- `MSA_RECOVERY_EMAIL_FROM`

A temporary local compose override used during secret provisioning was removed after the canonical compose mapping was confirmed.

The Resend delivery helper uses explicit `Accept: application/json` and an application User-Agent because Resend's Cloudflare edge rejected Python urllib's default fingerprint with Cloudflare error 1010.

## Bug fixes closed during finalization

- recovery-email card moved into the Account security surface;
- recovery-token cleanup/schema nullability mismatch that masked provider failures as HTTP 500;
- Resend Cloudflare 1010 transport incompatibility;
- password confirmation missing from Account UI;
- stale Account JS asset cache on Android Chrome;
- Forgot password confusion between username and recovery email;
- runtime validation compatibility after Request Access began requiring email.

## Authority boundary unchanged

- Google Sheet remains operationally authoritative;
- PostgreSQL remains non-canonical;
- F6B remains test-only;
- `database_canonical=false`;
- `migration_baseline_accepted=false`;
- no production inventory writes;
- no AI inventory writes;
- no transfers/Calculator deductions;
- no Telegram/Flutter stock mutation;
- no Sheet mirror conversion;
- no canonical DB promotion.

## Next

F7.2C is closed. The next authorized implementation slice remains:

**F7.2D — AI Agent Management & delegated authority**

Do not pull F7.3 operational Audit or later write-capable inventory work into F7.2D unless separately authorized as a strict prerequisite.
