# Medicine Store Assistant — Implementation Plan

Status: **F7.2A/B/C, F7.2D0 custom MCP connectivity, F7.2D2 named Agent Management/multi-agent sessions, and F7.2D3 Provider Registry/model catalog are verified complete; F7.2D4 internal model assignment/fallback/runtime identity is next; production inventory write authority remains unauthorized**

This file is the execution contract for current MSA implementation order and boundaries.

## 1. Global implementation rules

- Google Sheets remains operationally authoritative until explicit F11 promotion.
- PostgreSQL being deployed does **not** make it canonical.
- F6B remains test-only and must never be silently promoted.
- All humans, AI agents, integrations, and system jobs use typed backend operations.
- Never expose arbitrary SQL, database credentials, VPS shell/filesystem, Google Sheet credentials, plaintext provider keys, or generic unrestricted HTTP proxying to AI/client runtimes.
- Deterministic backend code owns identity, authorization, capability/location policy, constraints, arithmetic, idempotency, transactions, derived state, and committed read-back.
- AI may interpret/reconcile/propose and later execute only explicitly authorized typed operations.
- Significant mutation success requires committed-state read-back.
- Historical committed facts use correction/reversal semantics rather than silent destructive rewriting.
- Secrets never enter Git, browser storage, ordinary logs, prompts, audit payloads, or docs evidence.
- Prefer smallest runnable slices; avoid unnecessary infrastructure.
- Normal continuation uses connected tools, PRs, and the self-hosted runner; do not require routine Termux/SSH/Bamboo/manual Actions work from the Owner.
- Significant implementation/deploy/next-work changes update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, and relevant canonical docs.

## 2. Existing `$msa` workflow parity

Preserve:

1. inspect source evidence;
2. reconcile against current authoritative truth;
3. classify `SAFE`, `REVIEW`, `CONFLICT`, `NEW_UNMAPPED`;
4. execute only Owner-authorized workflow classes;
5. surface material ambiguity;
6. commit through typed backend operation;
7. read affected state back;
8. record actor/operation provenance;
9. report success only after verification.

## 3. Verified foundation

Verified complete:

- F0/F1/Cloudflare/F2/F3/F4/F5/F5.1/F6A/F6C
- F7.1 read-only Dashboard
- F7.2A canonical human identity/sessions
- F7.2B User Management/profile
- F7.2C Credential + Recovery Lifecycle
- F7.2D0 custom MCP full-schema/OAuth connectivity
- F7.2D2 named Agent Management + multi-agent session topology
- F7.2D3 Provider Registry + dynamic normalized model catalog

F6B remains test-only: 1,646 rows; SAFE 1,417; REVIEW 222; CONFLICT 0; NEW_UNMAPPED 7; `migration_baseline_accepted=false`; `database_canonical=false`.

## 4. F7.2D0 — verified custom MCP foundation

