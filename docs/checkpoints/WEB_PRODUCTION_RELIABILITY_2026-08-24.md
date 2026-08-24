# Web Production Reliability Hardening — 2026-08-24

Status: implementation branch under acceptance.

This hardening slice was opened after repeated Dashboard production defects in D4.8 exposed systemic Web integration gaps rather than isolated syntax errors.

Implemented on this branch:

- mandatory `docs/design/WEB_IMPLEMENTATION_STANDARD.md`;
- mandatory `docs/design/WEB_SURFACE_OWNERSHIP.md`;
- concise Web reliability rules in `AGENTS.md`;
- content-derived Dashboard asset identity via `dashboard_asset_version.py`;
- active Multi-Agent chat renderer ownership bridge so the base Review UI delegates to one authoritative renderer when the live module is loaded;
- duplicate direct feedback-button binding removed; stable-host delegated event remains;
- repository Web reliability validator;
- Playwright Chromium mobile-size interaction smoke covering Review reopen/back navigation and blank external-feedback submission through the replaceable chat DOM;
- updated asset-release and UI/UX integration design contracts.

Research basis:

- MDN event bubbling/delegation;
- MDN `addEventListener` and `MutationObserver` behavior;
- MDN HTTP caching/cache-busting guidance;
- Playwright best practices and locator guidance.

Acceptance requirement:

- Web reliability CI green, including real browser interaction;
- existing backend/AI Workspace/federation regressions green;
- exact merge SHA deployed through issue #26;
- subsequent Web slices must follow the new implementation standard.

No inventory canonicality or mutation authority changes are included.
