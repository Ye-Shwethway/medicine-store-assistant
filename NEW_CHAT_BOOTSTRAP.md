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
10. `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
11. `docs/checkpoints/F7_2D0_MCP_CONNECTIVITY_VERIFIED_2026-08-23.md`
12. `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`
13. `docs/checkpoints/F7_2D3_PROVIDER_REGISTRY_VERIFIED_2026-08-23.md`
14. task-relevant F7 architecture/design docs
15. current repository/runtime/deployment evidence

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

Verified complete:

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
- F7.2D0 custom MCP/OAuth full-schema connectivity proof
- F7.2D2 named AI Agent Management + multi-agent session topology
- F7.2D3 Provider Registry + dynamic model catalog

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

## F7.2D2 — named Agent Management truth

Runtime anchor:

- PR #58
- merge SHA `3b385a37b95c1ff79f76883381d8268fa6c49db2`
- deploy run `32620386876`
- deploy job `97147568336`
- migration `0010_mcp_oauth -> 0011_ai_agents`

Agent Management is Owner-only. Each agent has immutable `agent_id`, editable `display_name`, unique human-friendly `call_name`, lifecycle, capability/location/authority/execution/confirmation metadata, and server-owned deterministic self-identity context.

Persistent sessions support `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`, ordered participants, role labels, and open/closed lifecycle.

## F7.2D3 — verified Provider Registry truth

Runtime anchor:

- PR #60
- merge SHA `882c67b0134edb59156c17e948128de0ca8c3365`
- deploy run `32621925138`
- deploy job `97151213410`
- issue #26 `status=success`
- migration `0011_ai_agents -> 0012_providers`

Provider Registry is Owner-only and supports:

- OpenAI
- Google Gemini
- OpenRouter
- NanoGPT
- generic `OPENAI_COMPATIBLE`

Provider credentials are write-only. A dedicated server-side `msa_provider_secrets` Docker volume stores the secret material; PostgreSQL stores only opaque `credential_ref`. The Web/API never reads a saved provider key back to the Owner.

Provider flow now exists:

`Add provider -> provision credential -> Test connection -> Fetch models -> inspect normalized catalog -> Enable`

Deployment/runtime verification confirmed provider CRUD foundation, write-only secret persistence, no plaintext provider key in DB, enable gate, model normalization, Owner-only/public auth boundaries, and migration health. Deployment itself did not invoke a real provider API.

Custom provider base URLs require public HTTPS and reject private/loopback/link-local/reserved destinations and redirects. Provider responses are bounded and sanitized. Unknown model capability remains unknown rather than guessed.

### Current Agent Management presentation

- `Create agent` and `New session` use the same secondary-button design family as `Refresh`.
- Agent list is split into `External / MCP agents` and `Internal / provider-backed agents`.
- Agent cards show `Agent name`, `Origin`, and `Model`.
- Internal agents show `Not assigned` until F7.2D4.
- External runtime models show `Client-managed` rather than being guessed.
- Provider Registry appears in the same Owner-only AI control-plane page.

## Web implementation rule

Normal MSA Web work uses:

`UI/UX Pro Max -> repo design system -> authenticated API contract -> direct code implementation -> responsive/accessibility/runtime verification`

Pinned UI/UX Pro Max upstream commit:

`bc826e2267a36d98a2dcf5231e16c30ff546770f`

Canonical design files:

- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`

**Figma is optional, not mandatory.**

For every changed Dashboard CSS/JS asset, update/verify the HTML entrypoint version marker and browser delivery chain under `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md` before calling the UI verified.

## Next authorized slice

**F7.2D4 — internal model assignment/fallback/runtime identity**.

Required direction:

- assign primary provider/model to a named internal agent;
- optional ordered fallback chain;
- compatibility checks against known model capabilities;
- timeout/output policy and optional cost/usage metadata;
- inject current canonical agent identity on every model invocation;
- provider/model changes never alter stable `agent_id` or authority;
- prepare actual single-agent inference and future multi-agent comparison/review/debate execution.

Do not automatically bind or invent an existing external MCP agent identity/name. If the current ChatGPT MCP client is to become a named `AI_AGENT`, bind it through an explicit Owner-controlled relationship rather than guessing identity.

## Then

1. F7.3 — actor-aware Audit / operation ledger
2. F7.4 — Inventory Locations / Store Policy / Preferences
3. F7.5 — Smart Calculator / receipts, calculation-only first
4. F7.6 — Smart Analysis
5. F7.7 — internal read-only AI Assistant
6. F7.8 — Alerts & Notifications
7. F9 — controlled writes only after required foundations
8. F10 — real workflow + fresh migration + Sheet sync validation
9. F11 — explicit canonical promotion

## Required invariants

- AI agents are not human accounts.
- Agent identity is separate from provider/model/client transport.
- Provider/model selection is not authority.
- AI Agent Management, Provider Registry, and global Settings are Owner-only.
- Agents cannot self-escalate or edit grants/control-plane policy.
- Multi-agent sessions cannot union participant privileges.
- `$msa` SAFE/REVIEW/CONFLICT/NEW_UNMAPPED + read-back/audit workflow parity remains required.
- Significant writes are never reported successful before committed-state read-back.

## Immediate implementation instruction

A fresh implementation chat may proceed directly with **F7.2D4 model assignment/fallback/runtime identity**. Do not repeat MCP proof, F7.2D2 Agent Management, or F7.2D3 Provider Registry unless live repository/runtime evidence contradicts these verified checkpoints.

## Continuity rule

After significant architecture, implementation, deployment, migration, design-system, or next-work changes, update `ROADMAP.md`, this file, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.