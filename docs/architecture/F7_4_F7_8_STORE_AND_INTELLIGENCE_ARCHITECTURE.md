# F7.4–F7.8 — Store, Calculator & Intelligence Architecture

Status: **approved architecture direction; implementation follows F7.2 human identity/User Management/AI Agent Management and F7.3 actor-aware Audit foundation**

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

The Main Store cannot be duplicated through normal Owner UI. Renaming/replacing it later must preserve stable location identity and history.

### Sub Stores

The Owner may create any number of `SUB` stores as operations expand.

A Sub Store may be created, renamed, activated, or disabled/archived while preserving history.

### Location-aware balance

Stock is resolved at least by:

`product_id -> lot_id -> location_id -> balance`

This allows the same product/lot to be held simultaneously in Main Store and multiple Sub Stores.

## 2. Movement semantics

Initial domain movement types:

- `RECEIPT`: external source -> Main Store;
- `TRANSFER`: Main Store -> selected Sub Store;
- `DISPENSE/USAGE`: selected Sub Store -> customer/consumption;
- `ADJUSTMENT`: controlled balance correction;
- `REVERSAL/CORRECTION`: linked correction of a committed operation.

Sub-to-Sub transfer is deferred until a real workflow requires it.

Committed transfer/dispense history is never destructively edited merely to make totals look correct.

## 3. Current Daily Usage reinterpretation

The current operational sheet named `Daily Usage` is understood to represent Main Store -> Sub Store stock transfer activity rather than final end-customer usage.

Future migration treats supported rows as transfer-source evidence where source data is sufficient.

Rules:

- preserve original `Daily Usage` source provenance;
- never fabricate historical destination Sub Stores when source records do not identify them;
- surface unresolved ambiguity for Owner review;
- future UI terminology uses `Stock Transfer` for the canonical operation.

## 4. Reorder policy

Reorder calculations read an Owner-configurable backend policy:

- `MAIN_STORE_ONLY` — initial/default operational mode;
- `TOTAL_ACTIVE_STOCK` — Main Store + all active Sub Stores.

Only Owner may change this global policy through `Settings`.

Analytics may still display Main, individual Sub Store, and Total stock regardless of active reorder basis.

## 5. Store/location access policy

Role authorization and location scope are separate concepts.

Examples:

- Owner normally sees/manages all locations;
- Admin may manage permitted transfer/operational workflows according to backend policy;
- Staff may be scoped to one or more Sub Stores or other explicitly permitted reads;
- Read-only users receive only allowed read scope;
- AI agents may be granted Main Store, selected Sub Store, all-store, or analysis-only scope by Owner through `AI Agent Management`.

AI agents are **not** inherently Sub-Store-only. Later typed Main Store writes are allowed only when Owner capability policy and the corresponding write/canonicality slices explicitly authorize them.

Location scope is backend-enforced; hidden UI is not authorization.

## 6. Preference persistence

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

Ephemeral device-only state may remain local, but operational preferences should follow the user across clients.

## 7. Smart Calculator

Smart Calculator is a first-class operational tool, not an Excel-import feature.

### Data source

Normal use reads backend product/lot/location data directly.

The Calculator does **not** require a separate Excel upload or manual item/quantity/price mapping. Owner batch intake/import mapping remains a separate ingestion workflow.

### Identity and same-name protection

Display name is not canonical identity. Selection resolves to stable product/lot records, and similar names expose distinguishing strength/form, brand/source, lot/expiry, store availability, and code information where useful.

### Calculation-only mode

`CALCULATE_ONLY` supports item search, quantity, price/reference value, multiple items, extra fees, receiver/customer, issuer, note, subtotal/fees/total, saved calculations, receipt history, and print/PDF/export/share without changing inventory.

### Future dispense mode

`DISPENSE_FROM_SUB_STORE` becomes write-capable only after controlled-write authorization.

At commit time backend must validate current selected Sub Store stock, user/agent authority, exact product/lot identity, operation ID/idempotency, atomic deduction, actor-aware audit, receipt linkage, and committed-state readback.

## 8. AI/photo-to-calculation direction

A future scan/photo flow may:

1. extract candidate text/items/quantities;
2. call typed product search;
3. rank candidate matches;
4. require explicit selection for ambiguous same-name items;
5. build a draft Smart Calculator session;
6. allow human review/edit;
7. never auto-commit inventory solely from OCR/LLM interpretation.

## 9. Smart Analysis

Smart Analysis remains deterministic first and AI-assisted second.

Initial modules:

1. Stock Health
2. Transfer / Usage Trends
3. Expiry Risk
4. Reorder Outlook
5. Price Movement
6. Data Quality

Metrics support Main Store, individual Sub Stores, Total active stock, transfer velocity, and later reliable dispense/consumption velocity. Charts/KPIs remain traceable to supporting rows/lots/operations.

## 10. Internal AI Assistant

The internal Assistant is an identifiable `AI_AGENT` principal and uses typed tools over authorized backend data.

The Owner may enable AI Chat for selected human roles/users. AI Chat is an operational feature, not the Agent Management control plane.

When a human uses AI Chat:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

The Assistant may compare Main/Sub/Total stock, explain trends, identify expiry/reorder risk, discuss price/data quality, generate charts/tables, prepare Calculator drafts, and summarize audit history.

Initial mode remains read-only. Future write tools reuse the Owner-configured F7.2D Agent Management policy and F7.3 Audit model.

No arbitrary SQL or DB credentials are exposed.

## 11. Alerts & Notifications

Alerts originate from deterministic facts/events first.

Candidate events include low Main stock, low Total stock according to policy, Sub Store refill pressure, expiry, unusual transfer/dispense patterns, data-quality/mapping problems, sync failures, access/reset requests, and later scheduled analysis.

One backend event may surface through Web, Telegram, Flutter, or other clients. AI may explain/prioritize but does not replace the triggering fact.

## 12. Multi-client principle

Web, Telegram, Flutter, internal AI, Custom GPT, and system jobs are clients of the same backend.

They reuse canonical human/agent identities, RBAC/delegation, location scope, preferences, product/lot/location data, Calculator/receipts, analytics, notifications, typed inventory operations, and actor-aware Audit.

Flutter may later support offline-tolerant caching for usability, but the cache is not a second canonical inventory database.

## 13. Implementation order

1. F7.2A — canonical multi-user identity
2. F7.2B — User Management
3. F7.2C — credential lifecycle
4. F7.2D — AI Agent Management & delegated authority
5. F7.3 — actor-aware Audit / operation ledger
6. F7.4 — locations, store policy, preferences
7. F7.5 — Smart Calculator / receipts (calculation-only)
8. F7.6 — Smart Analysis
9. F7.7 — internal AI Assistant
10. F7.8 — Alerts & Notifications
11. F8 — external/Custom GPT read-only integration
12. F9 — controlled typed writes
13. F10 — real workflow + fresh migration + Sheet sync validation
14. F11 — explicit canonical promotion

## Safety boundary

This architecture does not authorize production inventory mutation, canonical DB promotion, direct LLM-to-DB writes, direct LLM-to-Sheet mutation, or silent migration of ambiguous historical rows.
