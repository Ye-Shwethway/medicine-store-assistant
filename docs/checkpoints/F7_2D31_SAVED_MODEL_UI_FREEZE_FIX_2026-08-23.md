# F7.2D3.1 Saved Model UI Freeze Fix — 2026-08-23

## Incident

After deploying the saved provider-model catalog overlay, the AI Agent Management screen could remain visually stuck on `Loading agents…`, `Loading sessions…`, and `Loading providers…` while other dashboard sections continued to work.

## Root cause

`dashboard_saved_models.js` installed `MutationObserver` instances on `#providerList` and `#agentList` with `subtree: true`. The observer callbacks then mutated descendants of those same observed trees:

- provider callback rendered the saved catalog inside provider cards;
- agent callback hydrated the model field inside agent cards.

Those descendant mutations retriggered the observers, producing a self-sustaining render/hydration loop and excessive API/DOM activity that could freeze the browser main thread, especially on mobile.

## Locked fix

Observe only direct list replacement (`childList: true, subtree: false`). The base Agent Management renderer replaces the direct children when agents/providers refresh, which is the only event the overlay needs. Descendant enrichment performed by the overlay must not retrigger hydration.

## Regression rule

Any UI enhancement layer using `MutationObserver` must not observe mutations that its own callback produces. Prefer direct-child observation, explicit event hooks, disconnect/reconnect guards, or idempotent debounced observation. CI should reject the known `childList:true,subtree:true` pattern for the saved-model list observers.

This incident does not change inventory authority, database canonicality, MCP authority, provider credentials, or saved-model semantics.
