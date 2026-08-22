#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${MSA_RUNTIME_ENV:-/opt/medicine-store-assistant/secrets/runtime.env}"
COMPOSE_FILE="$REPO_DIR/deploy/docker-compose.yml"
PUBLIC_BASE_URL="${MSA_PUBLIC_BASE_URL:-https://inventory.drthorne.uk}"

if [[ ! -r "$ENV_FILE" ]]; then
  echo "error: runtime env is not readable: $ENV_FILE" >&2
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

for _ in $(seq 1 30); do
  if docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db \
      sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db \
  sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm api alembic upgrade head

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm \
  api python -m app.dashboard_verify

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm \
  api python -m app.shadow_read_verify

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm \
  api python -c 'from app.dashboard_auth import ensure_bootstrap_owner; u=ensure_bootstrap_owner(); print("canonical_owner_bootstrap=pass user_id=" + u["user_id"] + " username=" + u["username"])'

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d api

API_PORT="$(awk -F= '$1 == "MSA_API_HOST_PORT" {print $2}' "$ENV_FILE" | tail -n1)"
API_PORT="${API_PORT:-8088}"

wait_for_url() {
  local url="$1"
  for _ in $(seq 1 30); do
    if curl --fail --silent --show-error "$url" >/dev/null; then
      return 0
    fi
    sleep 1
  done
  echo "error: endpoint did not become ready: $url" >&2
  return 1
}

wait_for_url "http://127.0.0.1:${API_PORT}/health"
wait_for_url "http://127.0.0.1:${API_PORT}/ready"
wait_for_url "http://127.0.0.1:${API_PORT}/dashboard/login"
wait_for_url "http://127.0.0.1:${API_PORT}/dashboard/api/session"

OPENAPI="$(curl --fail --silent --show-error "http://127.0.0.1:${API_PORT}/openapi.json")"
for route in \
  '/v1/shadow/batches' \
  '/v1/shadow/batches/{migration_batch_id}' \
  '/v1/shadow/rows' \
  '/v1/shadow/review-reasons' \
  '/dashboard/api/session' \
  '/dashboard/api/authorization/owner' \
  '/dashboard/api/overview' \
  '/dashboard/api/rows' \
  '/dashboard/api/review-reasons'; do
  grep -Fq "\"${route}\"" <<<"$OPENAPI"
done

LOGIN_BODY="$(curl --fail --silent --show-error "http://127.0.0.1:${API_PORT}/dashboard/login")"
grep -Fq 'Secure dashboard access' <<<"$LOGIN_BODY"
grep -Fq '>Username<' <<<"$LOGIN_BODY"
grep -Fq '>Password<' <<<"$LOGIN_BODY"

ANON_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "http://127.0.0.1:${API_PORT}/v1/shadow/batches")"
if [[ "$ANON_STATUS" != "401" ]]; then
  echo "error: anonymous shadow read returned HTTP ${ANON_STATUS}, expected 401" >&2
  exit 1
fi

DASHBOARD_REDIRECT="$(curl --silent --output /dev/null --write-out '%{http_code}:%{redirect_url}' "http://127.0.0.1:${API_PORT}/dashboard")"
case "$DASHBOARD_REDIRECT" in
  307:*'/dashboard/login') ;;
  *) echo "error: unauthenticated dashboard did not redirect to dedicated login: ${DASHBOARD_REDIRECT}" >&2; exit 1 ;;
esac

DASHBOARD_PRIVATE_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "http://127.0.0.1:${API_PORT}/dashboard/api/overview")"
if [[ "$DASHBOARD_PRIVATE_STATUS" != "401" && "$DASHBOARD_PRIVATE_STATUS" != "503" ]]; then
  echo "error: unauthenticated dashboard BFF returned HTTP ${DASHBOARD_PRIVATE_STATUS}, expected 401 or fail-closed 503" >&2
  exit 1
fi

# Exercise canonical human identity, revocable sessions, RBAC, disabled-user denial,
# and the existing read-only dashboard against the running API.
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T \
  -e MSA_DASHBOARD_VERIFY_BASE_URL=http://127.0.0.1:8080 \
  api python -m app.dashboard_runtime_verify

wait_for_url "${PUBLIC_BASE_URL}/health"
wait_for_url "${PUBLIC_BASE_URL}/dashboard/login"
wait_for_url "${PUBLIC_BASE_URL}/dashboard/api/session"

PUBLIC_SESSION="$(curl --fail --silent --show-error "${PUBLIC_BASE_URL}/dashboard/api/session")"
grep -Fq '"database_canonical":false' <<<"$PUBLIC_SESSION"
grep -Fq '"migration_baseline_accepted":false' <<<"$PUBLIC_SESSION"

PUBLIC_PRIVATE_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "${PUBLIC_BASE_URL}/dashboard/api/overview")"
if [[ "$PUBLIC_PRIVATE_STATUS" != "401" && "$PUBLIC_PRIVATE_STATUS" != "503" ]]; then
  echo "error: public unauthenticated dashboard BFF returned HTTP ${PUBLIC_PRIVATE_STATUS}, expected 401 or fail-closed 503" >&2
  exit 1
fi

echo "shadow_routes=pass shadow_test_batch=pass anonymous_auth_guard=pass"
echo "f7_2a_identity=pass canonical_owner=pass username_password=pass durable_sessions=pass backend_rbac=pass access_denied_403=pass disabled_user_denied=pass"
echo "dashboard_public_route=pass dashboard_public_private_gate=pass:${PUBLIC_PRIVATE_STATUS} public_base=${PUBLIC_BASE_URL}"
echo "MSA backend deployed at ${CURRENT_SHA}; inventory remains read-only; no live workbook import executed."
