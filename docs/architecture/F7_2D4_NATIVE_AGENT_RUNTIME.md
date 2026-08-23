# F7.2D4 — Native Internal-Agent Runtime

Status: **next active architecture slice**

## Purpose

Build MSA-owned provider-backed agents that operate independently of ChatGPT and independently of the public MCP transport.

This document complements `F7_2D_EXECUTION_PATH_SEPARATION.md` and must not override its peer-path invariant.

## Execution path

`MSA Web / future Telegram / Flutter / automation -> native agent runtime -> assigned provider/model -> internal typed-tool adapter -> shared typed MSA domain services -> response/audit`

MCP remains a peer external path. `msa_agent_invoke` is optional delegation into this native runtime after the runtime exists.

## D4.0 preflight

Before native execution work:

- verify persisted agent capability/authority policy is not UI-only;
- keep external MCP effective-authority enforcement intact;
- enforce Provider/Saved model controls only for `INTERNAL_MODEL` agents in both UI and backend;
- preserve production write gates closed.

## D4.1 assignment/fallback contract

Extend the current single primary assignment foundation into:

- stable assignment identity;
- one primary enabled provider + Owner-saved healthy model;
- ordered optional fallbacks;
- capability expectations;
- timeout/max-output policy;
- optional usage/cost budget metadata;
- enabled/disabled state and provenance.

Provider/model/fallback changes never modify `agent_id` or authority.

## D4.2 native invocation service

Create a backend service callable without MCP:

`caller -> resolve internal agent -> resolve assignment -> inject canonical identity/policy -> provider call -> normalize -> provenance/audit -> response`

No ChatGPT or public MCP dependency is allowed.

## D4.3 conversations

Persist MSA-owned conversations/messages with selected internal agent, human/session ownership, roles, timestamps, lifecycle, and provider/model provenance where relevant.

## D4.4 Web AI Chat

Provide a mobile-first MSA-owned chat interface with agent selector, new/resume conversation, history, selected agent identity/state/provider/model display, and native provider-backed responses.

## D4.5 internal typed tools

Internal agents use an internal typed-tool adapter over shared MSA domain services. They do not call the public MCP endpoint for ordinary data/tool access.

Effective authority is evaluated under the internal agent and invoking human/session/autonomous policy. Initial proof remains bounded read-only.

## D4.6 failover

Execute only the approved ordered fallback chain. Record selected provider/model, fallback use/reason, latency, and available usage/cost metadata. No silent arbitrary substitution.

## D4.7 multi-agent execution

Activate persisted `GROUP`, `COMPARE`, `REVIEW`, and `DEBATE` topology. Each participant retains separate identity, assignment, and authority; permissions never union.

## D4.8 optional MCP delegation

Only after the native runtime exists may `msa_agent_invoke` and session MCP slots delegate to selected native agents. Direct MCP actions remain direct.

## Acceptance

Required survival proof with ChatGPT completely out of the path:

`MSA Web -> selected INTERNAL_MODEL agent -> provider/model -> authorized typed MSA read -> response + audit`

Production inventory writes, workbook import, and canonical DB promotion remain out of scope.
