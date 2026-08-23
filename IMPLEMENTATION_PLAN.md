# Medicine Store Assistant — Implementation Plan

Status: **F7.2A/B/C, F7.2D0 custom MCP connectivity, and F7.2D2 named Agent Management/multi-agent session foundation are verified complete; F7.2D3 Provider Registry + model catalog is the next authorized slice; production inventory write authority remains unauthorized**

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

Owner may later preauthorize narrow SAFE workflow classes; REVIEW/CONFLICT/NEW_UNMAPPED and high-risk/control-plane cases remain review boundaries.

## 3. Verified foundation

Verified complete:

- F0/F1/Cloudflare/F2/F3/F4/F5/F5.1/F6A/F6C
- F7.1 read-only Dashboard
- F7.2A canonical human identity/sessions
- F7.2B User Management/profile
- F7.2C Credential + Recovery Lifecycle
- F7.2D0 custom MCP full-schema/OAuth connectivity
- F7.2D2 named Agent Management + multi-agent session topology

F6B remains test-only:

- 1,646 rows
- SAFE 1,417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7
- `migration_baseline_accepted=false`
- `database_canonical=false`

## 4. F7.2D0 — verified custom MCP foundation

Custom MCP is the verified primary ChatGPT access path.

Verified route:

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> typed backend`

Current granted external-client scopes:

- `mcp:connect`
- `mcp:read`
- `offline_access`

Propose/write/control remain disabled.

The durable MCP server exposes a full typed schema, but backend policy/system gates define actual authority. Connector rebuild is not required merely to unlock future typed grants.

Custom GPT Actions are optional/fallback only.

## 5. F7.2D2 — VERIFIED COMPLETE

Canonical design: `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`

Checkpoint: `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`

Runtime evidence:

- PR #58
- merge `3b385a37b95c1ff79f76883381d8268fa6c49db2`
- deploy run `32620386876`
- job `97147568336`
- migration `0010_mcp_oauth -> 0011_ai_agents`
- issue #26 `status=success`

Implemented:

- Owner-only `AI Agent Management`;
- stable immutable `agent_id`;
- editable `display_name`;
- case-insensitive unique `call_name`;
- deterministic self-identity context preview;
- runtime mode/lifecycle/capability/location/authority/execution/confirmation metadata;
- disable/reactivate/revoke;
- non-Owner 403 and public anonymous 401;
- persistent multi-agent sessions;
- `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` topology modes;
- ordered participants and optional role labels;
- session close/reopen;
- provider/model inference explicitly disabled.

Runtime verifier passed named identity, stable ID across rename, self-identity context, call-name uniqueness, session persistence/order, lifecycle guards, and inference-disabled checks.

### Identity rule

Agent identity is server-owned configuration, not conversational memory.

F7.2D4 runtime invocation assembly must inject canonical identity on each internal-agent call, using at least `display_name` + stable `agent_id`. Changing provider/model must never change agent identity.

## 6. Web UI workflow — current canonical rule

Default Web path:

`UI/UX Pro Max -> design-system/medicine-store-assistant/MASTER.md + page override -> authenticated API contract -> direct code implementation -> responsive/accessibility/runtime verification`

Figma is optional and not a normal implementation prerequisite. Use it only when the Owner explicitly requests it or a task genuinely requires it.

## 7. F7.2D3 — Provider Registry + model catalog — NEXT

Purpose: let Owner configure model-provider connections without coupling authority to vendor/model identity.

### Provider presets

- OpenAI
- Google Gemini
- OpenRouter
- NanoGPT
- generic `OPENAI_COMPATIBLE`

### Required data separation

- `provider_connection` = API endpoint/configuration/secret reference
- `model_catalog_entry` = provider-local model resource/capability metadata
- `AI_AGENT` = durable identity/authority boundary

Provider/model must never be treated as authority.

### Provider connection fields

At minimum:

- stable `provider_id`;
- Owner-defined display name;
- provider kind/preset;
- base URL where applicable;
- credential/secret reference only, never plaintext DB key;
- optional non-secret compatibility configuration;
- enabled/disabled state;
- connection-test status/timestamps;
- model-fetch status/timestamps;
- provenance.

### Generic OpenAI-compatible security

Custom base URLs require SSRF protections:

- HTTPS by default in production;
- reject loopback/link-local/cloud-metadata/private destinations unless separately and explicitly authorized by architecture;
- protect redirects to forbidden destinations;
- re-resolve/check destinations where practical to mitigate DNS rebinding;
- sanitize and bound provider responses.

### Credential policy

Provider API keys are write-only from the Owner UI.

Persistent DB records store `credential_ref` or equivalent non-secret metadata, never plaintext secret value.

The browser must never receive provider-key read-back. Logs/errors must redact auth headers/tokens.

### Owner workflow

`Add provider -> provision credential -> Test connection -> Fetch models -> inspect capabilities -> Save/enable`

Required operations:

- add/edit provider metadata;
- provision/replace credential securely;
- test provider connection server-side;
- fetch models dynamically;
- normalize model metadata/capabilities;
- disable/reactivate provider;
- refresh models manually.

### Model catalog

Track where available:

- provider-local model ID;
- display name;
- discovery/refreshed timestamps;
- availability;
- text capability;
- vision capability;
- tool/function calling;
- structured output/JSON;
- context/output limits;
- other verified provider metadata.

Unknown capability remains unknown; do not infer or fabricate support merely from model names.

### F7.2D3 non-scope

- assigning models to agents;
- running agent inference;
- multi-agent orchestration;
- production inventory mutation;
- F7.3 operational audit implementation;
- DB canonical promotion.

### F7.2D3 exit criteria

Pass when:

1. Owner-only Provider Registry exists;
2. non-Owner access is 403;
3. built-in provider presets + generic OpenAI-compatible are supported;
4. provider secret is persisted only through protected runtime secret/reference mechanism;
5. connection test works server-side without secret exposure;
6. dynamic model fetch works for at least one configured provider;
7. fetched model catalog is persisted/refreshed with bounded normalized metadata;
8. unknown capabilities remain unknown;
9. provider disable/credential replacement works;
10. no agent authority changes merely because provider/model config changes;
11. no provider/model inference required for completion beyond explicit connection/model test probes;
12. no inventory mutation/workbook import/canonical promotion occurs.

## 8. F7.2D4 — Internal model assignment/fallbacks

After F7.2D3:

- assign primary provider/model to named agent;
- optional ordered fallback chain;
- capability compatibility checks;
- timeout/output policy;
- optional usage/cost metadata;
- inject canonical agent self-identity every invocation;
- enable future multi-agent session execution/comparison.

Fallback must never expand capability/location/operation authority or silently substitute incompatible semantics.

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

Proceed next with **F7.2D3 Provider Registry + model catalog**.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deduction, Telegram/Flutter stock mutation, Sheet mirror conversion, or PostgreSQL canonical promotion during F7.2D3/F7.2D4.
