#!/usr/bin/env bash
# Fresh-clone smoke test: what a first-time setup on a new laptop runs into.
#
#   scripts/smoke_fresh_clone.sh                 # clone origin's main
#   scripts/smoke_fresh_clone.sh /path/to/repo   # clone a local checkout instead (its committed HEAD)
#   KEEP=1 scripts/smoke_fresh_clone.sh          # keep the temp folder to look around
#
# Steps: clone into a temp folder, new venv, pip install -e ".[claude]", factory init, factory doctor
# --offline, import + render one post per brand (offline writer and voice, dry run), launch-check.
# Needs python3.11+, ffmpeg and git. Posts nothing, writes nothing outside the temp folder.
set -euo pipefail

SRC="${1:-$(git -C "$(dirname "$0")/.." remote get-url origin 2>/dev/null || echo https://github.com/Dhruv123-123/cocosl)}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/factory-smoke.XXXXXX")"
LOG="$WORK/smoke.log"
cleanup() { if [ -z "${KEEP:-}" ]; then rm -rf "$WORK"; else echo "kept: $WORK"; fi; }
trap cleanup EXIT
step() { printf '\n== %s\n' "$*" | tee -a "$LOG"; }
fail() { echo "FAIL: $*" | tee -a "$LOG"; echo "log: $LOG"; KEEP=1; exit 1; }

step "clone $SRC"
git clone -q --depth 1 --branch main "$SRC" "$WORK/repo" 2>>"$LOG" || git clone -q "$SRC" "$WORK/repo" || fail "clone"
cd "$WORK/repo"

step "venv + install"
command -v ffmpeg >/dev/null || fail "ffmpeg is not installed (Mac: brew install ffmpeg, Linux: sudo apt install ffmpeg)"
python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
pip install -q --upgrade pip >>"$LOG" 2>&1
pip install -q -e ".[claude]" >>"$LOG" 2>&1 || fail "pip install"

# a first-time user has no keys: everything must still work offline and in dry run
export FACTORY_HOME="$WORK/repo" FACTORY_DRY_RUN=1 FACTORY_LLM=offline FACTORY_TTS=silent
unset ANTHROPIC_API_KEY OPENAI_API_KEY ELEVENLABS_API_KEY KOKORO_URL 2>/dev/null || true

step "factory init"
factory init 2>&1 | tee -a "$LOG" || fail "factory init"
[ -f .env ] || fail "init didn't write .env"

step "factory doctor --offline"
factory doctor --offline --no-voice 2>&1 | tee -a "$LOG" || echo "(doctor reported problems; expected on a fresh laptop without keys)"

step "import + render one post per brand"
brands=$(python - <<'PY'
from contentfactory.pipeline import Factory
print(" ".join(Factory.create().brands()))
PY
) || fail "loading brands"
[ -n "$brands" ] || fail "no brands found"
for b in $brands; do
  pack=$(ls launch/"$b"/content.json launch/"$b"/*.json 2>/dev/null | head -1 || true)
  if [ -z "$pack" ]; then echo "  $b: no pack in launch/$b, skipped" | tee -a "$LOG"; continue; fi
  factory import "$pack" --brand "$b" --limit 1 2>&1 | tee -a "$LOG" || fail "import/render for $b"
done
python - <<'PY' 2>&1 | tee -a "$LOG" || fail "render check"
from contentfactory.pipeline import Factory
f = Factory.create()
rows = f.db.query("SELECT id, brand, status, assets FROM posts ORDER BY id")
bad = [r for r in rows if not (r["assets"] or {}).get("video") and not (r["assets"] or {}).get("slides")]
for r in rows:
    print(f"  #{r['id']} {r['brand']}: {r['status']} · {', '.join(sorted((r['assets'] or {}).keys())) or 'no media'}")
if not rows or bad:
    raise SystemExit(f"{len(bad)} post(s) without media")
PY

step "factory launch-check"
set +e
factory launch-check 2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}
set -e
[ "$rc" -le 2 ] || fail "launch-check crashed (exit $rc)"

step "OK: a fresh clone installs, renders one post per brand and runs launch-check (exit $rc: 0 green, 2 red)"
