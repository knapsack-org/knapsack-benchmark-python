"""Command line:  knapsack-benchmark [options]   or   python -m knapsack_benchmark [options]"""
from __future__ import annotations

import argparse
import json
import sys

from .benchmark import run_benchmark
from .algorithms.algorithm_loader import ALGORITHMS


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="knapsack-benchmark",
        description="Benchmark 0-1 knapsack algorithms (dp, bnb, ilp, qubo, qubo_chz) and "
                    "write output/run-dd-mm-yy-hh-mm.json.")
    p.add_argument("-n", "--num-instances", type=int, help="number of instances (default 100)")
    p.add_argument("--seed", type=int, help="master seed (default 2026)")
    p.add_argument("-a", "--algorithms",
                   help=f"comma-separated subset of {','.join(ALGORITHMS)} (default: all)")
    p.add_argument("-o", "--output-dir", help="output folder (default: <project>/output)")
    p.add_argument("--config", help="JSON file with option overrides (any benchmark_config field)")
    p.add_argument("--set", action="append", default=[], metavar="KEY=JSON",
                   help='override one option, dotted keys allowed, e.g. --set '
                        'qubo_chz.tabu.restarts=50 (repeatable)')
    p.add_argument("--trace-memory", action="store_true",
                   help="also measure the tracemalloc peak of each algorithm in an extra "
                        "untimed run (slow: about 6x longer)")
    p.add_argument("-q", "--quiet", action="store_true", help="no console output")
    args = p.parse_args(argv)

    overrides: dict = {}
    if args.config:
        with open(args.config, encoding="utf-8") as fh:
            overrides = json.load(fh)
    for item in args.set:
        key, _, raw = item.partition("=")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            value = raw
        node = overrides
        parts = key.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    if args.num_instances is not None:
        overrides.setdefault("instances", {})["count"] = args.num_instances
    if args.seed is not None:
        overrides["seed"] = args.seed
    if args.algorithms:
        overrides["algorithms"] = [a.strip() for a in args.algorithms.split(",") if a.strip()]
    if args.trace_memory:
        overrides.setdefault("timing", {})["trace_memory"] = True

    try:
        run_benchmark(overrides, args.output_dir, verbose=not args.quiet)
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
