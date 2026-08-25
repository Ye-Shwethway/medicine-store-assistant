from pathlib import Path

p=Path('deploy/apply_backend.sh')
s=p.read_text()

anchor='''docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm \\
  api python -c 'from app.dashboard_auth import ensure_bootstrap_owner; u=ensure_bootstrap_owner(); print("canonical_owner_bootstrap=pass user_id=" + u["user_id"] + " username=" + u["username"])'\n'''
insert=anchor+'''\n# Exercise authenticated user-owned Inventory Saved View metadata CRUD/read-back.\ndocker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm \\
  api python -m app.inventory_saved_views_runtime_verify\n'''
if s.count(anchor)!=1: raise SystemExit('bootstrap anchor mismatch')
s=s.replace(anchor,insert,1)

anchor="  '/dashboard/api/password-resets/complete'; do\n"
insert="  '/dashboard/api/password-resets/complete' \\\n  '/dashboard/api/inventory-view/saved-views' \\\n  '/dashboard/api/inventory-view/saved-views/{view_id}'; do\n"
if s.count(anchor)!=1: raise SystemExit('openapi route anchor mismatch')
s=s.replace(anchor,insert,1)

anchor='''ANON_PROVIDERS_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "http://127.0.0.1:${API_PORT}/dashboard/api/providers")"\nif [[ "$ANON_PROVIDERS_STATUS" != "401" && "$ANON_PROVIDERS_STATUS" != "503" ]]; then\n  echo "error: anonymous Provider Registry returned HTTP ${ANON_PROVIDERS_STATUS}, expected 401 or fail-closed 503" >&2\n  exit 1\nfi\n'''
insert=anchor+'''\nANON_SAVED_VIEWS_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' "http://127.0.0.1:${API_PORT}/dashboard/api/inventory-view/saved-views")"\nif [[ "$ANON_SAVED_VIEWS_STATUS" != "401" && "$ANON_SAVED_VIEWS_STATUS" != "503" ]]; then\n  echo "error: anonymous Inventory Saved Views returned HTTP ${ANON_SAVED_VIEWS_STATUS}, expected 401 or fail-closed 503" >&2\n  exit 1\nfi\n'''
if s.count(anchor)!=1: raise SystemExit('anonymous guard anchor mismatch')
s=s.replace(anchor,insert,1)

p.write_text(s)
