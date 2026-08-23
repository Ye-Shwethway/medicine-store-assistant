# F7.3A — Minimal MCP Audit Proof

Status: implementation candidate

Purpose: prove that a bound external MCP agent performs a real server-side read by persisting append-only actor-aware evidence that is independently visible in the MSA Audit surface.

Initial proof path:

`ChatGPT MCP -> bound named agent -> msa_inventory_read_summary -> shadow DB read -> operation_audit_events -> Dashboard Audit / Recent activity`

Recorded fields include event/correlation IDs, actor type, stable agent ID, delegated human authority, client source, client ID, runtime type, typed action name, capability scope, outcome, safe metadata, and timestamp. Tokens, authorization headers, prompts, provider keys, passwords, and session secrets are excluded.

This is intentionally not the full F7.3 Audit implementation. Month/date filters, provider/model filters, location/target drill-down, reversal/read-back/sync linkage, exports, and monthly history/archive navigation remain in full F7.3.

No production inventory write, canonical promotion, or new write authority is enabled by this proof.
