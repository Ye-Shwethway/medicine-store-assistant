# F7.2D4.7A — Native Agent Tool-Calling Refinement

Status: IMPLEMENTING
Date: 2026-08-23

## Problem proven by live testing

The first safe native-read slice used deterministic keyword routing. The backend selected a read tool from the current user message, executed it, and injected an `MSA NATIVE READ RESULTS` block into the model prompt. This is useful as a low-latency fast path but is not a complete agent tool runtime: follow-up requests such as "investigate this" can require fresh store evidence even when the current message contains no routing keyword.

## Locked architecture

Keep both paths:

1. Fast path — explicit supported intent -> deterministic native read prefetch -> model answer.
2. Agentic path — when fast-path evidence is absent, a tool-capable internal model receives every currently implemented and backend-authorized native tool definition, may request tools, receives typed results, and then returns a grounded final answer.

Native internal agents do not call the public MCP server. Native tool definitions are adapters over shared MSA backend/database services. The external MCP 106-action manifest remains a peer client surface, not the internal-agent tool gateway.

## Authority boundary

Tool visibility is not tool authority. The backend decides which tool schemas are exposed for the current invocation and validates every requested tool name before execution.

Current safe rollout:

- selected agent must have READ capability and at least READ authority ceiling;
- Owner sessions may execute the current native read-tool set;
- non-Owner Chat remains reasoning-only for native store tools until human/location authority intersection is implemented;
- production write/control tools remain unavailable;
- unknown or non-exposed tool requests never execute;
- public MCP is never used for native tool execution.

## Initial native tool set

Expose all currently implemented bounded native read tools when authorized:

- `inventory_summary`
- `new_unmapped_rows`
- `review_reasons`

The registry is designed to expand as typed native adapters are implemented. Do not imply that all 106 public MCP actions are native internal tools.

## Provider behavior

For OpenAI-compatible saved models that advertise tool support, use a bounded native tool-calling loop. The model may request one or more exposed tools; the backend executes allowlisted tools and returns results to the same model. Limit tool rounds to prevent unbounded loops.

For models/providers without supported native tool-calling semantics, retain deterministic fast-path prefetch and grounded reasoning-only fallback. Never fabricate tool execution.

## Provenance

Persist:

- tools exposed;
- deterministic fast-path tools requested/executed;
- model-requested tools and arguments;
- backend tool results/execution status;
- provider/model attempt chain;
- whether public MCP was used (must remain false).

## Acceptance

1. Explicit `NEW_UNMAPPED`/inventory requests still use the deterministic fast path.
2. A contextual follow-up such as "investigate this further" can cause a tool-capable internal model to request an authorized native read tool even without a current-message keyword.
3. The model sees the full currently authorized native read-tool registry, not an arbitrary subset chosen by the model.
4. Every model-requested tool is allowlisted and authority-checked server-side before execution.
5. Non-Owner sessions cannot execute native store tools in this slice.
6. No public MCP call occurs.
7. No production inventory write/canonical promotion occurs.
