"""Command line:  knapsack-benchmark   or   python -m knapsack_benchmark   (no options)."""
from __future__ import annotations

import sys

from .benchmark import run_benchmark

USAGE = ("usage: knapsack-benchmark\n"
         "Runs every algorithm of algorithms/ on every instance and writes "
         "output/run-dd-mm-yy-hh-mm.json.\n"
         "There are no options: edit the settings files instead (see README).")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        print(USAGE, file=sys.stderr)
        return 0 if args in (["-h"], ["--help"]) else 2
    run_benchmark()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
