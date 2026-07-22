# Build Prompts

The repo ships these two files already written, so you can clone and run. They
are reproduced here as prompts because building them yourself is the fastest
way to understand what they do, and because you will want to rebuild them
against your own outcome schema eventually.

Paste each into Codex from the repo root.

---

## 1. The validator

Build this **before** you build the improver. Every row in
`memory/outcomes.jsonl` is evidence the improver will cite. A row with an empty
reason teaches it nothing, and a row invented on Friday from memory teaches it
fiction.

```text
Build scripts/append_outcome.py.

It accepts:
- date
- account
- signal
- play
- score
- outcome: reply | meeting | no_reply | bad_fit | bounced
- reason

It rejects:
- missing fields
- unknown outcomes
- empty reason
- dates in the future

Append valid rows to memory/outcomes.jsonl.
Print the appended row.
```

---

## 2. The gate

Before Codex edits anything, it needs a test it cannot explain away.

```text
Build evals/score.py.

Read config/scoring.yaml and evals/fixtures.yaml.

For each case:
1. Sum weights for every signal.
2. Add negative signal penalties.
3. Route the account:
   - score >= thresholds.human_review => human_review
   - score >= thresholds.draft => draft
   - otherwise => ignore
4. Compare route to expected.

Print each prediction.
Print final accuracy as score=0.00 to score=1.00.
Exit 0 only when accuracy is 1.00.
```

The exit code is the part that matters. It is what lets a shell script, a git
hook, or CI block a change that did not help.

---

## 3. The offline improver (optional)

`scripts/propose_improvement.py` is the zero-key version of what
`prompts/improve_scoring.md` asks Codex to do. It exists so you can watch the
loop work, and watch it revert, before you hand the job to a model.

```text
Build scripts/propose_improvement.py.

Read memory/outcomes.jsonl and rank signals by positive outcome rate
(reply and meeting count as positive), breaking ties by touch count.

Run evals/score.py and record the baseline accuracy.

Then, for each signal in rank order, and for each increment from +1 to +4:
- write the new weight into config/scoring.yaml
- re-run evals/score.py
- if accuracy improved, keep the change and stop
- otherwise record the attempt and continue

If nothing improved the gate, restore config/scoring.yaml exactly as it was
and report that nothing was proposed.

Write outputs/proposal.json with the change, the before and after scores,
the outcome rows that justify it, and every rejected attempt.

Support --dry-run, which reports the proposal but never writes the config.
```

Keep the rejected attempts. They are the most instructive part of the output:
they show a plausible change being refused because it did not move the number.

---

## What NOT to build

The article is deliberate about what stays outside the loop. Do not prompt
Codex to build:

- a delivery integration, or anything that sends
- a merge step, or anything that approves its own pull request
- an enrichment or scraping step against real people

If a prompt starts drifting toward any of those, the law in `AGENTS.md` is what
pulls it back. Read that file before you extend this repo.
