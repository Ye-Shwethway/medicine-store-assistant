# F7.2D4F — Grounded Chat + Native Read Tools

Date: 2026-08-23

## Acceptance evidence entering this slice

- AI Workspace single-agent Chat is live in production.
- Owner can create a conversation, receive provider-backed replies, refresh, and retain history.
- Multi-Agent remains Owner-only and not executable yet.
- Current Chat correctly reports that MSA typed tools are not attached.
- Mobile acceptance exposed two follow-ups: button/style drift and weak grounding for Burmese/general prompts.

## Architecture lock

- Native internal agents do **not** call the public MCP transport for ordinary store operations.
- MCP agents and native internal agents are peer execution paths over shared MSA backend/domain operations.
- This slice attaches read-only native typed adapters directly inside the MSA backend.
- Production inventory writes remain disabled.
- Agent authority remains independent of provider/model assignment.
- A native agent may receive store data only when its stored capability/authority permits READ.

## Scope

1. Harden the native system prompt:
   - follow the user's language when practical,
   - never invent MSA/store-specific facts,
   - distinguish general domain knowledge from retrieved MSA facts,
   - state uncertainty plainly,
   - never claim a tool/result that was not supplied.
2. Add a small deterministic native read-tool adapter layer using shared backend/database read contracts, not MCP.
3. Initial read tools:
   - latest inventory/shadow batch summary,
   - latest `NEW_UNMAPPED` rows (bounded),
   - shadow review-reason summary (bounded).
4. Route obvious data-seeking prompts to the relevant bounded read adapters before provider invocation.
5. Include tool provenance in the assistant message runtime metadata.
6. Polish AI Workspace mobile controls so buttons/tabs/forms use the Dashboard visual language rather than browser-default styling.

## Security / authority invariants

- AI Workspace access policy and conversation ownership are checked before tool execution or provider invocation.
- Internal agent must be ACTIVE + `INTERNAL_MODEL`.
- READ data is supplied only when the agent has `mcp:read`/read capability and authority ceiling permits READ or above.
- Tool adapters are read-only and bounded.
- No raw SQL, arbitrary table access, write, propose, or control tool is exposed to the model.
- Tool selection is server-side; the provider cannot request an arbitrary backend operation in this slice.

## Acceptance

- Asking for an inventory summary returns actual current shadow/test summary data and identifies the DB as non-canonical/test evidence.
- Asking for `NEW_UNMAPPED` rows returns real bounded rows rather than an invented answer.
- A non-read internal agent receives no store data and cannot cause a DB read through Chat.
- A general/Burmese prompt does not invent store facts; it either answers general knowledge or says store facts require an attached/relevant read result.
- Runtime provenance records which native read tools ran.
- AI Workspace buttons/tabs/composer are visually consistent on mobile.