Custom MCP is the verified primary ChatGPT access path:

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> typed backend`

Current granted external-client scopes are `mcp:connect`, `mcp:read`, and `offline_access`; propose/write/control remain disabled. Custom GPT Actions are optional/fallback only.

## 5. F7.2D2 — VERIFIED COMPLETE

Canonical design: `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`

Checkpoint: `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`

Runtime anchor: PR #58; merge `3b385a37b95c1ff79f76883381d8268fa6c49db2`; deploy run `32620386876`; job `97147568336`; migration `0010_mcp_oauth -> 0011_ai_agents`.

Implemented Owner-only named agents with stable `agent_id`, editable name/call name, deterministic self-identity context, lifecycle/policy metadata, and persistent multi-agent session topology (`GROUP`, `COMPARE`, `REVIEW`, `DEBATE`). Provider/model execution was intentionally deferred.

## 6. F7.2D3 — VERIFIED COMPLETE

Checkpoint: `docs/checkpoints/F7_2D3_PROVIDER_REGISTRY_VERIFIED_2026-08-23.md`

Runtime evidence:

- PR #60
- merge `882c67b0134edb59156c17e948128de0ca8c3365`
- deploy run `32621925138`
- job `97151213410`
- migration `0011_ai_agents -> 0012_providers`
- issue #26 `status=success`

Implemented:

- Owner-only providers: OpenAI, Gemini, OpenRouter, NanoGPT, generic `OPENAI_COMPATIBLE`;
- stable provider records and normalized dynamic model catalog;
- dedicated server-side provider-secret volume with opaque DB `credential_ref` only;
- browser/API saved-key no-readback;
- credential replace/remove lifecycle;
- server-side provider connection test and model fetch;
- enable gate requiring credential + healthy connection + successful model fetch;
- provider health/model-fetch state separate from agent state;
- bounded/sanitized model metadata and explicit unknown capabilities;
- production SSRF boundary for custom provider URLs: HTTPS/public resolution, forbidden private/loopback/link-local/reserved destinations, blocked redirects, bounded response size/count;
- anonymous Provider Registry 401;
- runtime verification of write-only secrets, no DB plaintext key, enable gate, and model normalizers without making any real provider call during deployment.

UI refinements delivered in the same slice:

- Create agent/New session buttons match dashboard secondary-control language;
- agent list separates External/MCP from Internal/provider-backed origins;
- agent cards expose Name / Origin / Model;
- provider registry is colocated in the Owner-only AI control-plane page.

### F7.2D3 remaining operational test

A real provider is not configured by deployment automation. The first Owner-configured provider must still be exercised through the Web workflow:

`Add provider -> enter API key in write-only field -> Test connection -> Fetch models -> inspect -> Enable`

That real credential must be entered through the Owner Web UI, never pasted into chat/Git/docs.

## 7. Web UI workflow

Default Web path:

`UI/UX Pro Max -> design-system/medicine-store-assistant/MASTER.md + page override -> authenticated API contract -> direct code implementation -> responsive/accessibility/runtime verification`

Figma is optional and not a normal implementation prerequisite.

## 8. F7.2D4 — Internal model assignment/fallback/runtime identity — NEXT

Purpose: connect durable named internal agents to verified provider/model resources without coupling identity or authority to the model implementation.

### Required assignment data

At minimum:

- stable assignment identity;
- `agent_id`;
- primary `provider_id` + provider-local `model_id`/catalog reference;
- ordered optional fallbacks;
- required capability expectations;
- request timeout/output policy;
- optional usage/cost budget metadata;
- enabled/disabled assignment state and provenance.

### Assignment rules

- only `INTERNAL_MODEL` agents receive provider/model assignments;
- provider must be enabled;
- model must exist in the provider's current catalog;
- known incompatible capability requirements must fail closed;
- unknown capability requires explicit Owner acknowledgement rather than being treated as supported;
- changing assignment never changes stable `agent_id`, call name, capability scope, location scope, authority ceiling, or system write gate;
- fallback provider/model order never expands authority;
- disabled/unhealthy provider handling must be explicit, with no silent arbitrary substitution.

### Runtime identity

Every internal model call must inject current canonical agent identity from MSA configuration, including at least `display_name` and stable `agent_id`. Do not rely on chat history for an agent remembering its own name.

### First inference boundary

F7.2D4 may prove narrow model execution after an Owner has configured and enabled a provider. Initial proof should be non-inventory or read-only, e.g. deterministic identity response / simple text prompt, before any broader AI Assistant workflow.

Do not turn Provider Registry connection tests into agent authority. Provider/model choice remains implementation only.

### Multi-agent readiness

Once at least two internal agents have assignments, existing multi-agent session topology can later execute comparison/review/debate across same-provider or cross-provider models. Each participant retains its own identity and authority; permissions never union.

### External MCP identity relationship

The existing ChatGPT custom MCP connection is an external runtime/client. Do not auto-invent its named `AI_AGENT` identity. If Owner wants “the MCP agent” represented in Agent Management, add an explicit Owner-controlled bind/link from the registered external client/grant to a named external agent principal.

### F7.2D4 exit criteria

Pass when:

1. Owner can assign a primary enabled provider/model to an internal agent;
2. assignment survives rename without changing `agent_id`;
3. agent card shows actual provider/model after assignment;
4. invalid/disabled provider or missing model is rejected;
5. known capability mismatch is rejected and unknown capability is explicitly represented;
6. ordered fallback configuration is durable;
7. canonical identity context is assembled server-side for invocation;
8. at least one configured provider/model can pass a narrow real inference probe when Owner supplies credentials through Web UI;
9. provider/model changes do not alter authority;
10. no production inventory write, workbook import, or canonical promotion occurs.

## 9. F7.3 and later

After F7.2D4:

- F7.3 actor-aware Audit / operation ledger
- F7.4 Inventory Locations / Store Policy / Preferences
- F7.5 Smart Calculator / receipts, calculation-only first
- F7.6 deterministic Smart Analysis
- F7.7 internal read-only AI Assistant
- F7.8 Alerts & Notifications
- F9 controlled typed writes only after authority/audit/location/idempotency prerequisites
- F10 real workflow + fresh migration + Sheet sync validation
- F11 explicit canonical promotion

## Immediate execution boundary

Proceed next with **F7.2D4 internal model assignment/fallback/runtime identity**.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deduction, Telegram/Flutter stock mutation, Sheet mirror conversion, or PostgreSQL canonical promotion during F7.2D4.