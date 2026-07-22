# Safety

The interesting property of this repo is what it refuses to do.

## What it cannot do

| Guarantee | How it is enforced |
|---|---|
| **Never sends a message** | There is no delivery code in this repo. Nothing to misconfigure, no key to leak. |
| **Never merges its own change** | `scripts/open_pr.sh` opens a pull request and stops. `AGENTS.md` forbids self-merge. |
| **Never ships an unproven change** | `scripts/propose_improvement.py` restores `config/scoring.yaml` byte for byte when the gate does not move. |
| **Never changes two things at once** | `AGENTS.md` says one concept per proposal. `MAX_DELTA` bounds how far one weight can move. |
| **Never touches real people** | No scraping, no enrichment, no contact data. Every sample account is invented. |

## The one thing you have to keep doing

Read the diff.

Every other guarantee here is mechanical and holds whether or not anyone is
paying attention. This one is a habit, and it is the only thing standing
between a system that improves and a system that drifts.

The failure mode is not dramatic. Nobody decides to stop reviewing. The weekly
PR just becomes familiar, then it becomes noise, then someone grants the bot
merge rights because review feels like friction. That minute of friction is the
product.

If the PRs are piling up unread, turn the cron off until the habit is back. An
unreviewed queue of automated changes is worse than no automation.

## Before you wire anything real

Prove the improvement loop on the sample data first. The repo ships failing its
own gate on purpose so you have something to watch it fix.

When you do connect real data:

- Replace `memory/outcomes.jsonl` with your own touches, written as they land.
- Rewrite `evals/fixtures.yaml` around your accounts, including the ugly ones.
- Keep delivery in a different repo, behind a human.

## Reporting a problem

If you find a path where this repo can send, merge, or ship an unproven change,
that is a bug and not a feature request. Open an issue.
