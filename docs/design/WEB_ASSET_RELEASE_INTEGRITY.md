# Medicine Store Assistant — Web Asset Release Integrity

Status: **required for all Dashboard UI releases**

## Why this exists

On 2026-08-23, F7.2D3 Provider Registry backend/API/CSS/JS deployed successfully, but `dashboard.html` still referenced the older F7.2D2 Agent asset cache key. The result was a silent partial UI release: backend capability was live, CI was green, but the browser continued loading older Agent Management CSS/JS, so Provider Registry did not appear and button styling stayed stale.

This failure mode must not recur.

## Canonical rule

A Dashboard UI release is not complete merely because changed CSS/JS/backend files reached `main` or CI passed.

For any user-visible Web change, verify the full delivery chain:

`source change -> entrypoint reference -> asset cache identity -> deployed asset -> browser-visible behavior`

## Required release checklist

1. If a dashboard CSS or JS asset changes, inspect every HTML entrypoint that references it.
2. Version-bump the asset URL/cache identity in the entrypoint whenever the asset content changes, unless the build system uses immutable content-hashed filenames.
3. Do not reuse an older release tag such as `?v=f72d2-1` for newer asset content.
4. Dashboard HTML must be served `no-store`.
5. Dashboard CSS/JS responses must be served `Cache-Control: no-store, max-age=0` plus compatible no-cache headers while MSA uses manually versioned static assets.
6. CI must validate that the intended current asset version appears in the entrypoint and that known stale version markers for the changed asset do not remain.
7. CI/UI contract validation must check the user-visible feature entrypoints, not only backend routes or standalone JS syntax.
8. After merge, do not declare the UI live from merge/CI evidence alone. Wait for the automatic deployment checkpoint in issue #26.
9. Deployment verification for a UI release must confirm the deployed source SHA and, where practical, the live HTML asset references/cache headers.
10. For dynamically injected UI, verify that the JavaScript containing the injection logic is the version actually referenced by the live HTML.
11. A runtime/API verifier passing is not sufficient evidence that a browser feature is visible.
12. If a screenshot/browser report contradicts CI/deploy assumptions, treat the screenshot as evidence of a delivery-path defect and inspect entrypoint/asset/version state before blaming browser cache.

## Preferred future direction

Manual query-string versioning is acceptable for the current lightweight dashboard, but a later frontend build system should prefer immutable content-hashed asset filenames so cache identity cannot drift from asset content.

Until then, every CSS/JS change must explicitly maintain the entrypoint version references.

## Ownership

This rule applies to all MSA Web work performed through the UI/UX Pro Max direct-code workflow and is part of the release contract alongside:

- `AGENTS.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`
- repository CI/deployment workflows

No future Web slice should be called verified complete until the browser delivery chain is consistent with the deployed source.