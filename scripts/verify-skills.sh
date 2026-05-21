#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Main Python validator (frontmatter, marketplace, references, links, tables,
# trigger overlap). See scripts/verify_skills.py.
python3 "$ROOT/scripts/verify_skills.py" --root "$ROOT"

# Rules files (outside skills/ so the Python ref check does not cover them).
test -f "$ROOT/rules/english.md" \
  && test -f "$ROOT/rules/chinese.md" \
  && test -f "$ROOT/rules/anti-patterns.md" \
  && echo "references: ok"

if ! grep -Fq "npx skills add tw93/Waza -a claude-code -g -y" "$ROOT/README.md"; then
    echo "README INSTALL COMMAND: Waza install must use the default direct-skill command" >&2
    exit 1
fi
echo "ok: README installs nested skills"

if ! grep -Fq "Chinese-only messages" "$ROOT/rules/english.md" \
   || ! grep -Fq "already-natural English, stay silent" "$ROOT/rules/english.md"; then
    echo "ENGLISH COACHING GUARD: rules/english.md must suppress Chinese-only and no-op correction output" >&2
    exit 1
fi
echo "ok: English Coaching guard"

# Attribution leak hardstop: no AI attribution strings in tracked markdown or scripts.
# These strings indicate AI-generated co-authorship leaked into skill content.
ATTRIBUTION_PATTERNS="Co-Authored-By: Claude\|Co-authored-by: Cursor\|noreply@anthropic.com\|cursoragent@cursor.com"
# Scan only non-documentation files: skip SKILL.md, rules/*.md, and this script
# (those legitimately document what patterns to detect rather than leaking them).
if ( cd "$ROOT" && grep -rn --include="*.sh" --include="*.json" "$ATTRIBUTION_PATTERNS" . 2>/dev/null ) \
   | grep -v "^Binary\|\.git/" \
   | grep -v "scripts/verify-skills.sh"; then
    echo "ATTRIBUTION LEAK: AI attribution string found in tracked script or config." >&2
    exit 1
fi
echo "ok: no attribution leak"
