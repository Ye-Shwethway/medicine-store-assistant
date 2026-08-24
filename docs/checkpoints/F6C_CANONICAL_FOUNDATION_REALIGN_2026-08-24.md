# F6C Canonical Inventory Foundation Realignment — 2026-08-24

Status: **Owner-confirmed architecture realignment**

## Decision

F6C/F6D no longer treat exact legacy Estimated Reorder Qty formula parity or exact monthly Excel formula/macro parity as prerequisites for the canonical inventory foundation.

The old Excel calculations existed to support a manual workflow. The future system has deterministic backend operations plus AI proposal/review workflows and can use richer dynamic planning logic later.

## Canonical foundation now prioritized

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Locked principles:

- one Main Store plus unlimited Sub Stores;
- stable Product and expiry-Lot identity shared across locations;
- quantity truth is location-aware movement history;
- Current Qty is derived/verified from opening/receipt/transfer/usage/adjustment movements;
- Total Store Stock is the aggregate of location balances, not an independent mutable truth;
- internal transfer atomically decreases source and increases destination under one transfer identity;
- Universal CMS Catalogue is global/versioned and separate from local Product identity;
- Product-to-CMS mapping is auditable/version-aware;
- current CMS price and historical receipt/source price remain separate;
- every protected operation resolves stable human/agent identity, operation/idempotency context, audit and read-back;
- Main Stock/Daily Usage remain important operational views, not canonical same-shaped tables.

## Inventory view direction

A useful future default inventory view may expose:

`Local Item Name | CMS Name | Type | Unit | CMS Code | Expiry Date | Original/Opening Qty | Received Qty | Deducted/Used Qty | Current Qty | CMS Price | Store/Location`

`No.` is display/order metadata only.

## Reorder direction

Future reorder/planning may combine usage trends, current/incoming stock, expiry risk, safety stock, lead time, store-specific demand, deterministic modules, AI proposal, agent review and authorized human adjustment/approval.

Exact old Estimated Reorder Qty formula may remain available later as a compatibility/reference strategy, but it does not dictate the schema.

## F6D implication

Next implementation should prioritize:

- Store entity;
- location-aware ledger;
- receipt provenance/destination;
- explicit atomic internal transfer;
- Product/Lot identity;
- Universal CMS Catalogue + mapping;
- actor/audit/idempotency;
- fresh Main-Store-bound shadow import;
- balance/Total Stock/projection proof.

## Canonicality boundary

Google Sheet/source documents remain operationally authoritative. PostgreSQL remains shadow/test and non-canonical. This checkpoint does not authorize production inventory mutations or canonical promotion.
