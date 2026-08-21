#!/usr/bin/env python3
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents" / "skills" / "medicine-store-assistant"
SKILL_FILE = SKILL_DIR / "SKILL.md"
PLUGIN_FILE = ROOT / ".codex-plugin" / "plugin.json"
MARKETPLACE_FILE = ROOT / ".agents" / "plugins" / "marketplace.json"

REQUIRED = [
    ROOT / "VERSION",
    ROOT / "NORMAL_CHAT_BOOTSTRAP.md",
    SKILL_FILE,
    SKILL_DIR / "references" / "system-contract.md",
    SKILL_DIR / "references" / "runtime-configuration.md",
    SKILL_DIR / "references" / "cms-batch-intake.md",
    SKILL_DIR / "references" / "daily-usage.md",
    SKILL_DIR / "references" / "cms-price-and-matching.md",
    SKILL_DIR / "references" / "visual-marking.md",
    PLUGIN_FILE,
    MARKETPLACE_FILE,
]


def fail(message: str) -> None:
    raise SystemExit(f"validation error: {message}")


for path in REQUIRED:
    if not path.is_file():
        fail(f"missing required file: {path.relative_to(ROOT)}")

skill_text = SKILL_FILE.read_text(encoding="utf-8")
frontmatter = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)
if not frontmatter:
    fail("SKILL.md lacks YAML frontmatter")
if not re.search(r"^name:\s*medicine-store-assistant\s*$", frontmatter.group(1), re.MULTILINE):
    fail("SKILL.md has the wrong name")
if not re.search(r"^description:\s*\S", frontmatter.group(1), re.MULTILINE):
    fail("SKILL.md lacks a description")

for relative in re.findall(r"\]\((references/[^)]+\.md)\)", skill_text):
    if not (SKILL_DIR / relative).is_file():
        fail(f"broken SKILL.md reference: {relative}")

version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    fail("VERSION must use semantic versioning")

plugin = json.loads(PLUGIN_FILE.read_text(encoding="utf-8"))
if plugin.get("name") != "medicine-store-assistant":
    fail("plugin name does not match the skill")
if plugin.get("version") != version:
    fail("plugin version does not match VERSION")
if plugin.get("skills") != "./.agents/skills/":
    fail("plugin skills path is not canonical")

marketplace = json.loads(MARKETPLACE_FILE.read_text(encoding="utf-8"))
plugins = marketplace.get("plugins", [])
if len(plugins) != 1 or plugins[0].get("name") != "medicine-store-assistant":
    fail("marketplace must expose exactly the MSA plugin")

forbidden_sheet_id = "1kATvZ3tfhwijd0wKx9m15QHN" + "RIdmFnGdvbesVktpjsE"

for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if forbidden_sheet_id in text:
        fail(f"live spreadsheet ID leaked in {path.relative_to(ROOT)}")
    if re.search(r"-----BEGIN (?:RSA )?PRIVATE KEY-----", text):
        fail(f"private key material found in {path.relative_to(ROOT)}")

print(f"Validated medicine-store-assistant {version}")
