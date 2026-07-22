# Sample Run

What a first clone actually prints.

## 1. The gate, before

```bash
python3 evals/score.py
```

```text
Northwind Finance: predicted=human_review expected=human_review (score 12)
Bluepeak Studio: predicted=ignore expected=ignore (score 1)
KiteOps: predicted=ignore expected=draft (score 4)   <- MISS
Atlas Recruiting: predicted=ignore expected=ignore (score -3)
score=0.75
```

Exit code 1. One case fails: an account with implementation intent is being
routed to `ignore`.

## 2. The improver

```bash
python3 scripts/propose_improvement.py
```

```text
changed config/scoring.yaml
implementation_page_visit: 4 -> 6
score=0.75 -> score=1.00

why:
  2026-07-02  KiteOps: reply (asked about implementation timeline)
  2026-07-04  Harborline Ops: meeting (wanted to walk through the rollout steps)
  2026-07-07  Pinewood Legal: reply (asked who owns the integration internally)

open PR for human review
wrote outputs/proposal.json
```

## 3. What it tried first

From `outputs/proposal.json`:

```json
"rejected_attempts": [
  "competitor_comparison: 8 -> 9 left score at 0.75",
  "competitor_comparison: 8 -> 10 left score at 0.75",
  "competitor_comparison: 8 -> 11 left score at 0.75",
  "competitor_comparison: 8 -> 12 left score at 0.75",
  "implementation_page_visit: 4 -> 5 left score at 0.75"
]
```

`competitor_comparison` is the best-looking signal in the outcome log. Six
touches, every one a reply or a meeting. The improver went there first, exactly
like a person would.

It was wrong. Raising a weight on accounts the system was already routing
correctly does nothing. The gate said so five times before one edit earned a
pull request.

The useful lesson is not that the improver is clever. It is that:

- a plausible change can still be a useless change
- the gate is what tells the difference
- a rejected proposal leaves no trace on disk
- the one that survives arrives with its evidence attached

## 4. The pull request

See [weekly-pr.md](weekly-pr.md) for the generated body.
