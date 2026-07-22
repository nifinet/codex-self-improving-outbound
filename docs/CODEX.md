# Running This With Codex

This repo is built for people who already pay for ChatGPT and want to run the
loop from that plan instead of wiring an API key on day one.

```bash
npm install -g @openai/codex
codex login
```

Then:

```bash
scripts/run_codex_step.sh improve_scoring
```

## The sandbox flag is not optional

`improve_scoring` has to edit `config/scoring.yaml` and run the eval. Codex
defaults to a read-only sandbox, which means without the right flag the step
runs, prints something reasonable, and changes nothing.

`scripts/run_codex_step.sh` therefore always passes:

```bash
codex exec -m "$model" --sandbox workspace-write "$(cat "$prompt")"
```

If you invoke Codex by hand, pass it yourself. A step that appears to succeed
while editing nothing is the most annoying failure mode in this repo, because
the gate will keep reporting the same score and it looks like the improver has
nothing to say.

## Why files instead of a database

Codex is good at reading local context, editing files, running commands, and
explaining what it changed. That means the loop needs no infrastructure:

- YAML for the rules a human argues with
- JSONL for memory that only ever appends
- shell scripts for repeatable runs
- an exit code for the gate

Everything is inspectable with `cat` and reviewable in a diff. That is the
property that makes the pull request readable.

## AGENTS.md

Codex reads `AGENTS.md` from the working directory before it acts. That file is
the law: what it may edit, what it must cite, and when it must stop. The
scripts `cd` to the repo root so the law is always in scope.

Keep it short. If it needs a table of contents it is too long to be enforced.

## Choosing a model

```bash
CODEX_MODEL=<model> scripts/run_codex_step.sh improve_scoring
```

Judgment work wants a strong model. The improver reads outcome reasons and
argues about weights, so this is not the place to economise.

## Recommended loop

1. Run `python3 scripts/propose_improvement.py` offline until the mechanics are boring.
2. Replace the sample outcomes with your own.
3. Rewrite `evals/fixtures.yaml` around accounts you wish had been routed differently.
4. Run `scripts/run_codex_step.sh improve_scoring` by hand, twice, and read both diffs.
5. Only then put `scripts/weekly_tune.sh` on a schedule.

Do not automate the merge. Ever.

## Docs

- [Codex authentication](https://developers.openai.com/codex/auth)
- [Codex non-interactive mode](https://developers.openai.com/codex/noninteractive)
- [Codex models](https://developers.openai.com/codex/models)
