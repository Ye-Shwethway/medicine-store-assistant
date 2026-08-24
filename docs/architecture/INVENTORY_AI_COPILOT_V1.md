# Inventory AI Copilot v1

Status: **F6E Slice D bounded contract. Read-only review assistance only. Ask AI runtime-verified; Deep Review handoff is the current sub-slice.**

## Goal

Add AI assistance to the existing Inventory review workspace without creating a second inference stack and without giving AI mutation authority.

Slice D uses one bounded evidence path:

`selected Inventory rows -> server-rehydrated bounded review context -> AI Workspace`

From there the user chooses either:

- **Ask AI** -> Chat composer draft -> explicit user Send -> existing native agent runtime;
- **Deep Review** -> Multi-Agent REVIEW composer draft -> explicit Owner Run native review -> existing durable review workflow.

Neither Inventory button executes a model merely because it is clicked.

## Reuse rule

Reuse the existing:

- Inventory View Engine and system presets;
- AI Workspace access policy;
- AI Workspace conversations/messages;
- native internal-agent/provider runtime;
- Multi-Agent REVIEW presets and stable orchestration roles;
- durable Work Item / Artifact / Review / Event / Attention substrate.

Do **not** add a parallel provider/inference implementation or a second review persistence model inside Inventory.

## Inventory Review Context

The browser must not send arbitrary store facts as trusted AI context.

The client sends only bounded selection coordinates:

- `preset`;
- current `offset` and `limit`;
- current search/review filters;
- selected zero-based row indices from the currently rendered page.

The backend re-runs the same registered View Engine provider query with the same preset/filter/page inputs and selects those rows server-side.

This makes the returned evidence a server-rehydrated read projection rather than a client-authored inventory payload.

### Limits

- supported review presets: `migration-review`, `cms-mapping-review`;
- maximum selected rows: **20**;
- indices must be unique and within the rehydrated page;
- only registered preset columns/evidence are returned;
- no arbitrary fields, SQL, expressions, URLs or tool instructions are accepted from the client.

### Response flags

Every context response states:

- `read_only=true`;
- `database_canonical=false`;
- `migration_baseline_accepted=false`;
- context origin = `SERVER_REHYDRATED_INVENTORY_VIEW`.

## Ask AI — COMPLETE + RUNTIME VERIFIED

When review rows are selected:

- `Ask AI` builds the bounded server context;
- opens existing AI Workspace Chat;
- prefills, but does **not** submit, a concise evidence-grounded draft;
- the user presses `Send` before any model request occurs.

Runtime issue #176 and deployment issue #26 verify merge `06b219ee4604bc984bf4d427f820a71c87202e65` in production.

## Deep Review — CURRENT

Deep Review uses the **same** server-rehydrated context endpoint. It must not trust browser row payloads and must not automatically start a REVIEW workflow.

Expected flow:

1. user selects 1–20 rows in Migration Review or CMS Mapping Review;
2. user presses `Deep Review`;
3. Inventory requests the same bounded server-rehydrated context;
4. Inventory emits a local handoff event containing that already returned context;
5. existing AI Workspace opens and switches to the Owner-only Multi-Agent tab;
6. the existing Multi-Agent REVIEW UI prefills:
   - a concise Work title derived from the selected Inventory preset/count;
   - the Owner task containing the selected server-rehydrated evidence and explicit shadow/non-canonical boundary;
7. the user chooses an existing open REVIEW preset/session and preserves/configures orchestration roles through the existing UI;
8. only the existing `Run native review` button may POST `/dashboard/api/ai-workspace/multi-agent/reviews` and start native agent execution.

### Important behavior

- Deep Review click itself must make **zero** `/multi-agent/reviews` requests.
- It must not create Work Items, Artifacts, Reviews or Events until the Owner presses the existing run button.
- It must not select a REVIEW preset automatically when there are multiple choices.
- It may preserve an already selected valid REVIEW preset if the existing UI already has one selected.
- The normal Multi-Agent workflow owns durable execution/history; Inventory only supplies bounded context.
- If the Multi-Agent workspace is unavailable to the current user, the handoff fails visibly and no execution occurs.

## Authority boundary

Slice D does not authorize:

- Product-CMS mapping acceptance;
- operational-price acceptance;
- inventory movements or quantity changes;
- migration-baseline acceptance;
- PostgreSQL canonical promotion.

AI output is advisory evidence only until a later authorized typed decision command exists and passes its own confirmation/audit/read-back gates.

## Verification

### Ask AI proof

1. selected row indices are rehydrated server-side through the registered provider;
2. arbitrary client row payload is not accepted;
3. more than 20 selected rows is rejected;
4. non-review presets are rejected;
5. Chat is prefilled without auto-sending a model request;
6. canonical flags remain false.

### Deep Review proof

1. Deep Review reuses `/inventory-view/review-context` rather than browser-authored row facts;
2. AI Workspace opens the Multi-Agent tab;
3. Work title + Owner task are prefilled with the selected server context;
4. no `/multi-agent/reviews` POST occurs during handoff;
5. an existing configured REVIEW preset may remain selected, but handoff does not silently choose a new preset;
6. `Run native review` remains the explicit Owner execution action;
7. no inventory/mapping/price mutation or canonicality change occurs during the handoff.
