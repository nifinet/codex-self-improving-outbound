Changed:
- implementation_page_visit: 4 -> 6 in config/scoring.yaml.

Why:
- KiteOps (2026-07-02): reply, asked about implementation timeline.
- Harborline Ops (2026-07-04): meeting, wanted to walk through the rollout steps.
- Pinewood Legal (2026-07-07): reply, asked who owns the integration internally.
- That signal is 4 positive out of 5 touches (0.8).

Before:
- eval score 0.75

After:
- eval score 1.00

Files changed:
- config/scoring.yaml

Risk:
- One weight moved. Routing for accounts near the draft threshold changes.

Reviewer check:
- Does this match actual sales judgment, not just the fixture?
- Is the signal specific enough to deserve the weight?
- Merge only if you would defend this rule to the team.

Rejected first:
- competitor_comparison: 8 -> 9 left score at 0.75
- competitor_comparison: 8 -> 10 left score at 0.75
- competitor_comparison: 8 -> 11 left score at 0.75
- competitor_comparison: 8 -> 12 left score at 0.75
- implementation_page_visit: 4 -> 5 left score at 0.75
