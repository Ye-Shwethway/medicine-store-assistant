# CMS Mapping Lifecycle

Status: **LOCKED ARCHITECTURE DIRECTION — implementation pending**

## Purpose

Define how Medicine Store Assistant connects the local store inventory to the much larger, periodically issued CMS catalogue without pretending that CMS Code is a stable local identity or that mapping can be safely auto-synchronized.

The target is an **assisted reconciliation workflow**:

> **CMS mapping is never blindly auto-synced. Last accepted mapping and price state remain usable until a newer mapping is reviewed and accepted.**

AI may substantially reduce mapping effort, but AI availability must never become a requirement for ordinary store operation.

## Source-backed problem

The live store uses roughly a much smaller operational subset of a CMS catalogue containing many thousands of rows. Local item names often differ materially from CMS catalogue names.

The live workbook also contains evidence that CMS codes can become operationally unsafe as direct identity keys:

- `S10100193` is currently `Diathermy Patient Plate (BG China)` in the CMS catalogue while a local `ECG / USG Transmission Gel` row still carries that code and is explicitly marked `Recycled ID`.
- `S10100011` is currently `Airway 1 (White) (China)` in the CMS catalogue while local Main Stock contains both `Guedel Airway No. 1 (White)` and `Eusol 500ml` rows carrying that code. This may reflect historical mapping state or local data-entry error; it must be reviewed rather than auto-interpreted.
- `M10101970` currently maps to `Clavamyn 625mg Tab`; sibling local `O' Coamoxiclav 625` lots show both current price adoption and a `Recycled ID` historical exception.
- numerous local items are explicitly marked `CMS Discontinued (Local Stock Retained)`, including rows with old CMS codes and rows with no current code.

The correct conclusion is not that every suspicious row is a CMS error. Some may be local staff error, stale mapping, historical truth, or recycled identity. The system must preserve that uncertainty and route it through review.

## Identity separation

Keep these concepts separate:

1. **Local Product** — stable store identity.
2. **Local Lot** — normally Product + Expiry Date in v1.
3. **CMS Catalogue Version** — one issued CMS price/catalogue dataset.
4. **CMS Catalogue Item Version** — one source-preserving catalogue row within that version.
5. **Product-CMS Mapping** — an accepted or reviewed relationship between a local Product and a CMS catalogue identity/context.

CMS Code is an external attribute of a catalogue row, not the local `product_id`.

## Catalogue lifecycle

Each new CMS list is imported as a new immutable/versioned catalogue dataset.

The prior dataset remains available for:

- price history;
- mapping history;
- code retirement/reuse analysis;
- forensic review;
- historical receipt context;
- rollback/reconciliation evidence.

Do not replace the old catalogue in place.

## Mapping lifecycle

A mapping is a durable reviewed state, not a live formula joining `local_product.cms_code = current_catalogue.code`.

Conceptual mapping fields may include:

- `mapping_id`;
- `product_id`;
- target catalogue item/version identity;
- `cms_code_snapshot`;
- CMS name/description snapshot where useful for audit;
- `mapping_status`;
- `valid_from` / `valid_to` or equivalent lifecycle timestamps;
- `match_basis` / evidence summary;
- review state/confidence metadata where useful;
- actor/proposer/approver context;
- operation ID;
- supersession link;
- note/reason.

Exact physical schema can remain compact, but historical accepted mapping state must not be overwritten destructively.

## Minimum mapping states

The implementation needs enough structured state to distinguish at least:

- `ACTIVE_MATCH` — accepted current mapping.
- `HISTORICAL_MATCH` — valid historical mapping not used as the current default.
- `REVIEW_REQUIRED` — candidate exists but identity/price propagation is not yet trusted.
- `UNMAPPED` — no accepted mapping.
- `RECYCLED_CODE` — code currently points to a materially different CMS identity or equivalent evidence indicates code reuse.
- `CMS_DISCONTINUED` — local Product remains valid but the prior CMS item is no longer active/available in the current catalogue.
- `SUPERSEDED` — mapping replaced by a newer accepted mapping.

Implementation may use a smaller normalized status vocabulary plus reason codes if it preserves these semantics clearly.

## New catalogue reconciliation

When a new CMS catalogue version is imported:

```text
New Catalogue Version
        |
        v
Deterministic diff against prior accepted catalogue/mappings
        |
        +--> unchanged / identity-compatible candidate
        |       -> retain accepted mapping
        |       -> current catalogue price may be proposed/applied under authorized price-update workflow
        |
        +--> changed / ambiguous / missing / recycled candidate
                -> REVIEW queue
                -> AI-assisted reconciliation when available
                -> manual review when AI unavailable
```

Deterministic preprocessing may safely narrow candidates using source facts such as:

