# F7.3B Broad Typed Read Surface — 2026-08-23

## Decision

`mcp:read` is not a summary-only permission. For an ACTIVE external MCP agent whose effective authority includes `mcp:read`, MSA should expose the authorized typed read surfaces needed to inspect operational data in detail.

This does **not** mean arbitrary SQL or unrestricted table dumps. Read-only authority never exposes secret-bearing authentication material such as password hashes, session/token digests, provider API-key values, OAuth token internals, or server secret storage.

## Current typed read scope

The MCP read surface includes or is being expanded to include:

- identity/system status and effective authority
- shadow inventory migration summary
- bounded shadow source-row detail for `SAFE`, `REVIEW`, `CONFLICT`, and `NEW_UNMAPPED`
- optional shadow filters by migration batch, source sheet, classification, search text, limit, and offset
- shadow batch detail and review-reason summaries
- product search/item detail
- lot reads
- catalogue current/history reads
- other explicitly typed operational reads as their owning slices are implemented

## Bug fixed in this slice

The shadow-row and review-reason queries previously used optional predicates such as `:q IS NULL OR ...`. PostgreSQL can fail to infer the type of a NULL bind parameter in this pattern, resulting in the observed `503 Database read failed` response when optional filters were omitted.

F7.3B builds only the WHERE clauses for filters that are actually present. This removes the ambiguous NULL-bind pattern and keeps queries bounded.

## Audit semantics

External MCP detail reads emit append-only audit evidence with the bound named agent, external MCP transport, `mcp:read` capability, action name, result count/filter metadata, outcome, timestamp, and correlation ID. Query text and secret material are not logged.

## Boundaries preserved

- production inventory writes remain disabled
- database remains non-canonical
- migration baseline remains unaccepted
- no arbitrary SQL endpoint
- no raw database credentials
- no security-secret read surface
