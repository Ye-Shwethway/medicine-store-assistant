#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${MSA_RUNTIME_ENV:-/opt/medicine-store-assistant/secrets/runtime.env}"
COMPOSE_FILE="$REPO_DIR/deploy/docker-compose.yml"

if [[ ! -r "$ENV_FILE" ]]; then
  echo "error: runtime env is not readable: $ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${MSA_GOOGLE_SPREADSHEET_ID:?MSA_GOOGLE_SPREADSHEET_ID is required}"
: "${MSA_GOOGLE_SERVICE_ACCOUNT_FILE:?MSA_GOOGLE_SERVICE_ACCOUNT_FILE is required}"

if [[ ! -r "$MSA_GOOGLE_SERVICE_ACCOUNT_FILE" ]]; then
  echo "error: Google service-account file is not readable by runner" >&2
  exit 1
fi

cd "$REPO_DIR"
python3 scripts/validate_repository.py
python3 -m compileall -q backend/app backend/alembic

CURRENT_SHA="$(git rev-parse HEAD)"
export MSA_BUILD_SHA="$CURRENT_SHA"
export COMPOSE_PROJECT_NAME="${MSA_COMPOSE_PROJECT_NAME:-deploy}"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config --quiet
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build api
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d db

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm \
  -e MSA_GOOGLE_SPREADSHEET_ID="$MSA_GOOGLE_SPREADSHEET_ID" \
  -e MSA_GOOGLE_SERVICE_ACCOUNT_FILE=/run/secrets/msa-google-service-account.json \
  -v "$MSA_GOOGLE_SERVICE_ACCOUNT_FILE:/run/secrets/msa-google-service-account.json:ro" \
  api python -m app.live_shadow_import

echo "F6B TEST-ONLY live workbook shadow snapshot staged at ${CURRENT_SHA}."
echo "This command is not part of normal backend deployment and does not establish a migration baseline."
