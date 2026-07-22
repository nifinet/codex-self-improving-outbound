#!/usr/bin/env python3
"""The validator. Build this before you build the improver.

Every row in memory/outcomes.jsonl is evidence the improver will cite. A row
with an empty reason teaches it nothing, and a row invented on Friday from
memory teaches it fiction. This rejects both.

    python3 scripts/append_outcome.py \\
        --date 2026-07-11 \\
        --account "KiteOps" \\
        --signal implementation_page_visit \\
        --play implementation_angle \\
        --score 6 \\
        --outcome reply \\
        --reason "asked about implementation timeline"
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTCOMES = ROOT / "memory" / "outcomes.jsonl"

VALID_OUTCOMES = ["reply", "meeting", "no_reply", "bad_fit", "bounced"]


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="YYYY-MM-DD, not in the future")
    parser.add_argument("--account", required=True)
    parser.add_argument("--signal", required=True)
    parser.add_argument("--play", required=True)
    parser.add_argument("--score", required=True, type=int)
    parser.add_argument("--outcome", required=True, choices=VALID_OUTCOMES)
    parser.add_argument(
        "--reason",
        required=True,
        help="why it landed that way. 'no_reply' alone teaches nothing.",
    )
    return parser.parse_args(argv)


def validate(args):
    errors = []

    try:
        date = dt.date.fromisoformat(args.date)
        if date > dt.date.today():
            errors.append(f"date {args.date} is in the future")
    except ValueError:
        errors.append(f"date {args.date!r} is not YYYY-MM-DD")

    for field in ("account", "signal", "play"):
        if not getattr(args, field).strip():
            errors.append(f"{field} is empty")

    if not args.reason.strip():
        errors.append("reason is empty. The reason field is the whole point.")

    return errors


def main(argv=None):
    args = parse_args(argv)

    errors = validate(args)
    if errors:
        for error in errors:
            print(f"rejected: {error}", file=sys.stderr)
        return 1

    row = {
        "date": args.date,
        "account": args.account.strip(),
        "signal": args.signal.strip(),
        "play": args.play.strip(),
        "score": args.score,
        "outcome": args.outcome,
        "reason": args.reason.strip(),
    }

    line = json.dumps(row)
    with OUTCOMES.open("a") as handle:
        handle.write(line + "\n")

    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
