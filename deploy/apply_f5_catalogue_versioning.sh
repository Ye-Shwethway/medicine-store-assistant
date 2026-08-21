#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${MSA_RUNTIME_ENV:-/opt/medicine-store-assistant/secrets/runtime.env}"
COMPOSE_FILE="$REPO_DIR/deploy/docker-compose.yml"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "error: runtime env not found: $ENV_FILE" >&2
  exit 1
fi

cd "$REPO_DIR"
python3 scripts/validate_repository.py

CURRENT_SHA="$(git rev-parse HEAD)"
if grep -q '^MSA_BUILD_SHA=' "$ENV_FILE"; then
  sed -i "s/^MSA_BUILD_SHA=.*/MSA_BUILD_SHA=${CURRENT_SHA}/" "$ENV_FILE"
else
  printf '\nMSA_BUILD_SHA=%s\n' "$CURRENT_SHA" >> "$ENV_FILE"
fi
chmod 600 "$ENV_FILE"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config --quiet
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build api
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d db
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm api alembic upgrade head
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm api python -m app.catalogue_verify
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d api

API_PORT="$(awk -F= '$1 == "MSA_API_HOST_PORT" {print $2}' "$ENV_FILE" | tail -n1)"
API_PORT="${API_PORT:-8088}"

wait_for_url() {
  local url="$1"
  local attempts=30
  local delay=1
  local i
  for ((i=1; i<=attempts; i++)); do
    if curl --fail --silent --show-error "$url"; then
      echo
      return 0
    fi
    sleep "$delay"
  done
  echo "error: endpoint did not become ready: $url" >&2
  return 1
}

wait_for_url "http://127.0.0.1:${API_PORT}/health"
wait_for_url "http://127.0.0.1:${API_PORT}/ready"

echo "F5 synthetic catalogue versioning applied and verified at ${CURRENT_SHA}."
