You improve the outbound scoring system.

Read:
- AGENTS.md
- config/scoring.yaml
- memory/outcomes.jsonl
- evals/fixtures.yaml

Your job:
1. Find one scoring rule that should change.
2. The reason must cite memory/outcomes.jsonl.
3. Change only config/scoring.yaml.
4. Run python3 evals/score.py.
5. If the score improves, keep the change.
6. If the score stays flat or drops, revert your change and stop.

Output:
- the exact line changed
- the outcome rows that caused it
- before score
- after score
- whether the change should become a PR

Do not edit prompts.
Do not add new signals.
Do not touch delivery.
