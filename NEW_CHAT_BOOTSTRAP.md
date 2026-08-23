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
7. `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
8. `docs/architecture/F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md`
9. `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
10. `docs/checkpoints/F7_2D0_MCP_CONNECTIVITY_VERIFIED_2026-08-23.md`
11. `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`
12. task-relevant F7 architecture/design docs
13. current repository/runtime/deployment evidence

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

## F6B test-only snapshot

- batch `be13d127-5045-4284-a088-0a0b9b024d76`
- rows 1,646
- SAFE 1,417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7

Never silently promote this dataset into migration truth.

## Human-account truth

Canonical human roles:

- `OWNER`
- `ADMIN`
- `STAFF`
- `READ_ONLY`

States:

- `PENDING`
- `ACTIVE`
- `DISABLED`

Stable human identity is UUID `user_id`. Username/password/recovery-email lifecycle is already product-native and verified. User Management remains Owner-only and separate from operational Audit.

## Custom MCP — verified primary ChatGPT path

Custom MCP is no longer proposal-only. It is live and verified.

Verified path:

`ChatGPT Developer Mode -> OAuth/PKCE -> https://inventory.drthorne.uk/mcp -> typed MSA backend`

Verified current external-client scopes:

- `mcp:connect`
- `mcp:read`
- `offline_access`

Propose/write/control remain disabled.

The MCP server is designed full-schema/policy-gated: future typed capabilities can be unlocked through backend policy without rebuilding the connector. Raw SQL, DB credentials, VPS shell/filesystem, plaintext secrets, or generic unrestricted HTTP proxying are never part of “full capability”.

Custom GPT Actions are optional/fallback only unless a concrete standalone-GPT need appears.

## F7.2D2 — verified current Agent Management truth

Runtime anchor:

- PR #58
- merge SHA `3b385a37b95c1ff79f76883381d8268fa6c49db2`
- deploy run `32620386876`
- deploy job `97147568336`
- issue #26 `status=success`
- migration `0010_mcp_oauth -> 0011_ai_agents`

Agent Management is Owner-only.

Each agent has:

- immutable stable `agent_id`;
- editable `display_name`;
- case-insensitive unique `call_name` for human-friendly addressing/selection;
- description/purpose;
- runtime mode;
- `ACTIVE` / `DISABLED` / `REVOKED` lifecycle;
- explicit capability/location/authority/execution/confirmation policy metadata.

Renaming preserves `agent_id`.

MSA generates deterministic self-identity context from canonical agent data. Future model execution must inject this server-side every invocation; agents do not rely on conversation memory to remember their own name.

### Multi-agent session foundation

Persistent sessions support:

- stable `session_id`;
- session name/objective;
- `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` modes;
- ordered participant selection;
- optional participant role labels;
- open/closed lifecycle.

This is currently topology/configuration only. Provider/model inference is **disabled**.

Runtime verification passed named identity, stable ID, self-identity context, call-name uniqueness, non-Owner 403, multi-agent session persistence/order, disable/reactivate, revoke guard, and inference-disabled checks.

## Web implementation rule — corrected/current

Normal MSA Web work uses:

`UI/UX Pro Max -> repo design system -> authenticated API contract -> direct code implementation -> responsive/accessibility/runtime verification`

Pinned UI/UX Pro Max upstream commit:

`bc826e2267a36d98a2dcf5231e16c30ff546770f`

Canonical design files:

- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`

**Figma is optional, not mandatory.** Use it only when the Owner explicitly asks or a specific task genuinely requires it.

## Next authorized slice

**F7.2D3 — Provider Registry + model catalog**.

Owner-only first-class presets:

- OpenAI
- Google Gemini
- OpenRouter
- NanoGPT
- generic `OPENAI_COMPATIBLE`

Required first workflow:

`Add provider -> provision secret securely -> Test connection -> Fetch models -> inspect normalized capabilities -> Save/enable`

Do not hard-code model IDs as the primary catalog. Provider keys remain runtime secrets/secret references and are never read back to the browser or committed to Git.

Provider/model choice is runtime implementation only and never increases agent authority.

## Then

1. F7.2D4 — internal model assignment/fallbacks + canonical identity injection
2. F7.3 — actor-aware Audit / operation ledger
3. F7.4 — Inventory Locations / Store Policy / Preferences
4. F7.5 — Smart Calculator / receipts, calculation-only first
5. F7.6 — Smart Analysis
6. F7.7 — internal read-only AI Assistant
7. F7.8 — Alerts & Notifications
8. F9 — controlled writes only after required foundations
9. F10 — real workflow + fresh migration + Sheet sync validation
10. F11 — explicit canonical promotion

## Required invariants

- AI agents are not human accounts.
- Agent identity is separate from provider/model/client transport.
- Provider/model selection is not authority.
- AI Agent Management and global Settings are Owner-only.
- Agents cannot self-escalate or edit their own grants/control-plane policy.
- Multi-agent sessions cannot union participant privileges.
- `$msa` SAFE/REVIEW/CONFLICT/NEW_UNMAPPED + read-back/audit workflow parity remains required.
- Significant writes are never reported successful before committed-state read-back.

## Immediate implementation instruction

A fresh implementation chat that reconciles these facts may proceed directly with **F7.2D3 Provider Registry + model catalog**. Do not repeat MCP proof or F7.2D2 architecture unless live repository/runtime evidence contradicts this checkpoint.

## Continuity rule

After significant architecture, implementation, deployment, migration, design-system, or next-work changes, update `ROADMAP.md`, this file, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.
