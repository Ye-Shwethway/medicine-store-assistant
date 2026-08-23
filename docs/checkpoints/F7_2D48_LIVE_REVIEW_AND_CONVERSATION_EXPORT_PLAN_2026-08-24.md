# F7.2D4.8 Live Review + Conversation Export Plan

Status: approved implementation plan

Date: 2026-08-24

## Goal

Polish the accepted native REVIEW workflow into a practical Owner work surface, then add one shared point-in-time export subsystem for Single-Agent Chat and Multi-Agent Review.

## Review polish

1. Keep REVIEW presets flexible: two-agent REVIEWER -> SYNTHESIZER is valid; ANALYST is optional unless assigned by the Owner.
2. Do not invent unconfigured roles in orchestration context. Every participant receives the actual configured role sequence and only persisted prior participant outputs.
3. Replace all-at-once UI completion with persisted turn-by-turn progress:
   - create Work Item immediately,
   - execute native participants in backend background work,
   - persist each artifact/event as the participant completes,
   - poll the durable Work Item from the browser at a short bounded interval,
   - render each completed turn as soon as it is persisted,
   - stop polling at WAITING_OWNER or FAILED.
4. This slice is turn streaming, not token streaming. No WebSocket/SSE is required yet.
5. Reuse Single-Agent Chat display normalization for Review bubbles so raw Markdown markers/tables are not shown as UI noise.
6. Add per-message Copy controls to Owner and agent Review turns, matching Single-Agent Chat behavior.
7. Preserve provider/model/fallback/latency provenance under agent turns.
8. Preserve the production mutation and database-canonicality boundaries.

## Unified Conversation Export

One shared backend export service covers both work surfaces.

### Formats in first slice

- DOCX: primary human-readable point-in-time snapshot.
- JSON: machine-readable snapshot for audit, automation, future federation, and archival.

PDF and Markdown may follow after DOCX/JSON acceptance; they are not required for this first export slice.

### Single-Agent Chat snapshot

Include:
- conversation ID/title,
- exported-at timestamp,
- authenticated owner/user identity reference,
- selected agent identity,
- ordered messages,
- message role and timestamps,
- assistant provider/model/fallback/latency provenance,
- saved attachment metadata/references,
- snapshot format/version.

### Multi-Agent Review snapshot

Include:
- Work Item metadata and current lifecycle state,
- Owner task and evidence references,
- ordered participant artifacts with assigned orchestration role,
- Review records/verdicts bound to artifact versions,
- Owner revision artifacts,
- provider/model/fallback/latency provenance,
- Attention state and immutable event timeline,
- production_mutation flag,
- database_canonical flag,
- exported-at timestamp and snapshot schema version.

## Snapshot invariant

Export is immutable point-in-time output, not a live-linked document. A later revision does not modify an earlier downloaded file. Re-exporting creates a newer snapshot of the same conversation/work item.

## Authorization

- Single-Agent export requires the same authenticated access and conversation ownership as Chat readback.
- Multi-Agent Review export remains Owner-only in the current phase.
- Export does not grant inventory authority and does not perform store mutation.

## UI

- Single-Agent Chat header: Export -> DOCX / JSON.
- Multi-Agent Review Work Item header: Export -> DOCX / JSON.
- Mobile-first; use browser download via authenticated same-origin endpoints.

## Acceptance

Review polish passes when:
- a two-agent REVIEWER -> SYNTHESIZER preset runs without implying a configured ANALYST,
- each persisted participant turn appears while later participants are still running,
- Copy works on Review messages,
- raw Markdown display noise is normalized,
- final state remains WAITING_OWNER with no store mutation.

Export passes when:
- an authorized user can download a complete Single-Agent snapshot as DOCX and JSON,
- Owner can download a complete Multi-Agent Work Item snapshot as DOCX and JSON,
- snapshots contain ordered content plus provenance/metadata,
- unauthorized cross-user Chat export is denied,
- Review export is Owner-only,
- files are generated from persisted state and do not mutate source records.
