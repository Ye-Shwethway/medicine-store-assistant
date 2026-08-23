# Medicine Store Assistant — New Chat Bootstrap

Use this file for project-development continuity and reconciliation in a fresh chat.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Mandatory reconciliation order

Before changing code/config/schema/runtime in a fresh chat, read in this order:

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `IMPLEMENTATION_PLAN.md`
5. `docs/architecture/README.md`
6. `docs/design/UI_UX_PRO_MAX_INTEGRATION.md` for Web work
7. `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md` for Web release verification
8. `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
9. `docs/architecture/F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md`
10. `docs/architecture/F7_2D0_MCP_SCHEMA_FINALIZATION_V2.md`
11. `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
12. `docs/architecture/F7_2D4A_EXTERNAL_MCP_AGENT_BINDING.md`
13. `docs/checkpoints/F7_2D0_MCP_CONNECTIVITY_VERIFIED_2026-08-23.md`
14. `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`
15. `docs/checkpoints/F7_2D3_PROVIDER_REGISTRY_VERIFIED_2026-08-23.md`
16. `docs/checkpoints/F7_2D4A_MCP_AGENT_BINDING_VERIFIED_2026-08-23.md`
17. task-relevant F7 architecture/design docs
18. current repository/runtime/deployment evidence

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Current authority boundary

- Google Sheet/source documents remain operationally authoritative.
- PostgreSQL is deployed but **not canonical**.
- F6B staged dataset is **test-only** and not an accepted migration baseline.
- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- No production inventory write, AI inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, Sheet mirror conversion, or DB canonical promotion is authorized.

## Delivery policy

Canonical flow:

`branch -> PR -> main -> automatic VPS deploy -> issue #26 evidence -> continuity-doc refresh`

Do not require routine Termux, SSH, tmux, Bamboo/Bamboo Claw, or manual Actions work from the Owner. Runtime secrets remain on the VPS.

For Web changes, never infer that green backend/CI evidence means the browser feature is live. Changed CSS/JS must have a current entrypoint asset version, manually versioned assets remain no-store/no-cache, and browser delivery must match the deployed SHA. Follow `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`.

## Verified checkpoints

Verified complete/foundational:

- F0 VPS inspection
- F1 runtime skeleton
- Cloudflare public HTTPS route
- F2 PostgreSQL foundation
- F3 authenticated read-only API
- F4 synthetic ledger foundation
- F5 CMS catalogue versioning
- F5.1 catalogue read API
- F6A synthetic shadow migration adapter
- F6C authenticated shadow read API
- F7.1 read-only Web Dashboard
- F7.2A canonical human identity/sessions
- F7.2B User Management/profile
- F7.2C Credential + Recovery Lifecycle
- F7.2D0 custom MCP/OAuth connectivity
- F7.2D0 MCP schema finalization v2 — 94-action runtime catalog
- F7.2D2 named AI Agent Management + multi-agent session topology
- F7.2D3 Provider Registry + dynamic model catalog + tested saved-model catalog
- F7.2D4A external MCP OAuth grant -> named-agent binding
- F7.3A minimal external-MCP actor audit evidence
- F7.3B broad typed row-level shadow reads

## F6B test-only snapshot

- batch `be13d127-5045-4284-a088-0a0b9b024d76`
- rows 1,646
- SAFE 1,417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7

Never silently promote this dataset into migration truth.

## Custom MCP — verified primary ChatGPT path

Verified path:

`ChatGPT Developer Mode -> OAuth/PKCE -> https://inventory.drthorne.uk/mcp -> typed MSA backend`

Current external-client scopes are `mcp:connect`, `mcp:read`, and `offline_access`; propose/write/control remain disabled.

The MCP server is full-schema/policy-gated. Future typed grants can be unlocked through backend policy without rebuilding the connector. Raw SQL, DB credentials, shell/filesystem, plaintext secrets, Google Sheet credentials, and generic unrestricted HTTP proxying remain excluded.

Custom GPT Actions are optional/fallback only.

### MCP schema v2 — current durable truth

Runtime anchor:

- PR #76
- merge SHA `bed14194661f0f2d6536d1d90b0e79d4e37e6da3`
- deploy run `32637213532`
- issue #26 `status=success`
- schema version `2026-08-23.v2`
- expected runtime actions **94**
- tool-name SHA-256 `3031969fec8e5e3ea52937b8c00ba3106b6da185e998d161cea855d5db616662`

`msa_system_schema_manifest` is the server-owned schema identity. It reports version/count/hash/build/domain coverage and explicit exclusion classes.

The finalized catalog already reserves typed actions for current and future inventory/shadow/catalogue/reconciliation/transfers/locations/store policy/preferences/calculator/receipts/analysis/users/agents/multi-agent sessions/providers/audit/alerts/notifications/sync/sources/integrations/settings/migration-control domains.

Important exclusions:

