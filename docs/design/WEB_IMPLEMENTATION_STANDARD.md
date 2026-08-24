# Medicine Store Assistant — Web Implementation Standard

Status: **mandatory for all Dashboard/Web implementation**

This standard exists because repeated production defects were not isolated syntax bugs. They were integration defects: stale asset identity, two scripts owning the same DOM, event handlers lost after `innerHTML` replacement, persisted backend state omitted during rehydration, live-only behavior that failed after reload/reopen, and CI that proved strings/routes existed without proving a user click worked.

The goal is not to add a heavy frontend framework or slow production. The goal is a small set of deterministic rules that prevent the same class of defects from reaching production.

## Research basis

The rules below are aligned with:

- MDN Event Bubbling / Event Delegation: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling
- MDN EventTarget.addEventListener: https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
- MDN MutationObserver.observe: https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver/observe
- MDN HTTP Caching / cache busting: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching
- Playwright Best Practices: https://playwright.dev/docs/best-practices
- Playwright Locators / current-DOM behavior: https://playwright.dev/docs/locators

## 1. Single owner for every interactive surface

**One interactive DOM subtree must have one authoritative renderer/state owner.**

A second script may add a narrow enhancement outside that subtree, but it must not independently reconstruct the same chat/detail/form DOM.

For every significant surface, record:

- state owner;
- renderer owner;
- event owner;
- persistence source;
- polling/live-update owner.

If two files both call `innerHTML`/`replaceChildren` on the same interactive subtree, stop and consolidate ownership before adding another patch.

Do not solve ownership conflicts by adding another MutationObserver or another overlay renderer.

## 2. Replaceable DOM requires durable event wiring

If a subtree can be replaced, controls inside it must use one of these patterns:

1. delegated events on a stable ancestor; or
2. deterministic listener binding performed every time the subtree is rendered.

Prefer delegated events for dynamic chat/work-item surfaces.

A button existing in HTML is not proof that it works. Every new/changed interactive control must have a test that performs the user action and observes the expected effect.

## 3. MutationObserver is last-resort glue

Do not use MutationObserver as a primary state-management mechanism.

If it is genuinely required:

- observe the narrowest possible target;
- avoid `subtree:true` unless necessary;
- callback writes must be idempotent;
- never rewrite unchanged DOM from the observer callback;
- coalesce repeated work where appropriate;
- disconnect observers that are no longer required;
- add a regression test proving the observer cannot self-trigger indefinitely.

## 4. Frontend/backend changes are one paired contract

Any UI action backed by an API is implemented and verified as one contract:

`user action -> frontend event -> request method/path/payload -> auth/authority -> backend state change -> response -> persisted read-back -> UI rehydrate`

A feature is incomplete if only the backend route or only the frontend control exists.

For a mutating workflow-state action, tests must verify persistence/read-back, not merely HTTP 2xx.

## 5. Persisted state is the source for rehydration

Live UI state is temporary. After refresh/reopen, the browser must reconstruct the same user-visible workflow from persisted backend data.

Do not create special messages that exist only in memory/DOM. Owner turns, internal-agent turns, external MCP reviews, workflow status, and relevant provenance must have durable backing before they are relied on in the UI.

Render ordered conversations from one canonical persisted ordering. Do not independently group artifact types if that changes conversational chronology.

## 6. Mandatory lifecycle matrix

For each persistent interactive feature, verify all applicable paths:

1. **fresh load** — enter the page from a new document load;
2. **same-tab update** — perform the action without reloading;
3. **refresh** — reload the page after the state has changed;
4. **reopen** — navigate away/back or reopen the saved record;
5. **intermediate async state** — REVIEWING/WAITING_EXTERNAL/loading/etc.;
6. **terminal/settled state** — WAITING_OWNER/completed/failed/cancelled/etc.;
7. **mobile return path** — user can leave the active view without scrolling to an unrelated control.

A live-only success is not acceptance.

## 7. Async/polling ownership

Each async surface has one polling/live-update owner.

Required behavior:

- start exactly when the persisted state requires live updates;
- avoid duplicate timers;
- stop on settled/terminal state;
- resume after refresh/reopen if persisted status is still live;
- tolerate transient read failures without creating duplicate work;
- never use polling as the source of truth — polling only re-reads durable state.

## 8. Asset delivery and stale-code prevention

Browser-delivery integrity remains governed by `WEB_ASSET_RELEASE_INTEGRITY.md`.

Preferred cache identity is **content-derived** (hash of the actual served CSS/JS bundle) rather than a manually remembered release string. A content change must produce a different asset URL identity automatically.

Until immutable hashed filenames are introduced, authenticated Dashboard HTML and dynamic assets remain explicitly no-store/no-cache as defined by the current release contract.

Never diagnose a screenshot mismatch as “browser cache” until source -> entrypoint -> asset identity -> deployed SHA -> browser delivery has been checked.

## 9. Interaction tests, not presence tests

Static assertions (`grep`, route existence, JS syntax) are useful but insufficient.

Critical Web flows require a lightweight real-browser interaction test where practical. Tests should interact through user-visible roles/labels and assert user-visible outcomes, following Playwright guidance.

At minimum, critical controls must prove:

- the control is visible/enabled when expected;
- clicking it sends the expected request;
- the request contains the expected payload;
- the returned/persisted state changes the UI;
- re-rendering does not make the control inert;
- reload/reopen restores the durable result.

Prefer resilient role/label locators over CSS implementation-detail selectors.

## 10. Required pre-merge Web review

Before a Web PR merges, explicitly review:

- [ ] one renderer/state owner per interactive subtree;
- [ ] no duplicate event owners;
- [ ] dynamic controls use delegated/rebound events safely;
- [ ] no broad non-idempotent MutationObserver loop;
- [ ] frontend/API payload and backend contract match;
- [ ] persisted state supports refresh/reopen;
- [ ] async timers start/resume/stop correctly;
- [ ] empty/loading/error/disabled states exist where applicable;
- [ ] mobile back/close/navigation path exists;
- [ ] asset identity changes automatically or is correctly bumped;
- [ ] JS syntax/backend tests pass;
- [ ] critical interaction test clicks the changed control;
- [ ] deployment issue #26 confirms the exact merged SHA before production acceptance.

## 11. Surface ownership registry

Keep `docs/design/WEB_SURFACE_OWNERSHIP.md` current when ownership changes. This registry is architectural, not decorative: it prevents two independent scripts from silently taking responsibility for the same interactive DOM.

## 12. Definition of done for Web slices

A Web slice is done only when all four are true:

1. **contract correct** — backend/frontend/auth/persistence agree;
2. **interaction correct** — actual user action works;
3. **lifecycle correct** — same-tab + refresh/reopen work;
4. **delivery correct** — exact deployed source/assets reach the browser.

CI green on source-only checks is not sufficient evidence by itself.
