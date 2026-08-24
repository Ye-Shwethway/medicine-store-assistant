# Inventory AI Copilot v1

Status: **F6E Slice D bounded contract. Read-only review assistance only.**

## Goal

Add AI assistance to the existing Inventory review workspace without creating a second inference stack and without giving AI mutation authority.

The first Slice D sub-slice is deliberately narrow:

`selected Inventory rows -> server-rehydrated bounded review context -> AI Workspace draft -> user Send -> existing native agent runtime`

No model request occurs merely because the user selects rows or presses `Ask AI`.

## Reuse rule

Reuse the existing:

- Inventory View Engine and system presets;
- AI Workspace access policy;
- AI Workspace conversations/messages;
- internal-agent/provider runtime;
- durable AI Workspace review/multi-agent substrate for later Deep Review.

Do **not** add a parallel provider/inference implementation inside Inventory.

## Inventory Review Context

The browser must not send arbitrary store facts as trusted AI context.

For v1, the client sends only bounded selection coordinates:

- `preset`;
- current `offset` and `limit`;
- current search/review filters;
- selected zero-based row indices from the currently rendered page.

The backend re-runs the same registered View Engine provider query with the same preset/filter/page inputs and selects those rows server-side.

This makes the returned evidence a server-rehydrated read projection rather than a client-authored inventory payload.

### Limits

- review presets only for the first sub-slice: `migration-review`, `cms-mapping-review`;
- maximum selected rows: **20**;
- indices must be unique and within the rehydrated page;
- only registered preset columns/evidence are returned;
- no arbitrary fields, SQL, expressions, URLs or tool instructions are accepted from the client.

### Response flags

Every context response must state:

- `read_only=true`;
- `database_canonical=false`;
- `migration_baseline_accepted=false`;
- context origin = server-rehydrated Inventory View projection.

## Web behavior

When one or more review rows are selected:

- show `Ask AI` in the existing selection-context bar;
- pressing it builds the bounded server context;
- open AI Workspace Chat using the existing access/agent runtime;
- create a conversation only if needed;
- prefill, but do **not** submit, a concise draft describing the selected evidence;
- the user remains responsible for pressing `Send` before any model request occurs.

The draft must clearly say that the evidence is shadow/non-canonical and that the AI should explain/summarize/rank only, not claim acceptance or mutation.

## Deep Review

Deep Review is a subsequent Slice D sub-slice. It will hand the same bounded context into the existing durable AI Workspace multi-agent/review substrate rather than inventing another review store.

## Authority boundary

Slice D does not authorize:

- Product-CMS mapping acceptance;
- operational-price acceptance;
- inventory movements or quantity changes;
- migration-baseline acceptance;
- PostgreSQL canonical promotion.

AI output is advisory evidence only until a later authorized typed decision command exists and passes its own confirmation/audit/read-back gates.

## Verification

The first Slice D sub-slice must prove:

1. selected row indices are rehydrated server-side through the registered provider;
2. arbitrary client row payload is not accepted;
3. more than 20 selected rows is rejected;
4. non-review presets are rejected for this AI review-context endpoint;
5. the Web handoff opens/prefills AI Workspace without auto-sending a model request;
6. canonical flags remain false and no inventory/mapping/price mutation occurs.
