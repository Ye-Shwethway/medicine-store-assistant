# F7.2 — Dedicated Login + Shadow Data Diagnostic

Status: implementation slice authorized 2026-08-22.

## User evidence

Public dashboard access and Owner sign-in were confirmed from a mobile browser. After sign-in, the dashboard reported an active Owner session but overview metrics and attention data remained blank.

The screenshot alone cannot distinguish between an absent test-only shadow batch and a dashboard BFF read error because the current JavaScript leaves the visible cards blank in both cases.

## This slice

- add a dedicated `/dashboard/login` page;
- redirect unauthenticated `/dashboard` visits to the dedicated login page;
- redirect already-authenticated login-page visits back to `/dashboard`;
- preserve the existing secure HttpOnly session cookie and read-only boundary;
- use the normal `test -> PR -> main -> automatic VPS deploy` flow;
- rely on the existing deployment-time `app.shadow_read_verify` check to confirm whether the F6B/F6C test-only shadow batch still exists and reconciles.

If deployment-time shadow verification passes, the test rows were not deleted and remaining blank-dashboard behavior is a dashboard BFF/UI issue to fix next. If it fails with `no test-only Google Sheet shadow batch found`, recovery of the test-only dataset must be handled explicitly and must not be conflated with canonical migration promotion.

No live workbook import, inventory mutation, or database canonical promotion is authorized by this diagnostic slice.
