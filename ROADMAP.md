# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2 verified complete; F6B remains test-only; F7.2D3 Provider Registry + model catalog is next; PostgreSQL remains non-canonical**

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

Primary ChatGPT external-access path is now the custom remote MCP service at the existing public MSA HTTPS origin.

Verified path:

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> typed backend -> authorized reads`

Verified current external-client scopes are `mcp:connect`, `mcp:read`, and `offline_access`; propose/write/control remain disabled. Custom GPT Actions are now optional/fallback only.

The MCP transport publishes a durable full typed schema, while execution remains controlled by live backend policy. `full transport/schema != full current authority`.

## F7.2D2 — Named AI Agent Management & multi-agent sessions — **VERIFIED COMPLETE**

PR #58 merged as `3b385a37b95c1ff79f76883381d8268fa6c49db2`; deploy run `32620386876` / job `97147568336` succeeded.

Verified capabilities:

- Owner-only named `AI_AGENT` principals;
- immutable stable `agent_id`;
- editable `display_name`;
- case-insensitive unique `call_name` for human-friendly addressing/selection;
- deterministic server-owned self-identity context so a future model does not rely on chat history to remember its name;
- lifecycle `ACTIVE` / `DISABLED` / `REVOKED`;
- capability, location, authority, execution, and confirmation-policy metadata;
- reusable multi-agent sessions with `GROUP`, `COMPARE`, `REVIEW`, and `DEBATE` topology modes;
- ordered participant selection and optional participant role labels;
- non-Owner Agent Management 403;
- public anonymous Agent Management 401;
- provider/model inference remains disabled;
- system production-write gate remains closed.

Canonical checkpoint: `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`.

## Web implementation workflow

Default Web workflow is now explicitly:

`UI/UX Pro Max -> MSA repo design system -> authenticated API contract -> direct code implementation -> responsive/accessibility/runtime verification`

Figma is optional and only used when the Owner explicitly requests it or a specific task genuinely requires it. It is not a normal implementation gate.

## F7.2D3 — Provider Registry + model catalog — **NEXT**

Owner-only Provider Registry will support:

- OpenAI;
- Google Gemini;
- OpenRouter;
- NanoGPT;
- generic `OPENAI_COMPATIBLE` providers.

Required workflow:

`Add provider -> provision secret securely -> Test connection -> Fetch models -> inspect normalized capabilities -> Save/enable`

Rules:

- no hard-coded model IDs as the primary catalog mechanism;
- provider API keys never persist as plaintext database fields;
- browser receives no plaintext provider key read-back;
- provider health is distinct from model health and agent health;
- unknown model capabilities remain unknown rather than guessed;
- custom provider URLs use SSRF protections;
- Provider Registry is Owner-only;
- provider/model configuration never expands an agent's authority.

## F7.2D4 — Internal model assignment & fallbacks

After F7.2D3:

- assign a primary provider/model to an agent;
- optional ordered fallback models;
- required-capability compatibility checks;
- timeout/output policy;
- server-side injection of canonical agent identity (`display_name` + stable `agent_id`) on every internal invocation;
- future multi-agent sessions can compare agents backed by different models/providers.

Changing provider/model never changes `agent_id` or authority.

## F7.3 — Actor-aware Audit & Operation Ledger

Operational/database Audit remains separate from User Management and Agent Management.

Actor classes: `HUMAN`, `AI_AGENT`, `SYSTEM`, `INTEGRATION`.

Meaningful operations retain actor/client/delegation/location/policy/outcome/read-back provenance. Historical committed facts use correction/reversal semantics rather than silent destructive rewriting.

## Later sequence

1. **F7.2D3** — Provider Registry + model catalog — next
2. **F7.2D4** — model assignment/fallback/runtime identity
3. **F7.3** — actor-aware Audit / operation ledger
4. **F7.4** — Inventory Locations / Store Policy / Preferences
5. **F7.5** — Smart Calculator / receipts, calculation-only first
6. **F7.6** — deterministic Smart Analysis
7. **F7.7** — internal read-only AI Assistant
8. **F7.8** — Alerts & Notifications
9. optional standalone Custom GPT Action path if a concrete need appears
10. **F9** — controlled typed writes only after required authority/audit/location/idempotency foundations
11. **F10** — real workflow + fresh migration + Sheet sync validation
12. **F11** — explicit canonical DB promotion
13. Telegram/Flutter rollout over proven contracts

## Immediate boundary

The next authorized implementation slice is **F7.2D3 Provider Registry + model catalog**.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion as part of F7.2D3/F7.2D4.

## Canonical architecture/docs

- `IMPLEMENTATION_PLAN.md`
- `NEW_CHAT_BOOTSTRAP.md`
- `docs/architecture/README.md`
- `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
- `docs/architecture/F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md`
- `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
- `docs/checkpoints/F7_2D0_MCP_CONNECTIVITY_VERIFIED_2026-08-23.md`
- `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`
- `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.
