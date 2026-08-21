#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${MSA_RUNTIME_ENV:-/opt/medicine-store-assistant/secrets/runtime.env}"
TOKEN_FILE="${MSA_F3_TOKEN_FILE:-/opt/medicine-store-assistant/secrets/f3_read_api.token}"
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
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d db api

API_PORT="$(awk -F= '$1 == "MSA_API_HOST_PORT" {print $2}' "$ENV_FILE" | tail -n1)"
API_PORT="${API_PORT:-8088}"
BASE_URL="http://127.0.0.1:${API_PORT}"

wait_for_url() {
  local url="$1"
  local attempts="${2:-30}"
  local delay="${3:-1}"
  local i
  for ((i=1; i<=attempts; i++)); do
    if curl --fail --silent --show-error "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$delay"
  done
  echo "error: timed out waiting for $url" >&2
  return 1
}

wait_for_url "$BASE_URL/health"
wait_for_url "$BASE_URL/ready"

UNAUTH_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "$BASE_URL/v1/products")"
if [[ "$UNAUTH_STATUS" != "401" ]]; then
  echo "error: expected unauthenticated /v1/products to return 401, got $UNAUTH_STATUS" >&2
  exit 1
fi

TOKEN="$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm api python -m app.service_key_cli --name f3-read-verifier --scope inventory:read --raw)"
mkdir -p "$(dirname "$TOKEN_FILE")"
printf '%s\n' "$TOKEN" > "$TOKEN_FILE"
chmod 600 "$TOKEN_FILE"

AUTH_BODY="$(curl --fail --silent --show-error -H "Authorization: Bearer $TOKEN" "$BASE_URL/v1/products")"

printf '%s\n' "$(curl --fail --silent --show-error "$BASE_URL/health")"
printf '%s\n' "$(curl --fail --silent --show-error "$BASE_URL/ready")"
printf '%s\n' "anonymous /v1/products -> HTTP 401"
printf '%s\n' "$AUTH_BODY"
printf '%s\n' "F3 authenticated read-only API verified at ${CURRENT_SHA}."
printf '%s\n' "Read credential stored at ${TOKEN_FILE} with mode 0600; token not printed."
