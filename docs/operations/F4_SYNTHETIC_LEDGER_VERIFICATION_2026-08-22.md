# F4 Synthetic Ledger Verification — 2026-08-22

Status: **verified complete**

## Deployed revision

`184f964a86cfb00696f4f2622e41289ab53f165a`

## Verification command

```bash
cd /opt/medicine-store-assistant/app/repo && git pull --ff-only && bash deploy/apply_f4_ledger_foundation.sh
```

## Verified results

- repository fast-forwarded from F3 revision `dac1a4a...` to `184f964a86cfb00696f4f2622e41289ab53f165a`;
- repository validator passed for Git-backed `medicine-store-assistant` plugin 1.1.0;
- API image rebuilt successfully;
- PostgreSQL remained running on the existing private deployment network;
- Alembic upgraded `0001_foundation -> 0002_ledger` successfully;
- synthetic ledger verifier reported `F4 synthetic ledger verification PASS`;
- balance math passed;
- duplicate-operation/idempotency protection passed;
- normal negative-stock guard passed;
- linked reversal/correction semantics passed;
- synthetic product/lot/transaction fixture data ran inside a transaction and was rolled back by the verifier;
- API was recreated and restarted successfully;
- transient `curl: (56) Recv failure: Connection reset by peer` messages occurred during the API restart window, after which the deployment helper retry loop obtained successful health/readiness responses;
- `/health` returned healthy service metadata with build SHA `184f964a86cfb00696f4f2622e41289ab53f165a` and `database_canonical: false`;
- `/ready` returned `database: reachable`, migration `0002_ledger`, expected migration `0002_ledger`, and `database_canonical: false`;
- deploy helper completed with `F4 synthetic ledger foundation applied and verified at 184f964a86cfb00696f4f2622e41289ab53f165a`.

## F4 exit criteria

All F4 exit criteria passed:

1. deterministic balance calculation verified;
2. duplicate replay cannot duplicate stock movement;
3. normal negative-stock writes are blocked;
4. correction/reversal linkage is preserved;
5. migration `0002_ledger` is applied and readiness agrees with the expected migration;
6. synthetic verification does not retain fixture inventory data;
7. PostgreSQL remains explicitly non-canonical.

## Safety boundary preserved

F4 introduced no public production inventory-write endpoint and did not import or mutate live Google Sheet inventory.

The live Google workbook/source documents remain authoritative. PostgreSQL is still a non-canonical backend foundation. No database promotion, live shadow import, Telegram write path, Flutter rollout, Google Sheet mirror conversion, or Custom GPT write Action is authorized by this verification.
