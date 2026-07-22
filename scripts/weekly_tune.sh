#!/usr/bin/env bash
# The Monday tune-up.
#
# Outcomes accumulate all week. This runs once, proposes one change, proves it
# against the gate, and opens one pull request. It does not merge.
#
# Run the first two by hand and read every diff before you put this on cron.

set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p outputs

echo "==> before"
python3 evals/score.py || true

echo ""
echo "==> propose"
if command -v codex >/dev/null 2>&1; then
  scripts/run_codex_step.sh improve_scoring
else
  echo "codex not found, using the offline improver"
  python3 scripts/propose_improvement.py
fi

echo ""
echo "==> after"
if ! python3 evals/score.py; then
  echo ""
  echo "Gate did not pass. Not opening a PR." >&2
  exit 1
fi

echo ""
echo "==> pr summary"
if command -v codex >/dev/null 2>&1; then
  scripts/run_codex_step.sh pr_summary > outputs/pr-summary.md
else
  python3 scripts/create_pr.py --summary-only > outputs/pr-summary.md
fi
cat outputs/pr-summary.md

echo ""
echo "==> open pr"
scripts/open_pr.sh
