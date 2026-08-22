# F7.4–F7.8 — Store, Calculator & Intelligence Architecture

Status: **approved architecture direction; implementation follows F7.2 identity/User Management and F7.3 actor-aware audit foundation**

## Goal

Expand Medicine Store Assistant from a read-only dashboard into a scalable store-operations platform while preserving one backend truth across Web, future Telegram, future Flutter, internal AI, Custom GPT, and system jobs.

This architecture introduces:

- one canonical Main Store;
- any number of Owner-managed Sub Stores;
- location-aware product/lot balances;
- Owner-configurable reorder policy;
- durable cross-client user preferences;
- DB-backed Smart Calculator and receipts;
- deterministic Smart Analysis;
- grounded internal AI Assistant;
- reusable Alerts & Notifications.

Production stock mutation is **not** authorized by this document. Calculation-only, read-only, and architecture work may precede controlled writes.

## 1. Store-location model

### Main Store

The system has exactly one `MAIN` store.

The Main Store is the central receiving/holding location and initially remains the stock basis used for reorder calculations to match the current operational preference.

The Main Store cannot be duplicated through normal Owner UI. If future architecture ever requires replacing/renaming it, that must preserve stable location identity and history.

### Sub Stores

The Owner may create any number of `SUB` stores as operations expand.

A Sub Store may be:

- created;
- renamed;
- activated;
- disabled/archived while preserving history.

Each Sub Store has its own location identity and stock balance.

### Location-aware balance

Stock is not modeled as one anonymous quantity. Balance is resolved at least by:

`product_id -> lot_id -> location_id -> balance`

This allows the same lot/product to be held simultaneously in Main Store and multiple Sub Stores.

## 2. Movement semantics

Initial domain movement types:

- `RECEIPT`: external source -> Main Store;
- `TRANSFER`: Main Store -> selected Sub Store;
- `DISPENSE/USAGE`: selected Sub Store -> customer/consumption;
- `ADJUSTMENT`: controlled balance correction;
- `REVERSAL/CORRECTION`: linked correction of a committed operation.

Sub-to-Sub transfer is deferred until a real workflow requires it.

Committed transfer/dispense history is not destructively edited merely to make totals look correct. Corrections are linked and auditable.

## 3. Current Daily Usage reinterpretation

The current operational sheet named `Daily Usage` is understood to represent Main Store -> Sub Store stock transfer activity rather than final end-customer usage.

Future migration should therefore treat supported rows as transfer-source evidence where the source data is sufficient.

Rules:

- preserve original source provenance (`Daily Usage` sheet/document name);
- do not silently fabricate historical destination Sub Stores if source records do not identify them;
- surface unresolved historical ambiguity for Owner review;
- future UI terminology should use `Stock Transfer` for the new canonical operation.

## 4. Reorder policy

Reorder calculations read an Owner-configurable backend policy.

Supported policies:

- `MAIN_STORE_ONLY` — initial/default operational mode;
- `TOTAL_ACTIVE_STOCK` — Main Store + all active Sub Stores.

Changing the policy from Settings changes the reorder calculation basis without changing application code or rebuilding formulas.

The analytics UI may always display Main, individual Sub Store, and Total stock even when the reorder policy uses only one basis.

## 5. Store/location access policy

Role authorization and location scope are separate concepts.

Examples:

- Owner normally sees/manages all locations;
- Admin may manage permitted stock-transfer workflows according to policy;
- Staff may be scoped to one or more Sub Stores;
- Read-only users may receive read scope without operation rights.

Location scope is backend-enforced; hidden UI is not authorization.

## 6. Preference persistence

Preferences should follow the user across clients when the preference has operational meaning.

Backend user preferences may include:

- default store/location;
- default Smart Calculator Sub Store;
- whether the user/role may change Calculator location;
- default card/table/list inventory view;
- visible columns;
- column order;
- table density;
- saved filters;
- analysis defaults;
- calculator/receipt defaults;
- saved extra-fee presets where authorized.

Ephemeral device-only state may remain local to the browser/app, but canonical user preferences should not be trapped in one device.

## 7. Smart Calculator

Smart Calculator is a first-class operational tool, not an Excel-import feature.

### Data source

Normal use reads directly from backend product/lot/location data.

The Calculator does **not** require users to upload a separate Excel file or manually map item/quantity/price columns.

Owner batch intake/import mapping, when needed, is a separate data-ingestion workflow.

### Identity and same-name protection

Display names are not canonical identity.

