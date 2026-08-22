# F5 / F5.1 Catalogue Verification — 2026-08-22

Status: **verified complete**

## Verified deployment

Source commit: `3a49c8edb63c4c3f38da8508ebf3187962224bb7`

GitHub Actions workflow run: `32546107503`

Runner: repository-scoped self-hosted `msa-vps-runner-01` with labels `self-hosted`, `linux`, `msa-vps`.

## Verified results

- runner preflight passed with `msa-runner` in `docker` and `medstore` groups;
- VPS runtime secret file was readable by the runner without copying secrets into GitHub;
- repository validator passed for `medicine-store-assistant` plugin 1.1.0;
- API image built successfully;
- PostgreSQL container remained on the existing private deployment network;
- Alembic reached migration `0003_catalogue`;
- `F5 synthetic catalogue verification PASS`;
- `hash_idempotency=pass`;
- `version_history=pass`;
- `add_remove_diff=pass`;
- `price_diff=pass`;
- `identity_shift_guard=pass`;
- `F5.1 authenticated catalogue read surface verification PASS`;
- catalogue version list, current diagnostics, historical items, and deterministic version diff GET surfaces were present;
- no catalogue POST/PUT/PATCH/DELETE surface was present;
- API restarted successfully;
- transient connection-reset messages occurred only during container recreation and were followed by successful retry-loop checks;
- `/health` returned healthy service metadata with build SHA `3a49c8edb63c4c3f38da8508ebf3187962224bb7` and `database_canonical: false`;
- `/ready` returned database reachable with migration and expected migration both `0003_catalogue` and `database_canonical: false`.

## Safety boundary preserved

F5/F5.1 imported no live CMS catalogue, imported no live Google Sheet inventory, changed no production prices, changed no local product/lot mappings, created no production stock movements, exposed no inventory/catalogue write endpoint, and did not promote PostgreSQL.

The live Google workbook/source documents remain authoritative.

## Deployment model

Normal backend delivery now follows `test -> pull request -> main -> automatic VPS deployment` with path-aware validation. The user does not need to run VPS commands or press a manual Actions deploy button for normal continuation.
