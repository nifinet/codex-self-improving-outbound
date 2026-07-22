# Contributing

The most useful contributions to this repo are not features.

## What actually helps

**Harder fixtures.** `evals/fixtures.yaml` is the weakest part of any clone,
including this one. Four cases is enough to demonstrate the loop and not enough
to trust it. If you have an account shape that a naive scoring file routes
wrong, that is worth a PR.

**Failure modes I missed.** If you find a way for the improver to ship a change
that did not earn it, or a path where something could send or self-merge, open
an issue. That is a bug, not a feature request.

**Better improver heuristics.** `scripts/propose_improvement.py` tries signals
in order of positive rate and takes the first edit that moves the gate. That is
deliberately simple. If you have something smarter that is still explainable in
a PR body, show it.

**Prompt improvements.** `prompts/improve_scoring.md` and
`prompts/improve_prompt.md` are the actual product. If a wording change makes
Codex reason better or drift less, that is the highest-leverage diff in the
repo.

## What does not fit

- Delivery integrations. Sending stays outside this repo, on purpose.
- Anything that lets the loop merge its own work.
- Enrichment or scraping against real people.
- Making the sample data pass the gate on a fresh clone. It ships failing on
  purpose. That is the demo.

## Before you open a PR

```bash
python3 -m tests.test_repo
```

If you changed routing logic, add a case to `evals/fixtures.yaml` that would
have failed before your change.

Keep diffs small enough to review in one sitting. The repo argues that one
concept per pull request is what makes a self-improving system safe; that
applies to humans too.

## Style

Plain files over clever abstractions. Someone in sales should be able to open
`config/scoring.yaml` and argue with it without reading any Python.