Selection resolves to stable product/lot records. Similar/same-name candidates must expose enough distinguishing information such as:

- strength/form;
- brand/source name;
- lot/expiry;
- store availability;
- CMS/local code when useful.

AI/photo-assisted matching must stop for human confirmation when candidate identity is ambiguous.

### Calculation-only mode

`CALCULATE_ONLY` supports:

- item search;
- quantity;
- price/reference value;
- multiple items;
- extra fees;
- receiver/customer;
- issuer;
- note;
- subtotal/fees/total;
- save calculation;
- receipt history;
- print/PDF/export/share.

It does not change inventory.

### Future dispense mode

`DISPENSE_FROM_SUB_STORE` is designed now but only becomes write-capable after controlled write authorization.

The user selects a Sub Store or accepts their saved default Sub Store.

At eventual commit time the backend must:

- validate current stock at the selected Sub Store;
- enforce user role/location scope;
- resolve exact product/lot identity;
- use operation ID/idempotency;
- atomically deduct stock;
- create actor-aware audit/ledger entries;
- link the receipt/calculation to the committed operation;
- return committed-state readback.

## 8. AI/photo-to-calculation direction

A future scan/photo flow may:

1. extract candidate text/items/quantities;
2. call typed product search;
3. rank candidate matches;
4. require explicit selection for ambiguous same-name items;
5. build a draft Smart Calculator session;
6. allow human review/edit;
7. never auto-commit inventory solely from OCR/LLM interpretation.

This upgrade is suitable for Web/Flutter and may later be exposed through Telegram where UX permits.

## 9. Smart Analysis

Smart Analysis remains deterministic first and AI-assisted second.

Initial modules:

1. Stock Health
2. Transfer / Usage Trends
3. Expiry Risk
4. Reorder Outlook
5. Price Movement
6. Data Quality

Metrics should support location-aware views:

- Main Store;
- individual Sub Stores;
- Total active stock;
- transfer velocity;
- future dispense/consumption velocity once reliable Sub Store usage exists.

The UI clearly shows the active reorder basis when presenting reorder analysis.

Charts/KPIs must be traceable to supporting rows/lots/operations.

## 10. Internal AI Assistant

The internal Assistant is an identifiable `AI_AGENT` principal and uses typed tools over authorized backend data.

It may:

- compare Main/Sub/Total stock;
- explain transfer/usage trends;
- identify expiry/reorder risk;
- discuss price movement and data quality;
- generate charts/tables;
- help prepare a Smart Calculator draft;
- summarize audit history.

It must respect the current user's RBAC and location scope.

No arbitrary SQL or DB credentials are exposed.

Initial mode remains read-only.

## 11. Alerts & Notifications

Alerts originate from deterministic facts/events first.

Candidate events include:

- low Main Store stock;
- low Total Stock depending on active reorder policy;
- low Sub Store stock/refill pressure;
- approaching expiry;
- unusual transfer or dispense pattern;
- data-quality/mapping problem;
- reconciliation/sync failure;
- pending user-access/password-reset request;
- later scheduled analysis results.

One backend event may surface through Web, Telegram, Flutter, or other future channels.

AI may explain/prioritize an alert but does not replace the underlying triggering fact.

## 12. Multi-client principle

Web, Telegram, Flutter, internal AI, Custom GPT, and system jobs are clients of the same backend.

They reuse:

- canonical identities and sessions/service principals;
- RBAC and location scope;
- user preferences;
- product/lot/location data;
- Smart Calculator/receipts;
- analytics;
- notification events;
- typed inventory operations;
- actor-aware Audit.

Flutter may later support offline-tolerant caching for usability, but that cache is not a second canonical store database.

## 13. Implementation order

1. F7.2A — canonical multi-user identity
2. F7.2B — User Management
3. F7.2C — credential lifecycle
4. F7.3 — actor-aware Audit / operation ledger
5. F7.4 — locations, store policy, preferences
6. F7.5 — Smart Calculator / receipts (calculation-only)
7. F7.6 — Smart Analysis
8. F7.7 — internal AI Assistant
9. F7.8 — Alerts & Notifications
10. F8 — external/Custom GPT read-only integration
11. F9 — controlled typed stock writes, including transfer/Calculator dispense when separately authorized
12. F10 — real workflow + fresh migration + Sheet sync validation
13. F11 — explicit canonical promotion

## Safety boundary

This architecture does not authorize production inventory mutation, canonical DB promotion, direct LLM-to-DB writes, direct LLM-to-Sheet mutation, or silent migration of ambiguous historical rows.