# Medicine Store Assistant — Web Asset Release Integrity

Status: **required for all Dashboard UI releases**

## Why this exists

On 2026-08-23, F7.2D3 Provider Registry backend/API/CSS/JS deployed successfully, but the Dashboard entrypoint still referenced an older Agent asset cache key. The result was a silent partial UI release: backend capability was live, CI was green, but the browser loaded older CSS/JS.

Later D4.8 work reinforced the same lesson: source correctness is not browser delivery correctness.

## Canonical rule

A Dashboard UI release is not complete merely because changed CSS/JS/backend files reached `main` or CI passed.

For any user-visible Web change, verify the full delivery chain:

`source change -> entrypoint reference -> asset cache identity -> deployed asset -> browser-visible behavior`

## Current asset-identity implementation

MSA now prefers **content-derived query identity** for Dashboard bundles. `backend/app/dashboard_asset_version.py` hashes the exact CSS/JS files associated with an entrypoint bundle, and `backend/app/main.py` uses that hash as the `?v=` identity.

Therefore:

- changing served CSS/JS changes the browser URL identity automatically;
- no agent/human should manually invent or remember a release marker for those migrated bundles;
- CI must reject reintroduction of known stale manual markers;
- authenticated Dashboard HTML and assets remain no-store/no-cache under the current lightweight delivery model.

This follows the standard cache-busting principle documented by MDN: changing resources should receive a changed URL identity, commonly using a version or hash.

Reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching

## Required release checklist

1. If Dashboard CSS/JS changes, identify the bundle/entrypoint that serves it.
2. Prefer content-derived identity. If any asset is still manually versioned, bump that identity in the same change.
3. Never reuse an older manual release tag for newer content.
4. Dashboard HTML must remain explicitly non-stale (`no-store` under the current authenticated Dashboard contract).
5. Dashboard CSS/JS responses must remain `Cache-Control: no-store, max-age=0` plus compatible no-cache headers while the current direct-file serving model remains in use.
6. CI must validate content-derived identity wiring and reject known stale markers.
7. CI/UI validation must check user-visible behavior and entrypoints, not only backend routes or standalone JS syntax.
8. After merge, do not declare the UI live from merge/CI evidence alone. Wait for the automatic deployment checkpoint in issue #26.
9. Deployment verification must confirm the deployed source SHA and, where practical, the live HTML asset references/cache headers.
10. For dynamically injected UI, verify that the actual deployed JavaScript containing the behavior is loaded by the browser.
11. A runtime/API verifier passing is not sufficient evidence that a browser feature is usable.
12. If a screenshot/browser report contradicts CI/deploy assumptions, treat the screenshot as evidence of a delivery/integration defect and inspect source -> entrypoint -> identity -> deployed SHA before blaming browser cache.

## Future direction

Immutable content-hashed filenames plus long-lived immutable caching would be a conventional future build-system direction. The current content-derived query identity removes the human version-drift failure mode without introducing a frontend build pipeline yet.

## Ownership

This rule is part of the Web release contract alongside:

- `AGENTS.md`
- `docs/design/WEB_IMPLEMENTATION_STANDARD.md`
- `docs/design/WEB_SURFACE_OWNERSHIP.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`
- repository CI/deployment workflows

No future Web slice should be called verified complete until source, interaction, lifecycle, and browser delivery are all consistent with the deployed SHA.
