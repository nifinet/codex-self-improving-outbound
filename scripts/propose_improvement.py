#!/usr/bin/env python3
"""The improver, offline.

This is the zero-key version of what prompts/improve_scoring.md asks Codex to
do. It reads outcomes, proposes one weight change, runs the gate, and keeps the
change only if the number went up. Everything else is reverted.

Run this first. It proves the file contracts and the revert path before you
hand the same job to a model.

    python3 scripts/propose_improvement.py
    python3 scripts/propose_improvement.py --dry-run   # never write, just report
"""

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORING = ROOT / "config" / "scoring.yaml"
OUTCOMES = ROOT / "memory" / "outcomes.jsonl"
OUTPUTS = ROOT / "outputs"

POSITIVE = {"reply", "meeting"}
# How far a single proposal is allowed to move one weight. The law says one
# concept at a time; this is what that means numerically.
MAX_DELTA = 4


def load_outcomes():
    rows = []
    for line in OUTCOMES.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def evidence(rows):
    """Positive rate per signal, plus the rows that back each one up."""
    tally = defaultdict(Counter)
    citations = defaultdict(list)
    for row in rows:
        tally[row["signal"]][row["outcome"]] += 1
        if row["outcome"] in POSITIVE:
            citations[row["signal"]].append(row)

    summary = {}
    for signal, counts in tally.items():
        total = sum(counts.values())
        wins = sum(counts[o] for o in POSITIVE)
        summary[signal] = {
            "touches": total,
            "positive": wins,
            "positive_rate": round(wins / total, 2),
        }
    return summary, citations


def run_gate():
    """Run the eval gate and return (accuracy, stdout)."""
    result = subprocess.run(
        [sys.executable, "evals/score.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    match = re.search(r"^score=([0-9.]+)$", result.stdout, re.MULTILINE)
    return (float(match.group(1)) if match else 0.0), result.stdout.strip()


def set_weight(text, signal, new_value):
    """Rewrite one `weight:` line under one signal. Leaves the rest untouched."""
    lines = text.splitlines()
    inside = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == f"{signal}:":
            inside = True
            continue
        if inside:
            if stripped.startswith("weight:"):
                indent = line[: len(line) - len(line.lstrip())]
                lines[i] = f"{indent}weight: {new_value}"
                return "\n".join(lines) + "\n"
            # Left this signal's block without finding a weight.
            if stripped and not line.startswith("    "):
                inside = False
    raise KeyError(f"no weight line found for signal {signal!r}")


def current_weight(text, signal):
    inside = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == f"{signal}:":
            inside = True
            continue
        if inside and stripped.startswith("weight:"):
            return int(stripped.split(":", 1)[1])
    raise KeyError(signal)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report the proposal without writing config/scoring.yaml",
    )
    args = parser.parse_args()

    rows = load_outcomes()
    summary, citations = evidence(rows)
    original = SCORING.read_text()

    before_score, before_out = run_gate()
    print(before_out)
    print()

    if before_score == 1.0:
        print("The gate already passes. Nothing to propose until new outcomes land.")
        print("Add outcomes with scripts/append_outcome.py, then run this again.")
        return 0

    # Try the signals with the strongest outcome evidence first, and for each
    # one try the smallest bump before a larger one. The first edit that moves
    # the gate wins. This is deliberately boring.
    candidates = sorted(
        summary, key=lambda s: (summary[s]["positive_rate"], summary[s]["touches"]), reverse=True
    )

    accepted = None
    rejected = []

    for signal in candidates:
        try:
            start = current_weight(original, signal)
        except KeyError:
            continue  # signal appears in outcomes but not in scoring.yaml
        for delta in range(1, MAX_DELTA + 1):
            SCORING.write_text(set_weight(original, signal, start + delta))
            trial_score, trial_out = run_gate()
            if trial_score > before_score:
                accepted = {
                    "signal": signal,
                    "before_weight": start,
                    "after_weight": start + delta,
                    "after_score": trial_score,
                    "after_out": trial_out,
                }
                break
            rejected.append(f"{signal}: {start} -> {start + delta} left score at {trial_score:.2f}")
        if accepted:
            break

    OUTPUTS.mkdir(exist_ok=True)

    if not accepted:
        SCORING.write_text(original)
        print("No single weight change improved the gate. Reverted, nothing proposed.")
        print("\nTried:")
        for line in rejected:
            print(f"  {line}")
        print("\nThis is the loop working. A change that cannot prove itself does not ship.")
        return 0

    if args.dry_run:
        SCORING.write_text(original)

    signal = accepted["signal"]
    cited = citations[signal][:3]

    print(accepted["after_out"])
    print()
    print(f"changed config/scoring.yaml")
    print(f"{signal}: {accepted['before_weight']} -> {accepted['after_weight']}")
    print(f"score={before_score:.2f} -> score={accepted['after_score']:.2f}")

    proposal = {
        "changed_file": "config/scoring.yaml",
        "change": f"{signal}: {accepted['before_weight']} -> {accepted['after_weight']}",
        "before_score": before_score,
        "after_score": accepted["after_score"],
        "evidence": summary[signal],
        "cited_outcomes": cited,
        "rejected_attempts": rejected,
        "kept": not args.dry_run,
        "next_action": "open PR for human review",
    }
    (OUTPUTS / "proposal.json").write_text(json.dumps(proposal, indent=2) + "\n")

    print()
    print("why:")
    for row in cited:
        print(f"  {row['date']}  {row['account']}: {row['outcome']} ({row['reason']})")
    print()
    if args.dry_run:
        print("dry run, config/scoring.yaml was left untouched")
    else:
        print("open PR for human review")
    print("wrote outputs/proposal.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
