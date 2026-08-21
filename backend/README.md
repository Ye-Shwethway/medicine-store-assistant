# Medicine Store Assistant Backend

Status: **F1 runtime skeleton**

This directory contains the future deterministic Inventory API. The published Git-backed skill remains separate at `skills/medicine-store-assistant/`.

## Current F1 capability

- FastAPI process
- deterministic `GET /health`
- automatic FastAPI OpenAPI generation
- no inventory schema
- no canonical stock writes
- no Google Sheet mutation

## Run directly for development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8080
```

Then:

```bash
curl http://127.0.0.1:8080/health
```

Expected fields include `ok`, `service`, `environment`, `version`, `build_sha`, and `database_canonical=false`.

## Boundary

Do not add canonical inventory tables/migrations or write operations during F1. Schema work begins only after the gating decisions in `docs/architecture/DECISIONS_AND_OPEN_QUESTIONS.md` are resolved and F2 is authorized.
