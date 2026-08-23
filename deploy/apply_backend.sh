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

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm \
  api sh -c 'grep -Fq "user-profile-card" app/dashboard_assets/dashboard.html && grep -Fq "User Management" app/dashboard_assets/dashboard.html && grep -Fq "AI Agent Management" app/dashboard_assets/dashboard.html && grep -Fq "Multi-agent sessions" app/dashboard_assets/dashboard.html && grep -Fq "dashboard_agents.js" app/dashboard_assets/dashboard.html && grep -Fq "External / MCP agents" app/dashboard_assets/dashboard_agents.js && grep -Fq "Internal / provider-backed agents" app/dashboard_assets/dashboard_agents.js && grep -Fq "Provider Registry" app/dashboard_assets/dashboard_agents.js && grep -Fq "classList.add('"'"'secondary'"'"')" app/dashboard_assets/dashboard_agents.js && grep -Fq "Account security" app/dashboard_assets/dashboard.html && grep -Fq "Change username" app/dashboard_assets/dashboard.html && grep -Fq "Change password" app/dashboard_assets/dashboard.html && grep -Fq "Request access" app/dashboard_assets/login.html && grep -Fq "Confirm password" app/dashboard_assets/login.html && grep -Fq "Forgot password" app/dashboard_assets/login.html && grep -Fq "verified recovery email" app/dashboard_assets/login.html && grep -Fq "One-time reset" app/dashboard_assets/login.html && grep -Fq "Recovery email" app/dashboard_assets/recovery_email.html && echo "f7_2d2_d3_ui_contract=pass"'

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
  '/dashboard/api/review-reasons' \
  '/dashboard/api/access-requests' \
  '/dashboard/api/access-requests/confirmed' \
  '/dashboard/api/users' \
  '/dashboard/api/users/{user_id}/approve' \
  '/dashboard/api/users/{user_id}/reject' \
  '/dashboard/api/users/{user_id}/role' \
  '/dashboard/api/users/{user_id}/disable' \
  '/dashboard/api/users/{user_id}/reactivate' \
  '/dashboard/api/users/{user_id}/revoke-sessions' \
  '/dashboard/api/agents' \
  '/dashboard/api/agents/{agent_id}' \
  '/dashboard/api/agents/{agent_id}/disable' \
  '/dashboard/api/agents/{agent_id}/reactivate' \
  '/dashboard/api/agents/{agent_id}/revoke' \
  '/dashboard/api/agents/sessions/list' \
  '/dashboard/api/agents/sessions' \
  '/dashboard/api/agents/sessions/{session_id}' \
  '/dashboard/api/agents/sessions/{session_id}/close' \
  '/dashboard/api/agents/sessions/{session_id}/reopen' \
  '/dashboard/api/providers' \
  '/dashboard/api/providers/{provider_id}' \
  '/dashboard/api/providers/{provider_id}/credential' \
  '/dashboard/api/providers/{provider_id}/test' \
  '/dashboard/api/providers/{provider_id}/models/fetch' \
  '/dashboard/api/providers/{provider_id}/models' \
  '/dashboard/api/providers/{provider_id}/enable' \
  '/dashboard/api/providers/{provider_id}/disable' \
  '/dashboard/api/account/username' \
  '/dashboard/api/account/password' \
  '/dashboard/api/account/recovery-email' \
  '/dashboard/api/recovery-email-verifications/complete' \
  '/dashboard/api/password-recovery/request' \
  '/dashboard/api/password-reset-requests' \
  '/dashboard/api/password-reset-requests/{request_id}/issue' \
  '/dashboard/api/password-resets/complete'; do
  grep -Fq "\"${route}\"" <<<"$OPENAPI"
done

LOGIN_BODY="$(curl --fail --silent --show-error "http://127.0.0.1:${API_PORT}/dashboard/login")"
grep -Fq 'Secure dashboard access' <<<"$LOGIN_BODY"
grep -Fq '>Username<' <<<"$LOGIN_BODY"
grep -Fq '>Password<' <<<"$LOGIN_BODY"
grep -Fq 'Confirm password' <<<"$LOGIN_BODY"
grep -Fq 'Request access' <<<"$LOGIN_BODY"
grep -Fq 'Forgot password' <<<"$LOGIN_BODY"

CONFIRM_MISMATCH_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' -X POST -H 'Content-Type: application/json' -d '{"display_name":"Verifier","username":"confirm-mismatch-verifier","password":"abcdefghij","confirm_password":"abcdefghik"}' "http://127.0.0.1:${API_PORT}/dashboard/api/access-requests/confirmed")"
if [[ "$CONFIRM_MISMATCH_STATUS" != "400" ]]; then
  echo "error: confirmed access request mismatch returned HTTP ${CONFIRM_MISMATCH_STATUS}, expected 400" >&2
  exit 1
fi

RECOVERY_UNKNOWN_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' -X POST -H 'Content-Type: application/json' -d '{"username":"msa-definitely-unknown-recovery-user"}' "http://127.0.0.1:${API_PORT}/dashboard/api/password-recovery/request")"
if [[ "$RECOVERY_UNKNOWN_STATUS" != "202" ]]; then
  echo "error: unknown-user automated recovery returned HTTP ${RECOVERY_UNKNOWN_STATUS}, expected enumeration-safe 202" >&2
  exit 1
fi

ANON_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "http://127.0.0.1:${API_PORT}/v1/shadow/batches")"
if [[ "$ANON_STATUS" != "401" ]]; then
  echo "error: anonymous shadow read returned HTTP ${ANON_STATUS}, expected 401" >&2
  exit 1
fi

