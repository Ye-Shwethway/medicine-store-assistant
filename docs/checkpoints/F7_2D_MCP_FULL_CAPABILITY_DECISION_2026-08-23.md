# F7.2D MCP Full-Capability Decision — 2026-08-23

## Decision

The custom MSA MCP service will be built once as a **full-capability typed MCP schema** rather than as a permanently read-only server.

The initial deployed principal will still receive only currently authorized read capabilities. Future write/admin/control-plane capabilities are activated through MSA backend policy and project-slice gates rather than by rebuilding or reconnecting the MCP app.

Canonical rule:

`full MCP schema + progressive policy activation`

## Why

Custom MCP setup/connector configuration is relatively costly to repeat. The project prefers a stable long-lived tool catalog so future functionality can be unlocked by backend policy without repeated connector recreation.

This also separates three concepts that must not be conflated:

1. server/tool schema capability;
2. MSA execution authority;
3. ChatGPT client/plan/workspace capability.

A write tool may exist in the MCP catalog while MSA policy denies it, or while the active ChatGPT environment cannot invoke modify/write actions.

## Research checkpoint

Current external documentation reviewed on 2026-08-23 supports the following design assumptions:

- current MCP 2026-07-28 direction uses a stateless core;
- remote MCP deployment is HTTPS/Streamable-HTTP compatible;
- tool schemas support JSON Schema 2020-12 and structured outputs;
- tool annotations include `readOnlyHint`, `destructiveHint`, `idempotentHint`, and `openWorldHint`;
- MCP authorization uses protected-resource metadata/resource binding where OAuth is used;
- ChatGPT custom MCP write/modify support is product/plan/workspace dependent and may require confirmations/action controls;
- custom-app tool changes may require refresh/review, which strengthens the case for stable upfront namespaces.

Implementation must re-check the then-current OpenAI and MCP requirements immediately before coding.

## Locked server boundary

The MCP service may expose typed namespaces for:

- identity/system;
- inventory reads;
- catalogue reads;
- reconciliation/proposals;
- future typed inventory writes;
- transfers/calculator;
- analysis;
- Owner-only User Management;
- Owner-only AI Agent Management;
- Owner-only Provider Registry/model management;
- audit reads;
- typed Owner Settings.

It must never expose generic/raw infrastructure access such as SQL, arbitrary DB/table mutation, SSH, filesystem access, plaintext secrets, arbitrary environment editing, or a generic HTTP proxy.

## Write authority remains closed

This decision does **not** authorize:

- production inventory writes;
- AI inventory writes;
- transfers;
- Calculator deductions;
- Sheet mirror conversion;
- canonical DB promotion.

Those operations remain blocked until their explicit future implementation/authorization slices.

## Initial F7.2D0 proof

The first runtime proof deploys the full schema but grants only current read capabilities. ChatGPT must prove:

- connector/tool discovery;
- authenticated identity;
- system status;
- real inventory summary read;
- denial of a discoverable but ungranted write/control-plane tool;
- credential/client revocation;
- connector survival across service restart/redeploy.

If ChatGPT cannot perform write actions because of its current plan/workspace, record that separately from server capability and MSA policy.

## Next implementation order

1. F7.2D0 full-capability MCP server/schema + read-grant proof.
2. AI agent/external-client principal control plane.
3. Provider Registry/model catalog.
4. internal model assignment/fallbacks.
5. optional Custom GPT Action proof only if still needed.
6. F7.3 actor-aware operational Audit.
7. later controlled capability activation through explicit project slices.
