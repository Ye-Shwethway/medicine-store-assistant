# F7.2D — AI Agent Management, Provider Registry & Delegated Authority

Status: **approved architecture direction; implement after F7.2A/B/C and before broad AI writes**

## Purpose

Medicine Store Assistant must support multiple AI execution paths without tying authority to one model vendor or one client. The same backend policy must govern internal provider-backed agents, Custom GPT Actions, future Telegram/Flutter AI features, scheduled jobs, and other external integrations.

AI Agent Management is therefore a separate **Owner-only control plane** for named AI/service principals. Human users, AI agents, provider connections, models, and external clients are different concepts and must not be collapsed into one table or one role system.

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

A client such as a Custom GPT, Telegram bot, Flutter client, Web AI Chat, integration, or future external service. External clients call typed MSA APIs and do not receive raw database credentials.

**Custom GPT is an external Action client/runtime, not a model provider.**

## Runtime modes

F7.2D supports three execution patterns under the same authority engine:

1. `INTERNAL_MODEL` — the MSA backend invokes an assigned provider/model.
2. `EXTERNAL_ACTION_CLIENT` — an external agent/client such as a Custom GPT invokes the MSA typed API.
3. `SYSTEM_AUTOMATION` — a future scheduled/background workflow executes under an Owner-configured autonomous policy.

Runtime mode does not define authority. Authority is always derived from registered principal/policy state.

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

## External Custom GPT Action path

The first F7.2D implementation proof is deliberately the external Custom GPT Action path.

Architecture:

`Custom GPT -> HTTPS Action -> MSA typed API -> external-client credential -> agent/capability policy -> deterministic read service -> response`

The Custom GPT receives **no direct PostgreSQL credential** and no generic SQL endpoint.

The first proof is read-only and should expose the smallest useful typed API surface, for example:

- service/agent identity check;
- current test/shadow inventory summary;
- bounded item lookup or another already-authorized read endpoint.

The proof must demonstrate that a Custom GPT can authenticate to `inventory.drthorne.uk`, invoke the Action from GPT Preview/normal use, receive real MSA backend data, and be denied outside its registered capability scope.

Current OpenAI GPT Actions support OpenAPI schemas and API-key or OAuth authentication. For the first single-Owner server-to-server proof, use a revocable scoped API/service credential unless a concrete requirement forces OAuth. OAuth may be introduced later when per-human delegated identity is required.

## Owner-only control plane

Only `OWNER` may:

- create/register AI agent principals;
- create/configure/disable provider connections;
- provision/replace provider credential references;
- fetch/test provider models;
- assign primary/fallback models to internal agents;
- enable/disable/revoke an agent;
- grant/remove capabilities;
- change location scope;
- change authority ceiling or execution mode;
- change delegated/autonomous policy;
- register/revoke external Action clients/service credentials;
- configure which humans may use shared AI features.

An AI agent or external client may never modify its own grant, secret, authority ceiling, Owner/security policy, Provider Registry, Agent Management, or global Settings.

## Effective authority

For a human-delegated action:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

For an external service/client without a live human session:

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

The first Custom GPT Action proof is read-only.

## Audit direction

F7.3 must be able to record, as applicable:

- `agent_id`;
- external client/runtime type;
- provider/model assignment used for internal execution;
- `authorized_by_user_id` for delegated actions;
- capability/action invoked;
- location scope/target;
- reconciliation classification;
- validation/approval outcome;
- transaction/read-back outcome.

Secrets and unrestricted prompts are not operational audit payloads.

## Implementation order inside F7.2D

1. **F7.2D1 — Custom GPT Action read-only connectivity proof**: scoped external-client credential, minimal OpenAPI schema, typed read endpoint(s), real GPT invocation, capability denial test.
2. **F7.2D2 — AI agent principal/control-plane foundation**: agent lifecycle, capability and location policy, external-client registration.
3. **F7.2D3 — Provider Registry + model catalog**: OpenAI, Gemini, OpenRouter, NanoGPT, generic OpenAI-compatible provider; secret references; test/fetch/save.
4. **F7.2D4 — Internal model assignment**: primary/fallback models, capability-aware assignment, test agent.
5. F7.3 actor-aware Audit / operation ledger.
6. Later read-only AI Assistant and richer external integrations.
7. Write capabilities only through later explicitly authorized controlled-write slices.

## F7.2D exit criteria

- Custom GPT Action can read authorized MSA data through the public typed API and cannot access ungranted operations;
- Owner can manage named AI agents separately from human users;
- Owner can configure built-in or custom OpenAI-compatible providers without hard-coded model IDs;
- model fetch/test/save/assign works for supported provider types;
- provider/model changes do not change agent authority;
- non-Owner cannot access Agent Management/Provider Registry;
- no AI principal can self-escalate;
- no production inventory write authority is enabled merely by completing F7.2D.
