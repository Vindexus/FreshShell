#!/usr/bin/env python3
#
# Tests for lib/duration.sh. Run with: python3 tests/duration-test.py

import subprocess
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "lib" / "duration.sh"


def parse_duration(spec):
    result = subprocess.run(
        ["bash", "-c", 'source "$1" && parse_duration "$2"', "_", str(LIB), spec],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip()


VALID = [
    ("1m", 60),
    ("90m", 5400),
    ("1h", 3600),
    ("2d", 172800),
    ("3d", 259200),
    ("1w", 604800),
    ("0h", 0),
    ("08d", 691200),  # leading zero isn't read as octal
]

INVALID = ["", "d", "2", "2x", "2D", "-1d", "1.5h", "2 d", " 2d", "2d ", "2dd", "1h30m"]


def main():
    failures = 0

    for spec, seconds in VALID:
        code, out = parse_duration(spec)
        if code != 0 or out != str(seconds):
            failures += 1
            print(f"FAIL: {spec!r} should be {seconds}s, got exit {code} output {out!r}")

    for spec in INVALID:
        code, out = parse_duration(spec)
        if code != 1 or out != "":
            failures += 1
            print(f"FAIL: {spec!r} should be rejected, got exit {code} output {out!r}")

    total = len(VALID) + len(INVALID)
    print(f"{total - failures}/{total} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
