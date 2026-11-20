"""Command line (ADR 0014):

    knapsack-benchmark [--request req.json] [--instances inst.json] [--out DIR]
    knapsack-benchmark --describe
(or ``python -m knapsack_benchmark ...``)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import describe, run_benchmark
from .helpers.write_json import to_json


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="knapsack-benchmark",
        description="Run the knapsack algorithms of algorithms/ on every instance and write raw.json "
                    "(and instances.json when the instances are generated). Absent request fields "
                    "come from the settings files (see README).")
    p.add_argument("--request", metavar="FILE",
                   help="run request JSON: seed, instances, algorithms, algorithm_config")
    p.add_argument("--instances", metavar="FILE",
                   help="instance set JSON (format knapsack-instances) used instead of the generator")
    p.add_argument("--out", metavar="DIR", help="output directory (default output/run-dd-mm-yy-hh-mm/)")
    p.add_argument("--describe", action="store_true",
                   help="print the algorithms with their default settings and JSON Schemas, then exit")
    args = p.parse_args(argv)
    if args.describe:
        print(to_json(describe()))
        return 0
    request = json.loads(Path(args.request).read_text(encoding="utf-8")) if args.request else None
    run_benchmark(request, args.instances, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
