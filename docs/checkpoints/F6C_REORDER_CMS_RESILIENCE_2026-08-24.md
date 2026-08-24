# F6C Checkpoint — Reorder Resilience + CMS Assisted Mapping

Date: 2026-08-24

Status: **architecture aligned; no runtime/schema/inventory mutation in this checkpoint**

## Owner-confirmed decisions

### Reorder

- Do not make reorder AI-only.
- The system must retain a deterministic baseline reorder capability when all AI providers are unavailable.
- AI/advanced analysis may improve/review the baseline when available.
- Deterministic baseline, AI-enhanced proposal and final human-authorized quantity remain distinguishable.
- Exact legacy Excel Estimated Reorder Qty formula parity is not required for F6D.

### CMS mapping

- Do not blindly auto-sync Local Product <-> CMS Catalogue by CMS Code.
- The CMS catalogue is much larger than the local store inventory and local/CMS names often differ.
- CMS codes may retire/reuse and local workbook data may also contain stale or staff-entered errors.
- AI-assisted reconciliation is preferred for ambiguous matching because it reduced the previous manual workload effectively.
- AI outage must not block ordinary inventory operation.
- Keep last accepted catalogue/mapping/operational price state available.
- New/unresolved mapping remains review-required/unmapped until AI-assisted or manual review is completed.
- If a new mapping/price cannot yet be accepted, continue using the last accepted operational price rather than forcing an unsafe update.

## Live Google Sheet evidence reviewed

Cross-analysis used `Main Stock`, `CMS_Price_List_202608`, and `Audit_Log`.

Observed examples include:

- `S10100193`: current CMS catalogue identity is `Diathermy Patient Plate (BG China)` while local `ECG / USG Transmission Gel` carries the same code and is explicitly marked `Recycled ID`.
- `S10100011`: current CMS catalogue identity is `Airway 1 (White) (China)` while local rows include both `Guedel Airway No. 1 (White)` and `Eusol 500ml` using the code. Do not infer whether this is historical/stale mapping or local staff error without review.
- `M10101970`: local `O' Coamoxiclav 625` sibling expiry lots show current-price adoption plus a `Recycled ID` exception.
- multiple rows are marked `CMS Discontinued (Local Stock Retained)`, proving that local Product lifecycle must remain independent of current CMS catalogue availability.
- `Audit_Log` shows CMS Price Update operations with previous/updated values and backup snapshot references, reinforcing the need for mapping/price provenance.

## Architecture results

Added/updated:

- `docs/architecture/CMS_MAPPING_LIFECYCLE.md`
- `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`
- `docs/architecture/CANONICAL_INVENTORY_FOUNDATION.md`
- `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
- `docs/architecture/WORKBOOK_FUNCTION_CONTRACT.md`
- `ROADMAP.md`
- `IMPLEMENTATION_PLAN.md`
- `NEW_CHAT_BOOTSTRAP.md`

## Next implementation target

F6D schema foundation should now proceed with:

1. Store/Location identity;
2. location-aware ledger;
3. atomic internal transfer representation;
4. receipt provenance/location;
5. Product/Lot identity independent of location;
6. historical/auditable CMS mapping lifecycle and last-accepted-state retention;
7. actor/audit/idempotency;
8. fresh non-canonical Main Store shadow import and reconciliation.

Full AI semantic matcher and deterministic reorder engine remain later bounded slices.
