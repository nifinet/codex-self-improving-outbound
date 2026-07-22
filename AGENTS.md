# Self-Improving Outbound Rules

You improve an outbound system from outcomes.

Hard rules:
- Never send messages.
- Never scrape or enrich real people.
- Never self-merge.
- Edit only files in this repo.
- Change one concept at a time.
- Cite outcomes from memory/outcomes.jsonl for every proposed change.
- Improve evals/score.py before a change can become a PR.
- If the eval does not improve, revert your edit and stop.

Allowed edits:
- config/scoring.yaml
- config/plays.yaml
- prompts/*.md

Required output:
- changed files
- reason for each change
- before score
- after score
- pull request summary
