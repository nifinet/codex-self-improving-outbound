#!/usr/bin/env python3
"""The gate.

Reads config/scoring.yaml and evals/fixtures.yaml, routes every fixture case,
and prints one number. Exits 0 only when accuracy is 1.00, so a shell script,
a git hook, or CI can block a change that did not help.

No proposed edit becomes a pull request unless this number goes up.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORING = ROOT / "config" / "scoring.yaml"
FIXTURES = ROOT / "evals" / "fixtures.yaml"

# pyyaml if it is installed, a small fallback parser if it is not. The offline
# demo has to run on a clean machine before anyone has done pip install.
try:
    import yaml

    def load_yaml(path):
        return yaml.safe_load(path.read_text())

except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _minimal_yaml import load_yaml  # noqa: F401


def load_scoring():
    """Flatten scoring.yaml into {signal: weight} plus the thresholds."""
    raw = load_yaml(SCORING)
    weights = {
        name: int(body["weight"]) for name, body in (raw.get("signals") or {}).items()
    }
    # Negative signals live in their own block so they read as disqualifiers,
    # not as just another weight. They are summed the same way.
    for name, value in (raw.get("negative_signals") or {}).items():
        weights[name] = int(value)
    thresholds = {k: int(v) for k, v in raw["thresholds"].items()}
    return weights, thresholds


def route(signals, weights, thresholds):
    """Sum the signals on an account and decide what happens to it."""
    total = sum(weights.get(signal, 0) for signal in signals)
    if total >= thresholds["human_review"]:
        return "human_review", total
    if total >= thresholds["draft"]:
        return "draft", total
    return "ignore", total


def main():
    weights, thresholds = load_scoring()
    cases = load_yaml(FIXTURES)["cases"]

    correct = 0
    for case in cases:
        predicted, total = route(case["signals"], weights, thresholds)
        expected = case["expected"]
        hit = predicted == expected
        correct += hit
        flag = "" if hit else "   <- MISS"
        print(
            f"{case['account']}: predicted={predicted} expected={expected} "
            f"(score {total}){flag}"
        )

    accuracy = correct / len(cases)
    print(f"score={accuracy:.2f}")
    return 0 if accuracy == 1.0 else 1


if __name__ == "__main__":
    sys.exit(main())
