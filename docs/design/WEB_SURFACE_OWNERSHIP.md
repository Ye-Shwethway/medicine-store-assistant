# Medicine Store Assistant — Web Surface Ownership Registry

Status: **required architecture registry**

This file records who owns rendering, events, persistence hydration, and live updates for interactive Dashboard surfaces. Two independent scripts must not own the same interactive subtree.

| Surface | Stable root | State / setup owner | Interactive renderer owner | Event owner | Persistence source | Live/polling owner |
| --- | --- | --- | --- | --- | --- | --- |
| AI Workspace — Single Chat | `#aiChatMode` | `dashboard_ai_workspace.js` | `dashboard_ai_workspace.js` | `dashboard_ai_workspace.js` | AI Workspace conversation/message APIs | `dashboard_ai_workspace.js` |
| Multi-Agent — setup/history | `#aiMultiMode` outside active chat state | `dashboard_multi_agent_review.js` | `dashboard_multi_agent_review.js` | `dashboard_multi_agent_review.js` | Work Item list/session APIs | none |
| Multi-Agent — active Review chat | `#reviewWorkDetail` | `dashboard_multi_agent_review.js` supplies Work Item selection/context | **one Review chat renderer only**; current transition target is `dashboard_multi_agent_live_export.js` until consolidation | delegated stable-ancestor handling; base Review host owns workflow actions, live module owns only its explicitly registered enhancements | Work Item/Artifact/Review/Event/Attention APIs | `dashboard_multi_agent_live_export.js` |
| MCP Agent binding/settings | Agent Management MCP connection section | `dashboard_mcp_binding.js` | `dashboard_mcp_binding.js` | `dashboard_mcp_binding.js` | MCP binding/grant APIs | none |

## Multi-Agent transition rule

The current Multi-Agent implementation grew from a base Review UI plus a later live/export module. This is a known risk area because both historically reconstructed `#reviewWorkDetail`.

Effective immediately:

- new functionality must not introduce a third renderer/observer for this surface;
- the active Review chat must converge to one authoritative rendering function;
- workflow controls inside replaceable chat DOM must use delegated events on the stable `#aiMultiMode` host or a renderer-owned deterministic binding step;
- external review, Owner feedback, internal-agent turns, Copy/provenance, export controls and status must all rehydrate from the same persisted Work Item detail;
- rendering order follows persisted artifact chronology;
- same-tab, refresh and reopen must produce the same durable conversation.

A later cleanup may merge the base/live files, but file count is not the invariant. **Single interactive ownership is the invariant.**

## Updating this registry

Update this file in the same PR whenever a Web change:

- adds a new interactive surface;
- moves rendering/event/polling responsibility between files;
- adds a second script that touches an existing surface;
- changes the persisted data source used to rehydrate a surface.
