# Troubleshooting

| Symptom | What is happening | Fix |
|---|---|---|
| `score=0.75` on a fresh clone | Correct. The repo ships failing its own gate on purpose. | Run `python3 scripts/propose_improvement.py` and watch it fix itself. |
| `No single weight change improved the gate` | Also correct, once the gate is at 1.00. There is nothing left to prove against the current fixtures. | Add outcomes, then add a fixture case that the current rules get wrong. |
| Codex runs, says it changed things, but `git diff` is empty | The sandbox was read-only. This is the most common Codex failure here. | Pass `--sandbox workspace-write`. `scripts/run_codex_step.sh` already does. |
| `codex not found` | Codex CLI is not installed or not on PATH. | `npm install -g @openai/codex && codex login`, or use the offline improver. |
| `ModuleNotFoundError: yaml` | Harmless. `evals/_minimal_yaml.py` takes over. | `pip install -r requirements.txt` to silence it. |
| `open_pr.sh` says nothing to open | The improver reverted its change because the gate did not move. | Working as intended. Nothing unproven ships. |
| The improver keeps proposing the same signal | Your fixtures only test one kind of miss. | Add cases that fail for different reasons: weak intent, stale signal, bad fit. |
| The improver proposes nothing useful with real data | Usually the `reason` fields are empty or generic. | `no_reply` teaches nothing. `content-only intent` teaches something. |
| Eval hits 1.00 and stays there forever | The fixture set is too easy. | Every time the system misroutes a real account, add it as a case. The gate should get harder over time. |
| PRs pile up unreviewed | The habit broke. | Turn the cron off until it is back. See [SAFETY.md](SAFETY.md). |
| `gh` not found when opening a PR | `scripts/create_pr.py` falls back to printing the commands. | Install `gh`, or run the printed `git push` and `gh pr create` by hand. |

## Checking the plumbing

```bash
python3 -m tests.test_repo
```

23 checks, standard library only. They cover the baseline miss, the
negative-signal cancel, the outcome validator, and the revert path. They pass
whether or not the improver has already run on your clone.

If those pass and something still looks wrong, the problem is in your data or
your fixtures rather than in the machinery.