- no provider API-key/credential provisioning or secret read-back through MCP;
- no password/token/recovery-secret action;
- legacy `msa_agents_rotate_credential` is removed from discovery;
- no arbitrary SQL/DB console;
- no shell/filesystem access;
- no generic unrestricted HTTP proxy.

Future work should normally implement existing `NOT_ENABLED` actions or extend inputs backward-compatibly. Adding new MCP action names is exceptional because the ChatGPT custom app may hold a scanned schema snapshot.

Before deleting/recreating the ChatGPT app, the deployed manifest must still report 94 actions. After creating the replacement app, verify the Actions list includes at least `msa_system_schema_manifest` and `msa_shadow_read_rows` and matches the expected count before deleting the old app.

## F7.2D2 — named Agent Management truth

Runtime anchor:

- PR #58
- merge SHA `3b385a37b95c1ff79f76883381d8268fa6c49db2`
- deploy run `32620386876`
- deploy job `97147568336`
- migration `0010_mcp_oauth -> 0011_ai_agents`

Agent Management is Owner-only. Each agent has immutable `agent_id`, editable `display_name`, unique human-friendly `call_name`, lifecycle, capability/location/authority/execution/confirmation metadata, and server-owned deterministic self-identity context.

Persistent sessions support `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`, ordered participants, role labels, and open/closed lifecycle.

## F7.2D3 — Provider Registry + saved model catalog truth

Provider Registry is Owner-only and supports OpenAI, Google Gemini, OpenRouter, NanoGPT, and generic `OPENAI_COMPATIBLE`.

Provider credentials are write-only. A dedicated server-side provider-secret volume stores secret material; PostgreSQL stores only opaque `credential_ref`. The Web/API never reads a saved provider key back to the Owner.

Current provider flow:

`Add provider -> provision credential -> Test connection -> Fetch models -> inspect detailed catalog -> Test model -> Save to approved provider catalog -> Enable`

Fetched/discovered models are not automatically usable models. Internal agents may bind only to Owner-saved, healthy models from the provider's approved catalog.

NanoGPT detailed discovery includes normalized capabilities, pricing, subscription/paid membership where provided by official endpoints, search/filter, and explicit unknown metadata rather than guessing.

## F7.2D4A — external MCP named-agent binding truth

Runtime anchor:

- PR #70
- merge SHA `5f00458b55e85cfe4e3a78f5fb7b2f8517e159e2`
- deploy run `32631778542`
- issue #26 `status=success`
- migration head `0014_mcp_agent_bindings`

Verified behavior:

- Owner can bind/rebind/unbind an active MCP OAuth grant to a named `EXTERNAL_MCP_CLIENT` agent from Agent Management.
- Binding does not require reconnecting ChatGPT.
- `msa_identity_whoami` resolves bound `agent_id`, display/call name, runtime/client context, and effective scopes.
- Named-agent effective MCP authority is live OAuth grant capability intersected with live agent capability scope and authority ceiling.
- Disabled/revoked/non-external agents contribute no named-agent capability authority.
- Unbound OAuth remains connected but reports `UNBOUND`; identity is never guessed.
- MSA cannot call back into ChatGPT through this binding. Outbound/internal AI is a separate provider-backed runtime path.
- Production inventory write and control-plane gates remain closed.

### Agent Management UI rules currently locked

- UI/UX Pro Max + MSA design system direct-code workflow; Figma optional only when explicitly requested.
- Primary constructive CTA uses green `.primary`.
- Neutral/lifecycle actions use `.secondary`.
- Destructive actions such as Revoke use `.danger-action`; browser-default action styling is not acceptable.
- Changed UI assets use versioned/no-store delivery and must avoid self-trigger MutationObserver loops.

## Early Audit/read foundations

F7.3 is not fully implemented, but these verified foundations are live:

- external MCP inventory/detail calls can create append-only actor-aware audit evidence;
- Dashboard Audit exposes minimal Recent activity;
- `mcp:read` means broad authorized typed operational reads, not summary-only;
- `msa_shadow_read_rows`, `msa_shadow_read_batch`, and `msa_shadow_read_review_reasons` provide permanent row-level migration diagnostics;
- raw SQL and secret-bearing auth/security tables remain excluded.

The full Audit UI still needs date/month, human, agent, runtime/client, provider/model, operation/result/location filters and preserved month/archive history navigation.

## Next authorized slice

Continue **F7.2D4 — internal model assignment/fallback/runtime identity**.

Required direction:

- assign a primary enabled provider + Owner-saved healthy model to a named internal agent;
- optional ordered fallback chain;
- compatibility checks against known model capabilities;
- timeout/output policy and optional usage/cost metadata;
- inject current canonical agent identity on every model invocation;
- provider/model changes never alter stable `agent_id` or authority;
- prove a narrow real provider-backed inference using Owner-configured credentials;
- prepare actual multi-agent comparison/review/debate execution using the already-published `msa_agent_invoke` / session schema when enabled.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutation, Sheet mirror conversion, or PostgreSQL canonical promotion during this continuation.