# F7.2D — AI Agent Management, MCP Access, Provider Registry & Delegated Authority

Status: **approved architecture direction; implement after F7.2A/B/C and before broad AI writes**

## Purpose

Medicine Store Assistant must support multiple AI execution paths without tying authority to one model vendor or one client. The same backend policy must govern ChatGPT through a custom MCP connection, internal provider-backed agents, optional Custom GPT Actions, future Telegram/Flutter AI features, scheduled jobs, and other external integrations.

AI Agent Management is therefore a separate **Owner-only control plane** for named AI/service principals. Human users, AI agents, provider connections, models, and external clients are different concepts and must not be collapsed into one table or one role system.

The first implementation objective is now to prove the **custom MCP path** end-to-end. Custom GPT Actions remain an optional secondary external-access path and are no longer required before Agent Management/provider work can continue.

## Canonical separation

### Human user

A canonical person with stable `user_id`, username/password credentials, human role, account state, and sessions.

### AI agent

A named `AI_AGENT` principal with stable `agent_id`, capabilities, location scope, authority ceiling, execution policy, and lifecycle state. An agent is the identity/policy boundary; it is not a model vendor account.

### Provider connection

A configured model API connection. A provider connection answers: which vendor/endpoint can MSA call, with which runtime-secret credential reference and provider adapter?

### Model

A model resource discovered or configured under a provider connection. Model identity and capability metadata are separate from agent authority.

### External client/runtime

A client/runtime such as ChatGPT through a custom MCP connector, an optional Custom GPT Action client, Telegram bot, Flutter client, Web AI Chat, integration, or future external service. External clients call typed MSA capabilities and do not receive raw database credentials.

**Custom MCP and Custom GPT are access/runtime paths, not model providers.**

## Runtime modes

F7.2D supports four execution patterns under the same authority engine:

1. `EXTERNAL_MCP_CLIENT` — ChatGPT or another MCP-capable client invokes typed MSA tools through the remote MCP service.
2. `INTERNAL_MODEL` — the MSA backend invokes an assigned provider/model.
3. `EXTERNAL_ACTION_CLIENT` — an optional external agent/client such as a Custom GPT invokes the MSA typed HTTPS API through an Action.
4. `SYSTEM_AUTOMATION` — a future scheduled/background workflow executes under an Owner-configured autonomous policy.

Runtime mode does not define authority. Authority is always derived from registered principal/policy state.

## Custom MCP path — primary external-access direction

The preferred first external access path is a custom remote MCP service hosted on the MSA VPS.

Conceptual architecture:

`ChatGPT Developer Mode -> HTTPS remote MCP -> MSA MCP adapter -> scoped external-client identity -> capability policy -> existing deterministic read services -> PostgreSQL/test-shadow reads`

The MCP layer is a protocol adapter, not a second business-logic implementation and not a raw database gateway.

The MCP service must never expose:

- PostgreSQL credentials;
- arbitrary SQL execution;
- arbitrary table browsing;
- VPS shell/SSH access;
- Google Sheet credentials;
- provider API keys;
- unrestricted internal admin functions.

The first proof is read-only and intentionally small. Suggested initial tools:

- `msa_whoami` — returns external-client identity/state/granted capabilities without secret material;
- `get_system_status` — returns bounded service/canonicality status;
- `get_inventory_summary` — returns the current authorized test/shadow inventory summary and canonicality flags;
- optional bounded `search_inventory` / `get_inventory_item` after basic connectivity is proven.

The remote MCP transport should be hosted as a small deployable service on the VPS and may use either a dedicated subdomain or a stable HTTPS path. Exact route choice is an implementation detail, but the public endpoint must be TLS-protected and independently revocable without exposing the database.

### MCP service boundary

Prefer a small separate MCP adapter/service rather than embedding MCP protocol details directly into inventory business logic. The adapter may reuse existing backend service functions or typed API contracts.

Reasons:

- MCP protocol/runtime changes remain isolated from core inventory API behavior;
- connection/debug/deploy failures are easier to localize;
- MCP credentials and capability policy can be revoked independently;
- future clients can reuse the same typed operations without duplicating business rules.

This separation is architectural, not an excuse to duplicate data-access logic.

### MCP authentication

The first proof uses one named, scoped, revocable external-client credential unless current ChatGPT MCP connection requirements force a different supported auth mechanism.

Requirements:

- high-entropy credential;
- plaintext secret shown/provisioned only at issuance;
- server-side digest/verifier or secret-reference storage only;
- client state `ACTIVE` / `REVOKED`;
- explicit capability allowlist;
- missing/invalid credential denied;
- valid credential without requested capability denied;
- revocation blocks later MCP calls immediately;
- no secret values in Git, logs, audit payloads, docs, or browser storage.

