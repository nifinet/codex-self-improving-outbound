You improve one outbound play.

Read:
- AGENTS.md
- config/plays.yaml
- memory/outcomes.jsonl
- the prompt file for the chosen play

Pick one play with at least 10 outcomes.

Find:
- lines or structures that appear in positive outcomes
- lines or structures that appear in no_reply or bad_fit outcomes
- any phrase that should be banned

Make one small edit to that play's prompt.

Rules:
- Do not change scoring.
- Do not create a new play.
- Do not add a new channel.
- Cite outcome rows.
- Write the before and after instruction.

Then run the copy eval if present.
If no copy eval exists, open the PR as review_required.
