# F7.2C.1 Recovery Email 500 Fix

The recovery email verification workflow intentionally clears token digests after cancellation, consumption, or expiry so verifier material is not retained after use.

Migration `0008_email_recovery` originally declared `recovery_email_verifications.token_digest` as `NOT NULL`, while the application cleanup path sets the digest to `NULL`. If provider delivery failed, the cleanup write could violate the database constraint and mask the intended provider-facing 503 response as HTTP 500.

Migration `0009_recovery_token_cleanup` makes the digest nullable so secure cleanup and schema semantics match. Active issued verification rows still require a digest by application flow; historical cancelled/consumed/expired rows may clear it.

This fix changes no inventory authority, migration-baseline status, or canonical-data boundary.
