#!/usr/bin/env bash
# Run one prompt file through Codex, inside this repo, with AGENTS.md in scope.
#
#   scripts/run_codex_step.sh improve_scoring
#   scripts/run_codex_step.sh improve_prompt
#   scripts/run_codex_step.sh pr_summary
#
# Uses your ChatGPT/Codex plan. No OpenAI API key required.
#
# Override the model if you want:
#   CODEX_MODEL=<model> scripts/run_codex_step.sh improve_scoring

set -euo pipefail

cd "$(dirname "$0")/.."

step="${1:-}"
# Unset by default so Codex picks its own current model. Pin it only if you
# want to, rather than having this script go stale when model names change.
model="${CODEX_MODEL:-}"

if [ -z "$step" ]; then
  echo "usage: scripts/run_codex_step.sh <improve_scoring|improve_prompt|pr_summary>" >&2
  exit 2
fi

prompt="prompts/${step}.md"

if [ ! -f "$prompt" ]; then
  echo "no such prompt: $prompt" >&2
  echo "available:" >&2
  ls prompts/*.md >&2
  exit 2
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "codex not found." >&2
  echo "  npm install -g @openai/codex && codex login" >&2
  echo "" >&2
  echo "To watch the loop work without Codex, run the offline improver:" >&2
  echo "  python3 scripts/propose_improvement.py" >&2
  exit 127
fi

# --sandbox workspace-write is required, not optional. improve_scoring has to
# edit config/scoring.yaml and run the eval. The default sandbox is read-only,
# which makes the step look like it worked while changing nothing.
#
# The prompt is passed as an argument rather than piped, so stdin stays free.
# AGENTS.md is picked up from the working directory.
if [ -n "$model" ]; then
  codex exec -m "$model" --sandbox workspace-write "$(cat "$prompt")"
else
  codex exec --sandbox workspace-write "$(cat "$prompt")"
fi
