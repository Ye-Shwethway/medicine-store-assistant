# F7.2D4.7B — Human-friendly response contract + attachment-ready Chat

Date: 2026-08-24

## Goal

Refine native AI Workspace answers so store facts are presented for humans first, while preserving exact provenance, and add an attachment-ready chat surface for both single-agent and Owner-only Multi-Agent workflows.

## Response contract

- Answer the user's question first; do not lead with debug identifiers or raw backend field names unless they are materially useful or explicitly requested.
- Tool adapters may return deterministic derived display values (for example calendar dates derived from stored spreadsheet serial dates) while retaining the raw source value in provenance.
- Distinguish retrieved facts, deterministic derived values, and model inference.
- Never claim a workflow state transition merely because one missing field appears to be the blocker. State that reclassification/validation must run and pass before a row changes state.
- Keep canonicality/test-shadow warnings concise in the user-facing answer. Full batch/source IDs remain available as provenance.

## Attachment architecture — LOCKED

Both `AI Workspace -> Chat` and future `AI Workspace -> Multi-Agent` use the same attachment contract.

Each composer must expose:

- photo/image picker;
- generic file picker;
- selected-attachment preview/list with remove-before-send.

Attachments are conversation/message evidence, not authority. Uploading a file never grants any agent new store permissions.

Backend requirements before processing:

1. authenticated AI Workspace access;
2. conversation ownership for single-agent Chat;
3. Owner backend authorization for Multi-Agent in the current phase;
4. bounded file count/size and MIME allowlist;
5. server-generated attachment ID and metadata;
6. no direct filesystem path, provider key, DB credential, or arbitrary URL exposure to the model;
7. model/vision processing only after capability + workflow checks.

Initial attachment slice is transport/persistence/UI only. It does not yet perform OCR, vision extraction, inventory mutation, Daily Usage posting, batch intake, or stock transfer.

Future workflows may consume attachments through typed operations, including:

- issue-paper photo -> vision/OCR -> draft batch intake -> human review -> typed commit;
- Daily Usage sheet/photo -> extraction -> validation -> draft usage rows -> review/commit;
- stock-transfer document/photo -> extraction -> location/authority validation -> proposed transfer -> controlled commit.

Raw uploaded evidence must remain traceable to any derived draft or later committed operation.

## Immediate implementation

1. Normalize current native read-tool results for human presentation while keeping raw provenance.
2. Strengthen response prompt against debug-dump answers and unsupported transition claims.
3. Add attachment buttons/selected-file UI to single-agent Chat and Multi-Agent composer shell.
4. Add backend attachment persistence/upload/read/delete contract with ownership/Owner checks, bounded types and sizes.
5. Do not send attachment bytes to provider models yet; mark processing as pending in UI/API.
6. Sync ROADMAP, IMPLEMENTATION_PLAN, and NEW_CHAT_BOOTSTRAP.
