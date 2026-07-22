#!/usr/bin/env python3
"""Pure-stdlib tests. No pytest needed.

    python3 -m tests.test_repo
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
sys.path.insert(0, str(ROOT / "scripts"))

import score  # noqa: E402

PASSED = []
FAILED = []


def check(name, condition, detail=""):
    if condition:
        PASSED.append(name)
        print(f"  ok    {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL  {name} {detail}")


def accuracy_at(implementation_weight):
    """Accuracy over the fixtures with one weight pinned.

    Pinned on purpose: these tests describe the routing logic, so they must give
    the same answer whether or not the improver has already run on this clone.
    """
    weights, thresholds = score.load_scoring()
    weights = dict(weights, implementation_page_visit=implementation_weight)
    cases = score.load_yaml(ROOT / "evals" / "fixtures.yaml")["cases"]
    results = {c["account"]: score.route(c["signals"], weights, thresholds)[0] for c in cases}
    correct = sum(results[c["account"]] == c["expected"] for c in cases)
    return correct / len(cases), results


def test_baseline_is_the_documented_miss():
    """At weight 4 the gate must fail on exactly the account the article names."""
    acc, results = accuracy_at(4)
    check("baseline accuracy is 0.75", acc == 0.75, f"got {acc}")
    check("KiteOps is the known miss", results["KiteOps"] == "ignore")


def test_negative_signals_cancel():
    weights, thresholds = score.load_scoring()
    route, total = score.route(["job_repost", "student_research"], weights, thresholds)
    check("bad-fit marker cancels the signal", route == "ignore", f"got {route} at {total}")


def test_the_documented_fix_passes():
    """implementation_page_visit 4 -> 6 must take the gate to 1.00."""
    acc, _ = accuracy_at(6)
    check("the documented fix reaches 1.00", acc == 1.0, f"got {acc}")


def test_outcomes_are_well_formed():
    required = {"date", "account", "signal", "play", "score", "outcome", "reason"}
    valid = {"reply", "meeting", "no_reply", "bad_fit", "bounced"}
    rows = [
        json.loads(line)
        for line in (ROOT / "memory" / "outcomes.jsonl").read_text().splitlines()
        if line.strip()
    ]
    check("outcomes file is not empty", len(rows) > 0)
    check("every row has every field", all(required <= set(r) for r in rows))
    check("every outcome is a known value", all(r["outcome"] in valid for r in rows))
    check("every reason is non-empty", all(r["reason"].strip() for r in rows))


def test_validator_rejects_bad_rows():
    import append_outcome

    base = [
        "--date", "2026-07-11", "--account", "KiteOps",
        "--signal", "implementation_page_visit", "--play", "implementation_angle",
        "--score", "6", "--outcome", "reply", "--reason", "asked about timeline",
    ]

    def errors_for(**overrides):
        argv = list(base)
        for flag, value in overrides.items():
            i = argv.index(f"--{flag}")
            argv[i + 1] = value
        return append_outcome.validate(append_outcome.parse_args(argv))

    check("a good row validates", errors_for() == [])
    check("empty reason is rejected", errors_for(reason="   ") != [])
    check("future date is rejected", errors_for(date="2099-01-01") != [])
    check("malformed date is rejected", errors_for(date="July 11") != [])


def test_improver_reverts_when_nothing_helps():
    """The revert path is the whole safety story. It has to be real."""
    import propose_improvement as improver

    original = improver.SCORING.read_text()
    # A value nothing else in the file uses, so the diff is unambiguous.
    text = improver.set_weight(original, "implementation_page_visit", 97)

    changed = [
        (a, b)
        for a, b in zip(original.splitlines(), text.splitlines())
        if a != b
    ]
    check("set_weight changes exactly one line", len(changed) == 1, f"changed {len(changed)}")
    check("set_weight changes the right line",
          bool(changed) and changed[0][1].strip() == "weight: 97", changed[:1])
    check("set_weight reads back the value it wrote",
          improver.current_weight(text, "implementation_page_visit") == 97)
    check("set_weight leaves the file otherwise intact",
          len(text.splitlines()) == len(original.splitlines()))
    check("config on disk is untouched by set_weight",
          improver.SCORING.read_text() == original)
    check("set_weight refuses an unknown signal",
          _raises(KeyError, improver.set_weight, original, "no_such_signal", 5))


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    except Exception:
        return False
    return False


def test_improver_end_to_end_dry_run():
    """--dry-run must propose the documented change and restore the file.

    Pins config/scoring.yaml back to its shipped before-state for the duration,
    so this passes on a clone where the improver has already been run.
    """
    import propose_improvement as improver

    on_disk = improver.SCORING.read_text()
    try:
        improver.SCORING.write_text(improver.set_weight(on_disk, "implementation_page_visit", 4))
        before = improver.SCORING.read_text()

        result = subprocess.run(
            [sys.executable, "scripts/propose_improvement.py", "--dry-run"],
            cwd=ROOT, text=True, capture_output=True,
        )
        after = improver.SCORING.read_text()

        check("dry run exits clean", result.returncode == 0, result.stderr[-300:])
        check("dry run restores config/scoring.yaml", before == after)
        check("dry run proposes implementation_page_visit",
              "implementation_page_visit: 4 -> 6" in result.stdout,
              result.stdout[-300:])
        check("dry run reports the score moving to 1.00",
              "score=0.75 -> score=1.00" in result.stdout)
        check("dry run cites outcome rows", "why:" in result.stdout)
    finally:
        improver.SCORING.write_text(on_disk)


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        print(f"\n{test.__name__}")
        test()

    print(f"\n{len(PASSED)} passed, {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
