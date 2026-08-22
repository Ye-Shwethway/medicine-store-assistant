# F7.2D — AI Agent Management, MCP Access, Provider Registry & Delegated Authority

Status: **approved architecture direction; implement after F7.2A/B/C and before broad AI writes**

## Purpose

Medicine Store Assistant must support multiple AI execution paths without tying authority to one model vendor or one client. The same backend policy must govern ChatGPT through a custom MCP connection, internal provider-backed agents, optional Custom GPT Actions, future Telegram/Flutter AI features, scheduled jobs, and other external integrations.

AI Agent Management is therefore a separate **Owner-only control plane** for named AI/service principals. Human users, AI agents, provider connections, models, and external clients are different concepts and must not be collapsed into one table or one role system.

The first implementation objective is the **custom MCP path**. Because remote custom-app configuration can be costly to repeat, the MCP server is now designed as a **full-capability typed schema from the start**. Read/write/admin/control-plane tool classes may exist in the catalog, while current backend policy grants only operations already authorized by the project.

Canonical rule:

`full transport/schema != full current authority`

Custom GPT Actions remain an optional secondary external-access path.

## Canonical separation

### Human user

A canonical person with stable `user_id`, username/password credentials, human role, account state, and sessions.

### AI agent

A named `AI_AGENT` principal with stable `agent_id`, capabilities, location scope, authority ceiling, execution policy, and lifecycle state. An agent is the identity/policy boundary; it is not a model vendor account.

### Provider connection

A configured model API connection. A provider connection answers which vendor/endpoint MSA can call, with which runtime-secret credential reference and provider adapter.

### Model

A model resource discovered or configured under a provider connection. Model identity/capability metadata is separate from agent authority.

### External client/runtime

A client/runtime such as ChatGPT through custom MCP, optional Custom GPT Action, Telegram, Flutter, Web AI Chat, integration, or future external service. External clients call typed MSA capabilities and never receive raw database credentials.

**Custom MCP and Custom GPT are access/runtime paths, not model providers.**

## Runtime modes

F7.2D supports four execution patterns under one authority engine:

1. `EXTERNAL_MCP_CLIENT` — ChatGPT or another MCP client invokes typed MSA tools through the remote MCP service.
2. `INTERNAL_MODEL` — MSA invokes an assigned provider/model.
3. `EXTERNAL_ACTION_CLIENT` — optional Custom GPT/other HTTPS Action client invokes typed MSA APIs.
4. `SYSTEM_AUTOMATION` — future scheduled/background workflow under Owner-configured autonomous policy.

Runtime mode never defines authority by itself.

## Custom MCP path — primary external-access direction

Conceptual architecture:

`ChatGPT Developer Mode -> HTTPS remote MCP -> msa-mcp adapter -> authenticated client/agent context -> capability + location + operation-policy + write/canonicality gates -> typed MSA services -> current backend/data boundary`

The MCP layer is a protocol adapter, not a second business-logic implementation and not a raw database gateway.

### Build once, activate progressively

The first long-lived MCP deployment should publish the stable tool namespaces needed across the planned MSA lifecycle, including read, proposal, write, User Management, Agent Management, Provider Registry, Audit and typed Settings operations.

A tool being discoverable does not authorize its execution. Future write/control-plane capabilities are enabled through backend policy and project-slice gates rather than rebuilding or reconnecting the MCP app.

Canonical companion document:

`docs/architecture/F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md`

### Explicitly forbidden generic access

Even a full-capability MSA MCP service must never expose:

- PostgreSQL credentials;
- arbitrary SQL execution;
- arbitrary table/column browsing or patching;
- VPS shell/SSH;
- generic filesystem access;
- Google Sheet credentials;
- plaintext provider API keys;
- unrestricted environment-variable editing;
- generic arbitrary HTTP proxying.

Full capability means full **typed MSA capability**, not unrestricted infrastructure access.

### MCP deployment boundary

Prefer a separate `msa-mcp` service/container behind the existing HTTPS reverse-proxy stack. MCP protocol/runtime changes stay isolated from inventory business logic, while the adapter reuses canonical typed backend service functions/contracts.

Current researched protocol direction as of 2026-08-23 includes:

- stateless MCP core in the 2026-07-28 specification;
- remote HTTPS/Streamable-HTTP-compatible deployment;
- JSON Schema 2020-12 tools/outputs;
- tool annotations including read-only, destructive, idempotent and open-world hints;
- current MCP authorization/protected-resource discovery where OAuth is used.

At implementation time, re-check the then-current MCP/OpenAI requirements before coding.

### MCP authentication

The long-lived service should be compatible with standards-based MCP authorization where the ChatGPT connection uses OAuth, including protected-resource metadata, audience/resource binding and scope validation.

For development/bootstrap or supported direct-token flows, MSA may also use a high-entropy revocable external-client credential.

In every mode:

- plaintext secrets are never persisted in Git/docs/logs;
- only digest/verifier/secret-reference material is retained;
- invalid/revoked clients fail;
- a valid client without capability fails;
- credential rotation must not require rebuilding the tool schema.

## F7.2D0 — Full-capability MCP connectivity proof

The first implementation slice deploys the permanent full-capability MCP schema but grants only currently authorized read capabilities to the initial external client.

Minimum proof:

1. deploy the remote MCP service on the VPS;
2. publish the stable full tool catalog;
3. authenticate one external MCP client;
4. connect/scan from ChatGPT Developer Mode;
5. prove `msa_identity_whoami`;
6. prove `msa_system_status`;
7. prove real `msa_inventory_read_summary`;
8. preserve `database_canonical=false`, `migration_baseline_accepted=false`, and F6B test-only state;
9. prove at least one discoverable but ungranted write/control-plane tool is denied by MSA policy;
10. revoke the client/credential and prove later calls fail;
11. prove service restart/deploy does not require connector redesign;
12. perform no production inventory mutation/provider call/workbook import during the proof.

If ChatGPT cannot use write actions because of plan/workspace/product limitations, record that as a client capability constraint rather than redesigning the server to read-only.

## AI agent principal model

Representative configuration:

- stable `agent_id`;
- display name/description;
- runtime mode;
- `ACTIVE` / `DISABLED` / `REVOKED` state;
- allowed typed capabilities;
- allowed store/location scope;
- authority ceiling;
- delegated vs autonomous policy;
- write-confirmation policy;
- allowed human users/roles for shared features;
- provider/model assignment for `INTERNAL_MODEL` agents;
- revocable external/service credential reference where applicable;
- created/updated/disabled provenance.

Human roles remain `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`; AI agents never receive those roles.

## Provider Registry

The Owner-only provider surface supports first-class adapters for a small set of well-known providers plus a generic OpenAI-compatible adapter.

Built-in presets:

- OpenAI;
- Google Gemini;
- OpenRouter;
- NanoGPT.

Generic provider:

- `OPENAI_COMPATIBLE` with Owner-defined name/base URL/credential reference and compatibility configuration.

Provider API keys remain runtime secrets. Persistent records store only secret references and non-secret provider/model metadata.

## Provider workflow

Canonical Owner flow:

`Add provider -> provision credential -> Test connection -> Fetch models -> inspect capabilities -> Save/enable -> Assign model to agent`

Required operations:

- test connection;
- fetch models without hard-coded model IDs;
- test model separately from provider health;
- save/enable;
- assign primary model;
- optional ordered fallback models.

Provider health and agent health are different concepts.

## Model catalog and assignment

Fetched/configured models may retain provider-local ID, display name, discovery timestamps, availability and known text/vision/tool/structured-output/context metadata. Unknown capabilities remain unknown rather than invented.

`INTERNAL_MODEL` agents may have primary/fallback model assignments, timeout/output-budget policy, optional cost metadata and required capability constraints. Fallback never expands agent authority.

Changing provider/model changes runtime implementation, not `agent_id` or authority.

## Owner-only control plane

Only `OWNER` may manage:

- AI agents/principals;
- MCP external clients/credentials;
- provider connections/credentials;
- model discovery/testing/assignment;
- agent capability/location/authority policy;
- delegated/autonomous policy;
- optional Action clients;
- shared AI-feature access policy.

An agent/client may never self-escalate or modify its own authority, Owner/security configuration, Provider Registry, Agent Management, or global Settings.

## Effective authority

Human-delegated action:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_write_gate`

External MCP/Action client without live human session:

`effective_authority = registered_client_scope ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_write_gate`

Autonomous/system execution:

`effective_authority = owner_configured_autonomous_policy ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_write_gate`

Provider/model selection is never an authority multiplier.

## MSA workflow parity

Preserve `$msa` semantics:

1. inspect evidence;
2. reconcile against authoritative/current truth;
3. classify `SAFE`, `REVIEW`, `CONFLICT`, `NEW_UNMAPPED`;
4. execute only within Owner-authorized typed scope;
5. surface ambiguity;
6. commit through deterministic backend operations;
7. read committed state back;
8. record actor/operation provenance;
9. report success only after verification.

Pre-authorized SAFE workflows may later run without per-row confirmation only after their corresponding production-write slices are explicitly authorized.

## Canonicality and write boundary

Google Sheets remains operationally authoritative and PostgreSQL remains non-canonical. Designing and publishing write-capable MCP tools does **not** authorize production stock mutation, AI inventory writes, transfers, Calculator deductions, Sheet mirror conversion, or DB promotion.

Current system write gates remain closed for those operations.

## Audit direction

F7.3 must capture, as applicable:

- agent/client ID and runtime type;
- human delegation context;
- provider/model for internal execution;
- capability/action;
- location;
- reconciliation classification;
- policy/approval outcome;
- transaction/read-back outcome.

Secrets and unrestricted prompt transcripts are not audit payloads.

## Optional Custom GPT Action path

Custom GPT Actions remain a valid secondary external path. If MCP proves reliable and sufficient, this path may be deferred or omitted unless a concrete standalone-GPT/distribution need appears.

## Implementation order inside F7.2D

1. **F7.2D0 — Full-capability MCP transport/schema + read-grant connectivity proof**.
2. **F7.2D2 — AI agent/external-client principal control plane**.
3. **F7.2D3 — Provider Registry + model catalog**.
4. **F7.2D4 — Internal model assignment/fallbacks**.
5. Optional **F7.2D1 — Custom GPT Action proof** only if needed.
6. F7.3 actor-aware Audit/operation ledger.
7. Later AI Assistant and richer integrations.
8. Write capabilities become executable only through later explicitly authorized slices and policy grants.

## F7.2D exit criteria

- ChatGPT custom MCP can discover the durable schema and execute authorized reads;
- ungranted write/control-plane tools are denied even if discoverable;
- MCP revocation works;
- Owner can manage named AI agents separately from humans;
- Owner can configure built-in/custom OpenAI-compatible providers without hard-coded model IDs;
- model fetch/test/save/assign works;
- provider/model changes do not alter authority;
- non-Owner cannot use Agent Management/Provider Registry;
- no AI principal self-escalates;
- no production inventory write is enabled merely by completing F7.2D.