ANON_USERS_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "http://127.0.0.1:${API_PORT}/dashboard/api/users")"
if [[ "$ANON_USERS_STATUS" != "401" && "$ANON_USERS_STATUS" != "503" ]]; then
  echo "error: anonymous User Management returned HTTP ${ANON_USERS_STATUS}, expected 401 or fail-closed 503" >&2
  exit 1
fi

ANON_AGENTS_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "http://127.0.0.1:${API_PORT}/dashboard/api/agents")"
if [[ "$ANON_AGENTS_STATUS" != "401" && "$ANON_AGENTS_STATUS" != "503" ]]; then
  echo "error: anonymous Agent Management returned HTTP ${ANON_AGENTS_STATUS}, expected 401 or fail-closed 503" >&2
  exit 1
fi

ANON_PROVIDERS_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "http://127.0.0.1:${API_PORT}/dashboard/api/providers")"
if [[ "$ANON_PROVIDERS_STATUS" != "401" && "$ANON_PROVIDERS_STATUS" != "503" ]]; then
  echo "error: anonymous Provider Registry returned HTTP ${ANON_PROVIDERS_STATUS}, expected 401 or fail-closed 503" >&2
  exit 1
fi

ANON_ACCOUNT_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' -X POST -H 'Content-Type: application/json' -d '{"current_password":"x","new_password":"1234567890"}' "http://127.0.0.1:${API_PORT}/dashboard/api/account/password")"
if [[ "$ANON_ACCOUNT_STATUS" != "401" && "$ANON_ACCOUNT_STATUS" != "503" ]]; then
  echo "error: anonymous account credential change returned HTTP ${ANON_ACCOUNT_STATUS}, expected 401 or fail-closed 503" >&2
  exit 1
fi

ANON_RECOVERY_EMAIL_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "http://127.0.0.1:${API_PORT}/dashboard/api/account/recovery-email")"
if [[ "$ANON_RECOVERY_EMAIL_STATUS" != "401" && "$ANON_RECOVERY_EMAIL_STATUS" != "503" ]]; then
  echo "error: anonymous recovery-email state returned HTTP ${ANON_RECOVERY_EMAIL_STATUS}, expected 401 or fail-closed 503" >&2
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

# Exercise canonical identity plus the full F7.2B/F7.2C account lifecycle against the running API.
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T \
  -e MSA_DASHBOARD_VERIFY_BASE_URL=http://127.0.0.1:8080 \
  api python -m app.dashboard_runtime_verify

# Exercise F7.2D2 named identity, Owner-only management, lifecycle, and multi-agent session topology.
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T \
  -e MSA_DASHBOARD_VERIFY_BASE_URL=http://127.0.0.1:8080 \
  api python -m app.agent_management_verify

# Exercise F7.2D3 Provider Registry without making any real provider API call.
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T \
  api python -m app.provider_registry_verify

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

PUBLIC_USERS_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "${PUBLIC_BASE_URL}/dashboard/api/users")"
if [[ "$PUBLIC_USERS_STATUS" != "401" && "$PUBLIC_USERS_STATUS" != "503" ]]; then
  echo "error: public unauthenticated User Management returned HTTP ${PUBLIC_USERS_STATUS}, expected 401 or fail-closed 503" >&2
  exit 1
fi

PUBLIC_AGENTS_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "${PUBLIC_BASE_URL}/dashboard/api/agents")"
if [[ "$PUBLIC_AGENTS_STATUS" != "401" && "$PUBLIC_AGENTS_STATUS" != "503" ]]; then
  echo "error: public unauthenticated Agent Management returned HTTP ${PUBLIC_AGENTS_STATUS}, expected 401 or fail-closed 503" >&2
  exit 1
fi

PUBLIC_PROVIDERS_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "${PUBLIC_BASE_URL}/dashboard/api/providers")"
if [[ "$PUBLIC_PROVIDERS_STATUS" != "401" && "$PUBLIC_PROVIDERS_STATUS" != "503" ]]; then
  echo "error: public unauthenticated Provider Registry returned HTTP ${PUBLIC_PROVIDERS_STATUS}, expected 401 or fail-closed 503" >&2
  exit 1
fi

echo "shadow_routes=pass shadow_test_batch=pass anonymous_auth_guard=pass"
echo "f7_2a_identity=pass canonical_owner=pass username_password=pass durable_sessions=pass backend_rbac=pass access_denied_403=pass disabled_user_denied=pass"
echo "f7_2b_user_management=pass request_pending=pass approval=pass rejection=pass role_assignment=pass disable_reactivate=pass session_revoke=pass owner_escalation_guard=pass account_events=pass notification_events=pass profile_ui=pass"
echo "f7_2c_credential_lifecycle=pass username_change=pass password_change=pass current_password_reauth=pass reset_enumeration_safe=pass owner_reset_issue=pass reset_token_digest_only=pass reset_single_use=pass credential_session_revoke=pass credential_events=pass account_ui=pass"
echo "f7_2c1_email_recovery_foundation=pass confirm_password=pass automated_recovery_enumeration_safe=pass recovery_email_auth_guard=pass provider_activation_optional=pass"
echo "f7_2d2_agent_management=pass named_agents=pass self_identity=pass multi_agent_sessions=pass system_write_gate=closed"
echo "f7_2d3_provider_registry=pass provider_crud=pass credential_write_only=pass model_catalog=pass provider_execution=not_invoked"
echo "dashboard_public_route=pass dashboard_public_private_gate=pass:${PUBLIC_PRIVATE_STATUS} user_management_public_gate=pass:${PUBLIC_USERS_STATUS} agent_management_public_gate=pass:${PUBLIC_AGENTS_STATUS} provider_registry_public_gate=pass:${PUBLIC_PROVIDERS_STATUS} public_base=${PUBLIC_BASE_URL}"
echo "MSA backend deployed at ${CURRENT_SHA}; inventory remains read-only; no live workbook import executed."