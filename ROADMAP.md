# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2/F7.2D3 verified complete; F6B remains test-only; F7.2D4 model assignment/fallback/runtime identity is next; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. The current F6B snapshot is test-only and is not an accepted migration baseline. A fresh migration candidate is imported only after the redesigned operational workflow, location model, management surfaces, and shadow-validation path are ready and explicitly approved.

## Delivery policy

Canonical flow: `branch -> PR -> main -> automatic VPS deploy for relevant runtime changes -> issue #26 runtime evidence -> continuity docs`.

Normal continuation does not require manual VPS commands, Termux/SSH/tmux, Bamboo/Bamboo Claw, or a manual Actions deploy button. Prefer connected tools, repository automation, the repo-scoped self-hosted runner, and durable browser/admin mechanisms.

Runtime secrets remain only on the VPS. Normal backend deployment must not read/import the live workbook.

## Product direction

MSA is a multi-client intelligent store-operations platform. Web, custom MCP, future Telegram/Flutter, internal AI, scheduled jobs, and optional external clients reuse the same typed backend contracts and authority engine.

Preserve the existing `$msa` workflow:

`source evidence -> reconcile current truth -> SAFE / REVIEW / CONFLICT / NEW_UNMAPPED -> Owner-authorized typed operation -> committed read-back -> audit`

No client or AI agent receives arbitrary SQL, raw database credentials, VPS shell, or unrestricted infrastructure access.

## Verified foundation

- F0 VPS inspection — verified 2026-08-22
- F1 runtime skeleton — verified 2026-08-22
- Cloudflare public HTTPS route — verified 2026-08-22
- F2 PostgreSQL foundation — verified 2026-08-22
- F3 authenticated read-only API — verified 2026-08-22
- F4 synthetic ledger foundation — verified 2026-08-22
- F5 CMS catalogue versioning — verified 2026-08-22
- F5.1 authenticated catalogue read API — verified 2026-08-22
- F6A synthetic shadow migration adapter — verified 2026-08-22
- F6B live-workbook snapshot — **test-only staging exercise**
- F6C authenticated shadow read API — verified 2026-08-22
- F7.1 read-only Web Dashboard — verified 2026-08-22
- F7.2A canonical multi-user identity/sessions — verified via PR #36
- F7.2B User Management/profile — verified via PR #38
- F7.2C Credential + Recovery Lifecycle — verified through PR #49
- F7.2D0 custom MCP full-schema/OAuth connectivity — verified 2026-08-23
- F7.2D2 named AI Agent Management + multi-agent session topology — verified 2026-08-23 via PR #58
- F7.2D3 Provider Registry + dynamic model catalog — verified 2026-08-23 via PR #60

## Current F6B test-only snapshot

- batch ID `be13d127-5045-4284-a088-0a0b9b024d76`
- rows **1,646**
- SAFE **1,417**
- REVIEW **222**
- CONFLICT **0**
- NEW_UNMAPPED **7**
- `migration_baseline_accepted=false`
- `database_canonical=false`

## F7.2D0 — Custom MCP access — **VERIFIED COMPLETE**

Primary ChatGPT external-access path is the custom remote MCP service.

