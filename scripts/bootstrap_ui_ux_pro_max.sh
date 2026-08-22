#!/usr/bin/env bash
set -euo pipefail

UPSTREAM="https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git"
PIN="bc826e2267a36d98a2dcf5231e16c30ff546770f"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$ROOT/.agents/skills/ui-ux-pro-max"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

command -v git >/dev/null 2>&1 || {
  echo "error: git is required" >&2
  exit 1
}

git clone --quiet --filter=blob:none --no-checkout "$UPSTREAM" "$TMP/upstream"
git -C "$TMP/upstream" fetch --quiet --depth 1 origin "$PIN"
git -C "$TMP/upstream" checkout --quiet --detach "$PIN"

SOURCE="$TMP/upstream/.claude/skills/ui-ux-pro-max"
if [[ ! -f "$SOURCE/SKILL.md" || ! -f "$SOURCE/scripts/search.py" ]]; then
  echo "error: pinned upstream skill bundle is incomplete" >&2
  exit 1
fi

rm -rf "$TARGET"
mkdir -p "$(dirname "$TARGET")"
cp -R "$SOURCE" "$TARGET"

printf '%s\n' "$PIN" > "$TARGET/.upstream-commit"
printf '%s\n' "$UPSTREAM" > "$TARGET/.upstream-repository"

echo "UI/UX Pro Max installed locally at .agents/skills/ui-ux-pro-max"
echo "upstream_commit=$PIN"
