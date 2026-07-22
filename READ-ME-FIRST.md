# Read Me First

Four commands. No key, no Codex, no risk.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 evals/score.py
python3 scripts/propose_improvement.py
```

Expected first run:

```text
score=0.75
changed config/scoring.yaml
implementation_page_visit: 4 -> 6
score=1.00
open PR for human review
```

That is the whole idea. The system found a rule that was wrong, proved the fix
against a test, and stopped to wait for a human.

Then install Codex and hand the same job to a model:

```bash
npm install -g @openai/codex
codex login
scripts/run_codex_step.sh improve_scoring
```

Codex runs on your normal ChatGPT plan. No OpenAI API key is required.

This repo never sends messages and never merges its own changes.

The managed version is [max](https://yourmax.ai).