Verified path:

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> typed backend -> authorized reads`

Current external-client scopes are `mcp:connect`, `mcp:read`, and `offline_access`; propose/write/control remain disabled. Custom GPT Actions are optional/fallback only.

The MCP transport publishes a durable full typed schema, while execution remains controlled by live backend policy. `full transport/schema != full current authority`.

## F7.2D2 — Named AI Agent Management & multi-agent sessions — **VERIFIED COMPLETE**

PR #58 merged as `3b385a37b95c1ff79f76883381d8268fa6c49db2`; deploy run `32620386876` / job `97147568336` succeeded.

Verified capabilities:

- Owner-only named `AI_AGENT` principals;
- immutable stable `agent_id`;
- editable `display_name` and case-insensitive unique `call_name`;
- deterministic server-owned self-identity context;
- `ACTIVE` / `DISABLED` / `REVOKED` lifecycle;
- capability/location/authority/execution/confirmation metadata;
- reusable `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` sessions;
- ordered participants and optional role labels;
- non-Owner 403/public anonymous 401;
- production system write gate remains closed.

Canonical checkpoint: `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`.

## F7.2D3 — Provider Registry + model catalog — **VERIFIED COMPLETE**

PR #60 merged as `882c67b0134edb59156c17e948128de0ca8c3365`; deploy run `32621925138` / job `97151213410` succeeded. Alembic upgraded `0011_ai_agents -> 0012_providers`.

Verified capabilities:

- Owner-only provider registry for OpenAI, Google Gemini, OpenRouter, NanoGPT, and generic `OPENAI_COMPATIBLE`;
- dedicated server-side provider-secret volume; PostgreSQL stores only opaque `credential_ref` rather than plaintext provider keys;
- provider credentials are write-only from the Web control plane and never returned to the browser;
- server-side connection-test and dynamic model-fetch endpoints;
- normalized model catalog with bounded metadata and explicit unknown capability states;
- provider state/health remains distinct from model/agent state;
- enable gate requires configured credential, healthy connection test, and successful model fetch;
- custom provider URL validation blocks non-HTTPS/private/loopback/link-local/reserved destinations and redirects;
- provider responses are bounded/sanitized;
- public anonymous Provider Registry returns 401;
- deploy verifier made no real provider API call and no inventory mutation/workbook import occurred.

Agent Management UI was also refined to match the approved dashboard language:

- `Create agent` and `New session` use the same secondary-button family as `Refresh`;
- agents are visibly grouped into `External / MCP agents` and `Internal / provider-backed agents`;
- each agent card shows `Agent name`, `Origin`, and `Model` primary metadata;
- unassigned internal agents show `Not assigned`; external client models remain `Client-managed` rather than guessed;
- Provider Registry lives in the same Owner-only AI control-plane page.

Canonical checkpoint: `docs/checkpoints/F7_2D3_PROVIDER_REGISTRY_VERIFIED_2026-08-23.md`.

## Web implementation workflow

Default Web workflow:

`UI/UX Pro Max -> MSA repo design system -> authenticated API contract -> direct code implementation -> responsive/accessibility/runtime verification`

Figma is optional and only used when explicitly requested.

## F7.2D4 — Internal model assignment, fallback & runtime identity — **NEXT**

Next slice:

- assign a primary provider/model to a named internal agent;
- optional ordered fallback chain;
- capability compatibility checks;
- timeout/output policy and optional usage/cost metadata;
- server-side injection of canonical agent identity (`display_name` + stable `agent_id`) on every invocation;
- preserve authority independently from provider/model assignment;
- prepare real single-agent inference and future multi-agent compare/review/debate execution across same or different providers.

Changing provider/model never changes `agent_id` or authority. External MCP identities remain separate from internal provider-backed agents.

## F7.3 — Actor-aware Audit & Operation Ledger

Operational/database Audit remains separate from User Management and Agent Management. Actor classes: `HUMAN`, `AI_AGENT`, `SYSTEM`, `INTEGRATION`.

Meaningful operations retain actor/client/delegation/location/policy/outcome/read-back provenance. Historical committed facts use correction/reversal semantics rather than silent destructive rewriting.

## Later sequence

1. **F7.2D4** — model assignment/fallback/runtime identity — next
2. **F7.3** — actor-aware Audit / operation ledger
3. **F7.4** — Inventory Locations / Store Policy / Preferences
4. **F7.5** — Smart Calculator / receipts, calculation-only first
5. **F7.6** — deterministic Smart Analysis
6. **F7.7** — internal read-only AI Assistant
7. **F7.8** — Alerts & Notifications
8. optional standalone Custom GPT Action path if a concrete need appears
9. **F9** — controlled typed writes only after required authority/audit/location/idempotency foundations
10. **F10** — real workflow + fresh migration + Sheet sync validation
11. **F11** — explicit canonical DB promotion
12. Telegram/Flutter rollout over proven contracts

## Immediate boundary

The next authorized implementation slice is **F7.2D4 internal model assignment/fallback/runtime identity**.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion as part of F7.2D4.

## Canonical architecture/docs

- `IMPLEMENTATION_PLAN.md`
- `NEW_CHAT_BOOTSTRAP.md`
- `docs/architecture/README.md`
- `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
- `docs/architecture/F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md`
- `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
- `docs/checkpoints/F7_2D0_MCP_CONNECTIVITY_VERIFIED_2026-08-23.md`
- `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`
- `docs/checkpoints/F7_2D3_PROVIDER_REGISTRY_VERIFIED_2026-08-23.md`
- `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.