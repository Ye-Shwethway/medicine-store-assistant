# F7.2D4.8 Review provenance + delete polish

Status: implementation in progress

Date: 2026-08-24

## Scope

This bounded slice follows the first successful per-participant native read-tool Review acceptance.

It adds:

- retrieval-first prompting for READ-capable Review participants when current MSA/store facts are required;
- deterministic runtime tool provenance in Review UI and DOCX/JSON snapshots;
- Owner-facing Delete for Multi-Agent Review work using audit-preserving cancellation semantics.

## Retrieval-first rule

A READ-capable participant should retrieve required current MSA evidence before evaluating, reviewing, or synthesizing it. It should not merely delegate tool use to a later participant when it can retrieve the required evidence itself.

This remains model-driven tool use. No new read tools are added. The bounded tool registry remains:

- `inventory_summary`
- `new_unmapped_rows`
- `review_reasons`

## Deterministic provenance

Runtime provenance, not model self-report, is authoritative for tool-use display.

Participant provenance records:

- whether native store READ tools were allowed;
- tools exposed;
- full native tool call trace;
- unique tools executed;
- total tool call count;
- provider/model/fallback/latency provenance.

The Review chat shows a compact `Tools: ... · N calls` line. DOCX snapshots include `Tools used` and `Tool calls`. JSON keeps the full trace.

## Review Delete semantics

Owner-facing Delete is intentionally not a hard database cascade.

Delete performs:

1. Work Item status -> `CANCELLED`;
2. item disappears from normal `Recent Review work`;
3. open Attention rows are resolved;
4. immutable `WORK_ITEM_DELETED_BY_OWNER` event is appended;
5. existing Artifacts, Reviews and Events remain preserved for audit evidence;
6. a running Review stops before the next participant/persistence boundary once cancellation is observed.

An already in-flight provider HTTP request cannot be force-cancelled by this slice, but its returned output is not persisted if the Work Item was deleted while the request was running.

## Boundaries unchanged

- no public MCP dependency;
- no inventory mutation;
- no canonical database promotion;
- no new native tools;
- no OCR/vision change;
- no hard deletion of workflow evidence.
