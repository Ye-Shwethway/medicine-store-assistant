# F6B — Live Workbook Shadow Snapshot Import

Status: **authorized; implementation authored on `test`; runtime credential bootstrap pending**

## Source

Canonical live workbook identified through connected Google Drive:

- title: `Medicine Store Cloud`
- timezone: `Asia/Rangoon`
- required tabs: `Main Stock`, `Daily Usage`

The workbook remains authoritative. F6B only reads it and stages a shadow snapshot in PostgreSQL.

## Source contract observed

`Main Stock` includes the live fields used by F6B such as:

- Items
- Expiry Date
- Unit
- Remaining Stock
- Received Stock
- Stock Status Today
- This Month Usage
- Serial Code
- CS Name

`Daily Usage` includes:

- Items
- Remaining Stock
- Received Stock
- day columns 1–31
- This Month Usage
- This Month Remaining
- Expiry Date

## F6B behavior

The importer:

1. reads only `Main Stock` and `Daily Usage` through the Google Sheets read-only OAuth scope;
2. hashes the complete staged source payload for idempotency;
3. stages source rows in the existing F6A migration provenance tables;
4. preserves source row number and row hash;
5. classifies rows as `SAFE`, `REVIEW`, `CONFLICT`, or `NEW_UNMAPPED`;
6. checks Main Stock balance math: `Remaining + Received - This Month Usage = Stock Status Today`;
7. checks Daily Usage day-column total against `This Month Usage`;
8. checks Daily Usage balance math: `Remaining + Received - This Month Usage = This Month Remaining`;
9. checks Main Stock versus Daily Usage monthly-usage/current-balance agreement by item + expiry;
10. never silently fixes a mismatch or remaps a CMS identity.

F6B does not create canonical products/lots/ledger transactions. It only stages source evidence for reconciliation.

## Runtime credential boundary

The VPS self-hosted runner needs a dedicated Google service account with read-only access to the workbook.

Required runtime settings in `/opt/medicine-store-assistant/secrets/runtime.env`:

```text
MSA_GOOGLE_SPREADSHEET_ID=<private runtime value>
MSA_GOOGLE_SERVICE_ACCOUNT_FILE=/opt/medicine-store-assistant/secrets/google-service-account.json
```

The JSON credential file must remain outside the repository and must never be printed into Actions logs. Recommended host ownership/mode:

```text
root:medstore 0640
```

The service-account email must be shared on the `Medicine Store Cloud` workbook as **Viewer** only.

No OAuth credential, workbook export, or live inventory row may be committed to this public repository.

## Deployment gate

Do not merge the F6B runtime path to `main` until the credential file exists, is readable by `msa-runner`, and the service-account email has Viewer access to the workbook.

Once those prerequisites are verified, promotion remains:

`test -> PR -> main -> automatic self-hosted VPS deployment`

No manual Actions button or manual VPS deployment is required.

## Exit evidence

F6B may be marked verified only after automated runtime evidence proves:

- Google read-only authentication succeeds;
- both required sheets are read;
- a shadow migration batch is staged or an identical snapshot resolves idempotently to the existing batch;
- classification counts are emitted without live row contents;
- no canonical product/lot/ledger mutation is performed;
- `/health` is healthy with `database_canonical: false`;
- `/ready` remains healthy at migration `0004_shadow`.
