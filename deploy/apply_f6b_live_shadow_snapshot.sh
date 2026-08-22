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

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d api

API_PORT="$(awk -F= '$1 == "MSA_API_HOST_PORT" {print $2}' "$ENV_FILE" | tail -n1)"
API_PORT="${API_PORT:-8088}"

wait_for_url() {
  local url="$1"
  for _ in $(seq 1 30); do
    if curl --fail --silent --show-error "$url"; then
      echo
      return 0
    fi
    sleep 1
  done
  echo "error: endpoint did not become ready: $url" >&2
  return 1
}

wait_for_url "http://127.0.0.1:${API_PORT}/health"
wait_for_url "http://127.0.0.1:${API_PORT}/ready"

echo "F6B live workbook shadow snapshot imported at ${CURRENT_SHA}."
