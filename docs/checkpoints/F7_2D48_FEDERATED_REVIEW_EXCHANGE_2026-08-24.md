# F7.2D4.8 Federated Review Exchange

Status: implementation candidate; CI/deployment/manual external acceptance pending

Date: 2026-08-24

## Accepted native REVIEW baseline before this slice

Owner mobile acceptance confirmed the native REVIEW path is usable with live participant turns, Copy, cleaned display formatting, DOCX/JSON snapshot export, deterministic native-tool provenance, retrieval-first prompting, and audit-preserving Review deletion from Recent Review work.

Native Review remains first-class. Federation is optional and is not required to run a Review.

## Federation contract

Owner may take a `WAITING_OWNER` Review Work Item and request optional external review. The request freezes one exact artifact identity:

- `work_item_id`
- `request_artifact_id`
- `bound_artifact_id`
- `bound_artifact_version`
- bound artifact type/content hash when available

The Work Item moves to `WAITING_EXTERNAL`. The request is stored as an immutable `EXTERNAL_REVIEW_REQUEST` artifact plus event and Attention evidence.

An authorized named `EXTERNAL_MCP_CLIENT` may read pending requests with `mcp:read` and submit an evidence-only review with `mcp:propose`.

Submission must bind to the exact current request artifact and exact bound artifact/version. Stale request IDs, artifact/version mismatch, and hash mismatch are rejected.

Accepted external submission creates:

- `workflow_reviews` row with `reviewer_actor_type=EXTERNAL_MCP_AGENT`
- immutable `EXTERNAL_REVIEW_SUBMISSION` artifact
- `EXTERNAL_REVIEW_SUBMITTED` event
- resolved `WAITING_EXTERNAL` Attention
- new `WAITING_OWNER` Attention

The Work Item returns to `WAITING_OWNER`.

## MCP surface

This slice intentionally does not repurpose `msa_agent_sessions_manage`. Its existing `mcp:control` semantics and parameter shape cannot express exact artifact-version review binding cleanly.

The same MSA MCP backend gains two bounded v2.2 tools:

- `msa_federated_review_query` — `mcp:read`; actions `list_pending` / `get_request`
- `msa_federated_review_submit` — `mcp:propose`; exact request/artifact/version + verdict/notes/findings

This is a schema extension on the existing MCP backend, not a second MCP server. ChatGPT-side MCP registration/schema refresh or replacement may be required before manual SOL acceptance.

## Authority boundary

External review evidence never inherits internal-agent authority and never gains inventory mutation authority.

`effective external authority = OAuth grant ∩ bound named-agent capability scopes ∩ agent authority ceiling ∩ tool scope`

Federated tools additionally require an ACTIVE named agent with `runtime_mode=EXTERNAL_MCP_CLIENT`.

No session privilege union is permitted.

## Store boundary

Unchanged:

- `production_mutation=false`
- `database_canonical=false`
- `migration_baseline_accepted=false`
- no inventory write
- no canonical DB promotion
- no automatic external approval/commit

## Owner UI

Opened `WAITING_OWNER` Review work exposes a separate workflow action: `Request external review`.

It is not mixed with DOCX/JSON export actions. While pending, the detail shows `Waiting for external review`. External submission appears in the Review chat as an External MCP reviewer bubble and the Work Item returns to `WAITING_OWNER`.

## Acceptance still required

1. CI validates route/schema/authority/exact-binding contracts.
2. Production deploy of the exact merge SHA succeeds.
3. ChatGPT-side MCP schema sees the v2.2 tools.
4. Owner requests external review for a harmless Review Work Item.
5. External SOL/ChatGPT reads the exact frozen artifact through MCP.
6. External SOL submits a review bound to that exact artifact/version.
7. UI shows the external review bubble and `WAITING_OWNER`.
8. No inventory mutation occurs.
