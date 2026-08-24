# F7.2D4.8 Per-Participant Native Read Tools

Status: implementation in progress

Date: 2026-08-24

## Goal

Allow each configured native REVIEW participant to use the existing bounded D4.7A native read tools when, and only when, that participant independently has READ authority.

Current bounded tool set remains:

- `inventory_summary`
- `new_unmapped_rows`
- `review_reasons`

Public MCP is not used by this path.

## Authority invariant

For every participant, tool exposure is evaluated independently. Session membership never unions participant privileges.

A participant may receive native store read tools only when all of the following are true:

1. the authenticated workflow is Owner-only;
2. the participant is an ACTIVE `INTERNAL_MODEL` agent in the selected REVIEW preset;
3. the participant capability scopes include `mcp:read`;
4. the participant authority ceiling is at least `READ`;
5. the requested operation is one of the explicit bounded native read tools;
6. the backend tool implementation remains read-only and non-canonical.

If the participant fails the READ check, the model is invoked normally with no native store tools exposed. Another participant's READ authority must not affect this result.

## Persistence / provenance

Each participant artifact must preserve, when applicable:

- whether native store tools were allowed;
- exposed native tool names;
- model-driven native tool call trace;
- successfully executed tool names;
- provider/model/fallback/latency provenance.

This evidence is also included automatically in the existing Work Item DOCX/JSON snapshot because export reads persisted artifact provenance.

## UI

The live Review bubble should show bounded tool provenance when a participant used tools, without dumping raw tool results by default.

Example:

`Tools: new_unmapped_rows · 1 call`

## Acceptance

1. A READ-capable participant can make a model-driven call to one of the three existing native read tools.
2. A participant without READ capability/ceiling receives no native store tool definitions.
3. Two participants with different authority do not inherit each other's tool access.
4. Tool call provenance persists in the participant artifact and event.
5. Live Review UI surfaces concise tool-use provenance.
6. A real Owner-only REVIEW can inspect current NEW_UNMAPPED shadow evidence and reach `WAITING_OWNER` with `production_mutation=false` and `database_canonical=false`.

## Non-goals

- no inventory writes;
- no MCP schema/action changes;
- no new read tools;
- no OCR/vision processing;
- no federated `WAITING_EXTERNAL` yet;
- no privilege union across a session.
