#!/usr/bin/env python3
"""Push the branch and open the pull request.

Uses the `gh` CLI if it is installed, and falls back to printing the exact
commands so nothing here is a black box. Never merges.

    python3 scripts/create_pr.py <branch> <title> <body>
    python3 scripts/create_pr.py --summary-only    # write a PR body from outputs/proposal.json
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "outputs" / "proposal.json"


def summary_from_proposal():
    """Build the PR body from the last offline proposal."""
    if not PROPOSAL.exists():
        print("outputs/proposal.json is missing. Run scripts/propose_improvement.py.", file=sys.stderr)
        return 1

    p = json.loads(PROPOSAL.read_text())
    evidence = p.get("evidence", {})

    lines = [
        "Changed:",
        f"- {p['change']} in {p['changed_file']}.",
        "",
        "Why:",
    ]
    for row in p.get("cited_outcomes", []):
        lines.append(f"- {row['account']} ({row['date']}): {row['outcome']}, {row['reason']}.")
    if evidence:
        lines.append(
            f"- That signal is {evidence['positive']} positive out of "
            f"{evidence['touches']} touches ({evidence['positive_rate']})."
        )

    lines += [
        "",
        "Before:",
        f"- eval score {p['before_score']:.2f}",
        "",
        "After:",
        f"- eval score {p['after_score']:.2f}",
        "",
        "Files changed:",
        f"- {p['changed_file']}",
        "",
        "Risk:",
        "- One weight moved. Routing for accounts near the draft threshold changes.",
        "",
        "Reviewer check:",
        "- Does this match actual sales judgment, not just the fixture?",
        "- Is the signal specific enough to deserve the weight?",
        "- Merge only if you would defend this rule to the team.",
    ]

    if p.get("rejected_attempts"):
        lines += ["", "Rejected first:"]
        for attempt in p["rejected_attempts"][:5]:
            lines.append(f"- {attempt}")

    print("\n".join(lines))
    return 0


def open_pr(branch, title, body):
    if not shutil.which("gh"):
        print("gh CLI not found. Push and open the PR with:", file=sys.stderr)
        print(f"  git push -u origin {branch}", file=sys.stderr)
        print(f"  gh pr create --title {title!r} --body-file outputs/pr-summary.md", file=sys.stderr)
        return 1

    subprocess.run(["git", "push", "-u", "origin", branch], cwd=ROOT, check=True)
    result = subprocess.run(
        ["gh", "pr", "create", "--title", title, "--body", body],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    print(result.stdout.strip() or result.stderr.strip())
    if result.returncode == 0:
        print("\nPull request opened. It is not merged. That part is yours.")
    return result.returncode


def main(argv):
    if argv and argv[0] == "--summary-only":
        return summary_from_proposal()
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    return open_pr(*argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