At implementation time, re-check current OpenAI/ChatGPT MCP authentication and Developer Mode requirements before choosing the exact connector authentication configuration.

## F7.2D0 — MCP connectivity proof

The first implementation slice inside F7.2D is **F7.2D0 Custom MCP Read-Only Connectivity Proof**.

It passes only when the real ChatGPT Developer Mode connection can invoke the deployed MSA remote MCP service and receive current authorized MSA data.

Minimum proof:

1. deploy a small remote MCP endpoint on the VPS;
2. register one scoped external MCP client/credential;
3. verify transport/health locally and through public HTTPS;
4. connect the custom MCP server from ChatGPT Developer Mode;
5. prove `msa_whoami` from ChatGPT;
6. prove a real `get_inventory_summary` read from ChatGPT;
7. preserve `database_canonical=false`, `migration_baseline_accepted=false`, and F6B test-only boundaries in relevant results;
8. prove a deliberately ungranted capability is denied;
9. revoke the MCP client/credential and prove a subsequent ChatGPT invocation fails;
10. confirm no inventory mutation/provider model call/workbook import occurs.

If ChatGPT cannot connect because of current MCP product/auth/network restrictions, document the exact constraint immediately. Do not weaken MSA security to force the proof to pass.

## Optional Custom GPT Action path

Custom GPT Actions remain a valid secondary external path but are no longer the first required proof.

Architecture:

`Custom GPT -> HTTPS Action -> MSA typed API -> external-client credential -> capability policy -> deterministic service -> response`

If MCP proves reliable and gives sufficient ChatGPT access/freedom for the intended workflow, the project may defer or omit the Custom GPT Action path unless a concrete product need appears.

The existing `F7_2D1_CUSTOM_GPT_ACTION_PROOF.md` remains as the optional Action proof contract.

## AI agent principal model

Representative fields/configuration:

- stable `agent_id`;
- display name and description;
- runtime mode;
- `ACTIVE` / `DISABLED` / `REVOKED` state;
- allowed typed capabilities;
- allowed store/location scope;
- authority ceiling;
- delegated vs autonomous policy;
- write-confirmation policy;
- allowed human users/roles for shared features where applicable;
- current provider/model assignment for `INTERNAL_MODEL` agents;
- revocable external/service credential reference where applicable;
- created/updated/disabled audit provenance.

Human roles remain `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`. AI agents never receive those human roles.

## Provider Registry

The Owner-only provider surface supports first-class adapters for a small set of well-known providers and a generic OpenAI-compatible adapter for the long tail.

### Built-in provider presets

Initial direction:

- OpenAI;
- Google Gemini;
- OpenRouter;
- NanoGPT.

These are first-class presets because their model discovery, request formats, capability metadata, and operational behavior may differ.

### Custom provider

`OPENAI_COMPATIBLE` supports additional OpenAI-compatible services without adding a new hard-coded adapter for every vendor.

Representative configuration:

- Owner-defined provider name;
- base URL;
- credential reference;
- optional extra non-secret headers/config;
- models endpoint/path where supported;
- chat/responses compatibility mode;
- enabled/disabled state.

Provider API keys are secrets. Persistent application records store only a secret/credential reference or non-secret status metadata; plaintext provider keys must not be written to Git, audit logs, browser storage, model catalog rows, or ordinary application logs.

## Provider workflow

Canonical Owner workflow:

`Add provider -> provision credential -> Test connection -> Fetch models -> inspect capabilities -> Save/enable -> Assign model to agent`

Required operations:

- `Test connection` — validates credential/network/provider API behavior without creating an agent;
- `Fetch models` — refreshes the provider model catalog without hard-coded model IDs;
- `Test model` — performs a minimal model-level request and reports capability/compatibility failure separately from provider health;
- `Save/enable` — activates the provider connection only after explicit Owner action;
- `Assign` — links an internal agent to a selected primary model and optional fallback chain.

Provider health and agent health are separate. A provider can be reachable while an assigned model/tool contract is incompatible.

## Model catalog

Fetched/configured model records may retain:

- provider-local model ID;
- display name;
- discovered_at / refreshed_at;
- availability state;
- text support;
- vision/multimodal support;
- tool/function calling support;
- structured-output/JSON support where known;
- context/output limits where reliably available;
- provider-specific metadata payload as non-authoritative supplemental data.

MSA must not silently invent unsupported capabilities. Unknown capability metadata remains unknown until tested or supplied by authoritative provider metadata.