- prior accepted code;
- local name tokens;
- CMS brand/description;
- strength;
- form;
- type/class;
- size/gauge;
- unit;
- historical mapping;
- historical receipt evidence;
- catalogue diff classification.

These signals generate candidates. They do not independently authorize a new identity mapping when ambiguity remains.

## AI-assisted reconciliation

AI is the preferred assistance layer for painful ambiguous matching because it can reason over non-identical local/CMS naming and multiple descriptive attributes.

AI may:

- rank candidate CMS rows;
- explain why a candidate likely matches;
- detect likely rename/description changes;
- flag likely recycled code or incompatible identity;
- compare current and historical mappings;
- propose mapping changes;
- help review batches of changed items.

AI does **not** silently replace accepted mapping state.

Accepted mutation still goes through typed operations, authority checks, confirmation where required, audit and read-back.

## AI unavailable fallback

AI outage must not block normal inventory use.

When AI services are unavailable:

- retain the last accepted CMS catalogue dataset locally/in the backend;
- retain all accepted Product-CMS mappings;
- retain last accepted store-facing price state;
- continue ordinary inventory operations with those accepted values;
- leave new/ambiguous mapping candidates as `REVIEW_REQUIRED` or `UNMAPPED`;
- allow human users to perform manual mapping/review using search/filter/candidate tools;
- never erase or null a working prior mapping merely because a newer catalogue could not yet be reconciled.

CMS catalogues are issued relatively infrequently in the current workflow, so delayed mapping review is operationally acceptable compared with unsafe automatic remapping.

## Price fallback semantics

A new catalogue issue does not automatically invalidate the store's last accepted operational price.

Keep separate concepts for:

- current catalogue price from the newest imported CMS dataset;
- last accepted Product-CMS mapping;
- last accepted store-facing/current operational CMS price;
- historical receipt/source price.

If a new catalogue row cannot yet be safely mapped:

> **Continue using the last accepted store price and surface that the newer CMS catalogue has not yet been reviewed for this Product.**

Do not fabricate a zero price, delete the prior price, or adopt a new code's price merely because the code string matches.

## Discontinued local stock

If CMS discontinues an item while local stock remains:

- local Product and Lot remain valid;
- historical mapping remains preserved;
- mapping becomes inactive/discontinued for current-catalogue purposes;
- existing local stock may continue normal lifecycle/use/sale according to store policy;
- no automatic remap to a vaguely similar CMS row occurs.

## Recycled code handling

A suspected recycled code is an identity conflict, not a price update.

On evidence of material identity shift:

- preserve old mapping history;
- freeze/close the prior current mapping as appropriate;
- mark affected local Product mapping for review;
- do not propagate the new CMS name/price as trusted local mapping automatically;
- require explicit accepted mapping before current mapping changes.

## Price-update workflow

CMS price update is downstream of mapping trust.

Preferred flow:

`import catalogue -> diff -> reconcile mappings -> classify SAFE/REVIEW/CONFLICT -> authorized price proposal/update -> read-back -> audit`

Code equality alone is insufficient to classify a mapping as SAFE when historical/source evidence conflicts.

## UI / operational view

Useful mapping/price columns may include:

- Local Item Name;
- Current Accepted CMS Name;
- CMS Code;
- Mapping Status;
- Current Catalogue Price;
- Last Accepted Store Price;
- Catalogue Version;
- Last Verified/Accepted time;
- Warning/Review Reason.

The UI should make stale-but-accepted price state visibly different from a fully reconciled current-catalogue state without blocking normal store work.

## Audit

Mapping and price changes must preserve:

- previous accepted mapping/price;
- proposed new mapping/price;
- source catalogue version;
- actor/agent proposal identity;
- human approval identity where required;
- operation/idempotency ID;
- reason/review evidence;
- read-back outcome.

The current workbook `Audit_Log` demonstrates the importance of previous/current value tracking. The backend should generalize this with stable identities and structured provenance.

## F6D implications

F6D must provide a schema path for:

1. immutable/versioned CMS catalogue datasets;
2. source-preserving catalogue items;
3. historical/auditable Product-CMS mappings;
4. mapping lifecycle/status;
5. last accepted mapping retention when a new catalogue is unresolved;
6. explicit separation of current catalogue price, accepted operational price and historical receipt price;
7. code-reuse/discontinuation review without local Product deletion;
8. AI/manual reconciliation using the same typed mapping operations.

F6D does not need a sophisticated semantic matching engine yet. It must get the persistence/lifecycle model correct so that deterministic and AI-assisted reconciliation can be added without redesigning inventory identity.

## Boundary

No live CMS mapping or price mutation is authorized by this architecture document. Google Sheet/source documents remain operationally authoritative until later controlled promotion.
