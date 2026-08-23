# F7.2D — Execution Path Separation

Status: **canonical architecture invariant — locked 2026-08-23**

## Purpose

Prevent MCP, internal provider-backed agents, Web chat, future Telegram/Flutter clients, and system automations from being accidentally collapsed into one execution path.

MSA has one typed backend/authority core and multiple peer ingress/runtime paths. No peer path is required to transit through another unless an explicit orchestration workflow calls for it.

## Canonical invariant

`client/runtime != agent identity != provider/model != typed backend operation`

The MSA core owns typed domain operations, authorization, policy, validation, persistence, read-back, and audit semantics. Adapters and runtimes call that core under their own authenticated/effective authority.

## Peer execution paths

### 1. External MCP / ChatGPT path

`ChatGPT model -> MSA MCP action -> MCP authority gate -> typed MSA backend operation -> data/service -> result`

This path is already proven in production. A bound external MCP agent may directly invoke an implemented MCP action when its OAuth/client scope, named-agent capability, operation policy, and system gate permit it.

The external MCP path does **not** require an internal provider-backed agent as an intermediary.

Example already verified:

`ChatGPT/SOL -> msa_shadow_read_rows -> shadow-read backend -> PostgreSQL shadow data -> result`

The corresponding Audit event records the bound external named agent and MCP transport. The backend operation may access PostgreSQL internally, but MCP never receives arbitrary SQL/table access or raw database credentials.

### 2. Native internal-agent path

`MSA Web chat / future Telegram / Flutter / automation -> native internal-agent runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> data/service -> model response`

An `INTERNAL_MODEL` agent is a first-class MSA runtime. It must continue to function independently of ChatGPT and independently of the MCP transport, subject only to its own provider availability, MSA backend availability, and configured authority.

The survival goal requires that MSA can operate its own named provider-backed agents from MSA-owned interfaces even when ChatGPT is unavailable.

### 3. Direct non-AI client path

`MSA Web/API client -> typed backend API -> authority gate -> typed MSA backend operation`

A normal Web/API workflow does not need an AI agent merely because AI functionality also exists in the product.

### 4. System automation path

`SYSTEM_AUTOMATION -> configured policy/agent/runtime -> typed MSA backend operation`

Scheduled/system jobs remain separate principals/runtimes and never inherit authority from MCP or another agent by accident.

## Shared typed backend, not chained transports

The desired layering is:

```text
                         MSA CORE
            Authority + typed domain operations
                         |
       +-----------------+-----------------+
       |                 |                 |
   MCP adapter        Web/API       Internal-agent tools
       |                                   |
 ChatGPT/SOL                         Provider/model runtime
                                           |
                              MSA Web chat / Telegram / Flutter
```

MCP tools, Web/API endpoints, and internal-agent tools should reuse the same domain/service functions wherever practical. They must not call each other merely to reach the same business operation.

In particular:

- internal agents do not call the public MCP endpoint to access MSA data;
- MCP does not call an internal agent just to execute an action the external model can execute directly;
- Web/API does not route through MCP for ordinary backend operations;
- business rules and authorization remain in shared backend services rather than being duplicated in each adapter.

## `msa_agent_invoke` semantics

`msa_agent_invoke` is an **optional delegation/orchestration bridge**, not the central gateway to MSA operations.

Appropriate use:

`External MCP model -> msa_agent_invoke -> selected INTERNAL_MODEL agent -> independent analysis/result`

Examples:

- ask an internal Inventory Analyst for an independent review;
- delegate a specialist reasoning task;
- compare the external model's conclusion with one or more internal agents;
- initiate an internal multi-agent review/debate workflow.

Inappropriate use:

`External MCP model -> msa_agent_invoke -> internal agent -> msa_shadow_read_rows`

when the external MCP model already has authorized direct access to `msa_shadow_read_rows` and no independent internal-agent reasoning is required.

Direct MCP actions remain the default for actions the external model is authorized to perform itself.

## Authority separation

Authority is evaluated per path/principal.

### External MCP named agent

`effective_authority = OAuth/client capability ∩ external-agent capability scope ∩ location scope ∩ operation policy ∩ system gate`

### Internal provider-backed agent

`effective_authority = invoking human/session/autonomous policy ∩ internal-agent capability scope ∩ location scope ∩ operation policy ∩ system gate`

Provider/model assignment never grants authority.

An external MCP agent and an internal agent may intentionally have different permissions even if they share a human-friendly name or purpose.

## Native agent product goal

MSA must support multiple durable internal agents, each with stable identity and independent provider/model assignment. The MSA-owned chat surface must support selecting the target agent and conversing with it without requiring ChatGPT.

Expected product direction:

- create multiple `INTERNAL_MODEL` agents;
- assign primary provider/saved model and optional fallbacks;
- persist conversations/messages;
- Web AI Chat agent selector;
- native single-agent inference;
- internal typed-tool execution under that agent's authority;
- reusable `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` execution;
- future Telegram/Flutter access to the same native runtime;
- optional MCP -> internal-agent delegation through the already-published schema slots.

## Implementation consequence for F7.2D4

F7.2D4 must build the native provider-backed agent runtime as a backend service independent of MCP. The MCP `msa_agent_invoke` action may later become one adapter into that runtime, but it must never become the runtime itself.

Recommended order:

1. durable assignment/fallback contract;
2. native internal-agent invocation service;
3. canonical identity injection and provider execution;
4. conversation/message persistence;
5. MSA Web AI Chat with agent selection;
6. internal typed-tool adapter over shared domain services;
7. fallback/failover and provider/model provenance;
8. multi-agent execution;
9. optional MCP-to-internal-agent delegation adapter;
10. acceptance with ChatGPT completely out of the loop: MSA Web -> selected internal agent -> provider/model -> authorized typed MSA read -> response/audit.

## Non-goals / forbidden architecture drift

Do not:

- make internal-agent survival depend on ChatGPT availability;
- make internal agents depend on the MCP server as their data/tool gateway;
- force direct MCP actions through internal agents;
- equate a model/provider with an agent identity;
- equate an MCP client/grant with an internal provider-backed agent;
- let assignment/provider changes alter authority;
- expose arbitrary SQL, DB credentials, shell/filesystem, or secret-bearing infrastructure to any AI path.

## Continuity enforcement

Any future implementation or documentation change that implies MCP is the required gateway for native internal agents, or that direct MCP actions must transit through an internal agent, conflicts with this document and must be corrected before merge.
