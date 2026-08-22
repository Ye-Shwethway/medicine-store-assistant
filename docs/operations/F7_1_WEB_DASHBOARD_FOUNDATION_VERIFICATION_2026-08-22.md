# F7.1 Web Dashboard Foundation Verification — 2026-08-22

Status: **verified complete**

## Scope

F7.1 established the first deployed browser-facing Medicine Store Assistant dashboard while preserving the current authority boundary:

- Google Sheets remains operationally authoritative;
- PostgreSQL remains non-canonical;
- the existing F6B/F6C Google-sheet snapshot remains test-only;
- no inventory write operation or live workbook import was added.

The approved Dashboard v2.4 visual/interaction baseline is implemented as a FastAPI-served HTML/CSS/vanilla-JavaScript UI with a server-side read-only BFF and a fail-closed owner-session boundary.

## Implementation PR

PR #14 — `Implement F7.1 read-only web dashboard foundation`

- validation source SHA: `bc2b17c3efddf969308e3dfe5b6a412f57f04da3`
- validation run: `32568157999`
- validation job: `97019708898`
- validation result: **success**
- merge SHA: `99b41c32c55d59e4acaafd44be77b78d93ed5889`
- automatic deploy run: `32568177813`
- deploy job: `97019754068`
- deploy result: **success**

Validated CI checks included repository contract validation, Python compilation, dashboard JavaScript syntax validation, and deployment-shell syntax validation.

## Public-route verification PR

PR #15 — `Verify F7 dashboard through public HTTPS route`

- validation source SHA: `905ff2622ca5a52003071ea34514a9b3ca6f559d`
- validation run: `32568290679`
- validation result: **success**
- merge SHA: `e114ce9abcde30f727315eea0c4314a5047f1c29`
- automatic deploy run: `32568305770`
- deploy job: `97020051556`
- deploy result: **success**
- deployment evidence marker commit: `0f9401baed9f950b1fb6abd507cc285f150f1c8b`

`.github/backend-deploy-result` recorded:

```text
status=success
source_sha=e114ce9abcde30f727315eea0c4314a5047f1c29
workflow_run_id=32568305770
```

## Verified runtime behavior

The self-hosted production runner verified both localhost origin behavior and the managed Cloudflare public HTTPS route.

Local runtime verification:

- F7 dashboard auth primitive verification: **PASS**
- password-hash verification: **PASS**
- signed-session verification: **PASS**
- tamper rejection: **PASS**
- F6C shadow read foundation verification: **PASS**
- test-only batch provenance/classification verification: **PASS**
- `/health`: healthy
- `/ready`: database reachable; migration `0004_shadow`
- `/dashboard`: served successfully
- `/dashboard/api/session`: served successfully
- anonymous `/v1/shadow/batches`: HTTP 401
- unauthenticated `/dashboard/api/overview`: HTTP 503 because owner dashboard credentials are intentionally not yet provisioned

The deploy log explicitly reported:

```text
F7 dashboard auth foundation verification PASS
password_hash=pass session_signature=pass tamper_guard=pass
F6C shadow read foundation verification PASS
test_only_batch=pass provenance=pass classification_summary=pass migration_baseline_accepted=false database_canonical=false
dashboard_auth_foundation=pass dashboard_shell=pass dashboard_session_state=pass dashboard_private_gate=pass:503
```

## Public HTTPS verification

The VPS runner verified through:

`https://inventory.drthorne.uk`

Successful public checks:

- `GET /health`
- `GET /dashboard`
- `GET /dashboard/api/session`

The public session response preserved:

- `database_canonical=false`
- `migration_baseline_accepted=false`

The unauthenticated public private-data endpoint:

`GET /dashboard/api/overview`

returned HTTP **503**, which is the intended fail-closed state before F7.2 owner credential provisioning.

The deploy log explicitly reported:

```text
dashboard_public_route=pass dashboard_public_private_gate=pass:503 public_base=https://inventory.drthorne.uk
```

## Current test dataset evidence

The existing test-only batch remains unchanged:

- batch ID: `be13d127-5045-4284-a088-0a0b9b024d76`
- rows: 1,646
- SAFE: 1,417
- REVIEW: 222
- CONFLICT: 0
- NEW_UNMAPPED: 7
- `migration_baseline_accepted=false`
- `database_canonical=false`

No new Google workbook snapshot was imported during F7.1 deployment.

## Dashboard security boundary

Verified implementation properties:

- existing F3 Bearer service credential is not placed in browser JavaScript or browser storage;
- owner password is represented server-side only as PBKDF2-SHA256 hash;
- dashboard session is HMAC-signed and uses HttpOnly + Secure + SameSite=Strict cookie semantics;
- missing dashboard owner credentials disable the private data plane fail-closed;
- dashboard/private JSON uses no-store cache policy;
- dashboard shell applies CSP, frame-denial, referrer, and MIME-sniffing protections;
- no arbitrary SQL interface is exposed;
- no edit/save/write UI is enabled.

## Approved interaction baseline

Dashboard v2.4 remains locked as the implementation baseline, including:

- responsive sidebar/mobile drawer;
- visual sun/moon Light/Dark theme toggle;
- spreadsheet-like horizontal and vertical table gridlines;
- Inventory `← Overview` return path;
- item detail drawer;
- expanded table focus mode with exit path;
- search and classification/source-sheet filters;
- permanent test/non-canonical state indicators while those facts remain true.

## No-live-import evidence

Both F7.1 deployment runs explicitly reported that no live workbook import executed. Normal deployment remains independent of the Google Sheets reader credential and does not stage a new snapshot.

## Next authorized implementation direction

F7.2 is the next slice:

1. provision dashboard owner authentication secrets in the protected VPS runtime environment;
2. keep those secrets out of Git and browser code;
3. verify owner login through public HTTPS;
4. verify authenticated dashboard BFF reads against the existing F6C test-only dataset;
5. regression-test navigation, theme switching, search/filtering, row detail, full-table mode, logout, and unauthenticated rejection.

F7.2 does not authorize inventory writes, Google Sheet mutation, migration promotion, or canonical database promotion.
