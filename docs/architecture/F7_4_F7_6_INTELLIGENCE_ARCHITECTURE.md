# F7.4–F7.6 — Intelligence Architecture

Status: **approved architecture direction; implementation follows identity/User Management/audit foundations**

## Goal

Medicine Store Assistant should become an intelligent operations system, not merely a database-backed spreadsheet replacement. The intelligence layer combines deterministic analytics, grounded AI interpretation, conversational analysis, charts, alerts, and notifications while keeping operational truth and AI inference clearly separated.

## Core principle — truth first, AI second

The system has two distinct analysis layers.

### Deterministic Analytics Layer

SQL, domain formulas, ledger projections, and explicit business rules calculate reproducible facts such as:

- stock balance and stock value;
- usage trends by item/category/time period;
- fast/slow/non-moving items;
- days-of-stock estimates;
- expiry exposure and expiry-risk buckets;
- reorder candidates and reorder outlook;
- receipt-versus-usage patterns;
- price/CMS catalogue movement;
- stock-out frequency;
- unusual usage or inventory anomalies;
- data-quality and reconciliation problems.

These outputs are authoritative calculations for the selected dataset/version and must be reproducible without an LLM.

### AI Analysis Layer

AI consumes only authorized, structured facts from the Analytics/API layer. It may:

- explain trends;
- summarize what changed;
- prioritize attention;
- compare periods;
- propose follow-up analysis;
- explain anomalies and uncertainty;
- generate professional natural-language insight around charts/tables.

AI must not invent stock balances, prices, expiry dates, quantities, or calculated metrics. When a claim depends on database truth, the response must be grounded in tool/API results.

## Product surfaces

### F7.4 — Smart Analysis

Dedicated dashboard surface with professional data visualization and drill-down.

Initial v1 analysis modules:

1. **Stock Health**
2. **Usage Trends**
3. **Expiry Risk**
4. **Reorder Outlook**
5. **Price Movement**
6. **Data Quality**

UX direction:

- KPI cards with clear date/scope context;
- line/bar/area charts only where they improve understanding;
- category/item/date-range filters;
- drill-down from summary metric to supporting rows/lots/operations;
- chart/table values remain inspectable;
- optional compact AI commentary: `What changed`, `Why it matters`, `Suggested attention`;
- deterministic values visually distinguishable from AI-generated explanation;
- no arbitrary opaque “AI score” unless its formula/model and meaning are explicitly defined.

Smart Analysis must remain useful even when the AI provider is unavailable.

### F7.5 — Internal AI Assistant

A first-party conversational analysis workspace inside the MSA application.

The Assistant may answer questions such as:

- compare usage for an item across recent months;
- show items likely to run low under current consumption;
- identify expiry-risk inventory unlikely to be consumed before expiry;
- explain abnormal usage patterns;
- generate charts/tables from authorized analysis results;
- drill down conversationally from a chart or analysis result.

Initial mode is read-only.

The Assistant uses registered typed tools such as:

- `get_stock_health`
- `get_usage_trend`
- `compare_periods`
- `get_expiry_risk`
- `get_reorder_candidates`
- `get_price_movement`
- `get_data_quality_issues`
- `get_audit_summary`

It never receives arbitrary SQL or raw database credentials.

The Assistant is an identifiable `AI_AGENT` service principal. Its read/tool activity may be logged at an appropriate level; any future write must pass normal RBAC/delegation/idempotency/audit requirements.

### F7.6 — Alerts & Notifications

Alerts are facts/events generated from deterministic rules first, with AI optionally helping explain or prioritize them.

Initial candidate alerts:

- low stock / low days-of-stock;
- expiry approaching;
- unusual usage spike/drop;
- missing/invalid mapping or data-quality issue;
- reconciliation/sync failure;
- pending User Management access/reset requests.

Notification surfaces may include:

- Web notification center;
- Telegram push/mirror later;
- Flutter notifications later;
- future email only if deliberately added.

One backend alert/event should be reusable across surfaces rather than reimplemented independently per client.

## Example shared fact flow

`days_of_stock = current_usable_quantity / average_daily_usage`

The deterministic analytics engine computes the value. The alert engine may create an alert when it crosses a configured threshold. The AI layer may explain the trend and contributing factors. Web may show a chart, Telegram may send a concise alert, and the AI Assistant may discuss the same item — all grounded in the same backend truth.

## Saved and scheduled analysis direction

Later versions may support saved analysis presets such as:

- items below 30 days of stock with rising usage;
- expiry-risk items by category;
- weekly usage anomaly summary.

A saved analysis can later be scheduled and delivered through Web/Telegram/Flutter. Scheduled jobs run as identifiable `SYSTEM` or `AI_AGENT` principals and retain provenance.

## Multi-client architecture

`Web / Telegram / Flutter / Custom GPT`
`               |`
`               v`
`        MSA Application API`
`               |`
`   +-----------+------------+`
`   |           |            |`
` RBAC      Analytics API   Typed Ops API`
`               |            |`
`               +------> PostgreSQL`
`                         |`
`                    Audit / Sync`
`                         |`
`                    Google Sheets`
`
`               AI Layer`
`                  |`
`        +---------+---------+`
`        |                   |`
`   analysis tools       typed actions`
`    (read-only first)      (F9+)`

## Relationship to canonicality

Smart Analysis and the read-only AI Assistant may be developed against clearly labeled shadow/test data before PostgreSQL becomes canonical. Every analysis must indicate the dataset/canonicality context where confusion is possible.

Production recommendations must not imply canonical truth while the database is still non-canonical.

## Implementation order

1. Complete F7.2A/B/C identity, User Management, and credential lifecycle.
2. Implement F7.3 actor-aware operational audit/ledger surface.
3. Implement F7.4 deterministic Smart Analysis and charts.
4. Implement F7.5 internal read-only AI Assistant grounded in analytics/tools.
5. Implement F7.6 Alerts & Notifications.
6. Reuse the same read/analysis APIs for F8 Custom GPT integration.
7. Add controlled typed writes only at F9+ after authorization/audit foundations are proven.