## Agent model assignment

`INTERNAL_MODEL` agents may have:

- one primary provider/model assignment;
- optional ordered fallback assignments;
- timeout/output-budget policy;
- optional cost/usage ceiling metadata;
- required model capability constraints.

Fallback is allowed only when the fallback satisfies the agent operation's required capabilities. A fallback model must never expand the agent's capability, location, or write authority.

Changing provider/model assignment changes runtime implementation, not `agent_id` or agent authority.

## Owner-only control plane

Only `OWNER` may:

- create/register AI agent principals;
- register/revoke external MCP clients and credentials;
- create/configure/disable provider connections;
- provision/replace provider credential references;
- fetch/test provider models;
- assign primary/fallback models to internal agents;
- enable/disable/revoke an agent;
- grant/remove capabilities;
- change location scope;
- change authority ceiling or execution mode;
- change delegated/autonomous policy;
- optionally register/revoke external Action clients/service credentials;
- configure which humans may use shared AI features.

An AI agent or external client may never modify its own grant, secret, authority ceiling, Owner/security policy, Provider Registry, Agent Management, or global Settings.

## Effective authority

For a human-delegated action:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

For an external MCP/Action client without a live human session:

`effective_authority = registered_client_scope ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

For autonomous/system execution:

`effective_authority = owner_configured_autonomous_policy ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

Provider/model selection never appears as an authority multiplier.

## Location scope

Agents are not inherently Sub-Store-only. The Owner may grant Main Store reads, selected/all Sub Store reads, all-store analytical reads, and later typed writes only after the corresponding controlled-write slice is explicitly authorized.

## MSA workflow parity

Preserve the established `$msa` operating model:

1. inspect source evidence;
2. reconcile against authoritative/current truth;
3. classify `SAFE`, `REVIEW`, `CONFLICT`, or `NEW_UNMAPPED`;
4. execute only within Owner-authorized typed operation scope;
5. surface ambiguity instead of guessing;
6. commit through deterministic backend operations;
7. read committed state back;
8. record actor/operation provenance;
9. report success only after verification.

Pre-authorized SAFE workflows may later run without per-row confirmation once production writes for that operation are separately authorized. REVIEW/CONFLICT/NEW_UNMAPPED and high-risk/control-plane operations remain human-review boundaries.

## Canonicality and write boundary

Google Sheets remains operationally authoritative and PostgreSQL remains non-canonical. F7.2D does **not** authorize production stock mutation, AI inventory writes, transfers, Smart Calculator deduction, Sheet mirror conversion, or DB canonical promotion.

The MCP connectivity proof is read-only.

## Audit direction

F7.3 must be able to record, as applicable:

- `agent_id`;
- external client/runtime type including MCP vs Action;
- provider/model assignment used for internal execution;
- `authorized_by_user_id` for delegated actions;
- capability/action invoked;
- location scope/target;
- reconciliation classification;
- validation/approval outcome;
- transaction/read-back outcome.

Secrets and unrestricted prompts are not operational audit payloads.

## Implementation order inside F7.2D

1. **F7.2D0 — Custom MCP read-only connectivity proof**: remote MCP service, scoped external-client credential, ChatGPT Developer Mode connection, `msa_whoami`, real inventory summary, denial/revocation tests.
2. **F7.2D2 — AI agent principal/control-plane foundation**: agent lifecycle, capability and location policy, external-client registration.
3. **F7.2D3 — Provider Registry + model catalog**: OpenAI, Gemini, OpenRouter, NanoGPT, generic OpenAI-compatible provider; secret references; test/fetch/save.
4. **F7.2D4 — Internal model assignment**: primary/fallback models, capability-aware assignment, test agent.
5. **Optional F7.2D1 — Custom GPT Action proof** only if MCP does not meet the product need or an Action-specific integration is later desired.
6. F7.3 actor-aware Audit / operation ledger.
7. Later read-only AI Assistant and richer external integrations.
8. Write capabilities only through later explicitly authorized controlled-write slices.

## F7.2D exit criteria

- ChatGPT through the custom MCP path can read authorized MSA data and cannot access ungranted operations;
- MCP credential/client revocation is effective;
- Owner can manage named AI agents separately from human users;
- Owner can configure built-in or custom OpenAI-compatible providers without hard-coded model IDs;
- model fetch/test/save/assign works for supported provider types;
- provider/model changes do not change agent authority;
- non-Owner cannot access Agent Management/Provider Registry;
- no AI principal can self-escalate;
- no production inventory write authority is enabled merely by completing F7.2D.
