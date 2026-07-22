#!/usr/bin/env bash
# Ship the proposal as a pull request. A human merges it, or does not.
#
# This is the control layer. Codex edits files and explains itself. The merge
# button stays with a person.

set -euo pipefail

cd "$(dirname "$0")/.."

branch="codex/weekly-tune-$(date +%Y-%m-%d)"

if [ ! -f outputs/pr-summary.md ]; then
  echo "outputs/pr-summary.md is missing. Run scripts/weekly_tune.sh." >&2
  exit 1
fi

if git diff --quiet -- config prompts; then
  echo "No changes to config or prompts. Nothing to open a PR for."
  exit 0
fi

git checkout -b "$branch"
git add config prompts evals memory
git commit -m "Codex weekly outbound tune"

body="$(cat outputs/pr-summary.md)"

python3 scripts/create_pr.py \
  "$branch" \
  "Codex weekly outbound tune" \
  "$body"
