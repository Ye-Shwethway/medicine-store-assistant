# F7.2D3.1 Saved Model UI Freeze Runtime Hotfix

The browser freeze was caused by saved-model MutationObservers observing descendant mutations that their own callbacks produced. The deployed hotfix serves the saved-model JavaScript with those observers constrained to direct-child changes only (`subtree: false`) and bumps the saved-model asset version so clients cannot reuse the freezing asset response.

Acceptance:
- Agent/Session/Provider lists complete loading after opening AI Agent Management.
- Saved catalog enrichment does not recursively retrigger observers.
- Existing provider/model, MCP, inventory authority, and canonicality boundaries remain unchanged.
