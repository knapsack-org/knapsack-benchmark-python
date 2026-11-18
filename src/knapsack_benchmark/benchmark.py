"""Benchmark runner: Python port of run_benchmark.m.

For each generated instance, every algorithm in ``cfg["algorithms"]`` is run and
measured; quality is compared with the DP optimum; everything is written to
``<output_dir>/run-dd-mm-yy-hh-mm.json`` with the same structure as the
MATLAB/Octave version. Algorithm adapters live in ``algorithms/<id>/algo_<id>.py``,
the runner helpers in ``helpers/``.
"""
from __future__ import annotations

import platform
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import scipy

from .algorithms.algorithm_loader import check_algorithms
from .algorithms.dp.dp import knapsack_dp
from .config import benchmark_config
from .helpers.add_ratios_vs_dp import add_ratios_vs_dp
from .helpers.measure import process_memory
from .helpers.printing import print_instance, print_summary
from .helpers.run_algorithm import run_algorithm
from .helpers.summary import summarize
from .helpers.write_json import write_json
from .instances.instances import generate_instances

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Version of the output JSON structure (same value as run_benchmark.m in the
# MATLAB/Octave project). Increase on any breaking change of the structure.
SCHEMA_VERSION = 2


def run_benchmark(overrides: dict | None = None, output_dir: str | Path | None = None,
                  verbose: bool = True) -> dict:
    """Run the benchmark and write ``run-dd-mm-yy-hh-mm.json``.

    OVERRIDES: any field of ``benchmark_config`` (nested dicts merged), e.g.
    ``run_benchmark({"instances": {"count": 10}, "algorithms": ["dp", "bnb"]})``.
    OUTPUT_DIR defaults to ``<project>/output``. Returns the result dict
    (with ``output_file``).
    """
    cfg = benchmark_config(overrides)
    algos = check_algorithms(cfg["algorithms"])

    ic = cfg["instances"]
    instances = generate_instances(ic["count"], cfg["seed"], ic["min_items"], ic["max_items"],
                                   ic["max_coefficient"], ic["capacity_ratio"])
    log = print if verbose else (lambda *a, **k: None)
    log(f"knapsack-benchmark-python | {', '.join(algos)} | {len(instances)} instances | "
        f"Python {platform.python_version()}")

    runs = []
    t_total = time.perf_counter()
    for k, inst in enumerate(instances, start=1):
        v, w, C = inst.values, inst.weights, inst.capacity
        optimum, opt_items, _ = knapsack_dp(v, w, C)     # reference optimum (untimed)
        results = {a: run_algorithm(a, v, w, C, cfg, k, optimum) for a in algos}
        add_ratios_vs_dp(results)
        runs.append({"id": k, "family": inst.family, "n": int(v.size), "capacity": C,
                     "weights": w, "values": v, "optimum": optimum,
                     "optimal_items": opt_items, "results": results})
        print_instance(runs[-1], algos, log)
    total_time = time.perf_counter() - t_total

    summary = summarize(runs, algos, total_time)
    now = datetime.now()
    result = {
        "project": "knapsack-benchmark-python",
        "schema_version": SCHEMA_VERSION,
        "algorithms": [{"id": a, "label": summary["algorithms"][a]["algorithm"],
                        "exact": summary["algorithms"][a]["exact"], "config": cfg[a]}
                       for a in algos],
        "instance_config": {"seed": cfg["seed"], **ic},
        "reference_algorithm": "dp",
        "description": ("0-1 knapsack: dynamic programming, branch and bound, integer linear "
                        "programming, QUBO + tabu search and its independent copy QUBO CHZ, "
                        "compared on quality (gap to the DP optimum) and execution cost "
                        "(time, CPU, memory, operations)"),
        "created": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "environment": {
            "interpreter": "Python",
            "version": platform.python_version(),
            "computer": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "process_memory_available": process_memory() is not None,
            "ilp_solver": "scipy.optimize.milp (HiGHS)" if "ilp" in algos else "",
        },
        "parameters": cfg,
        "summary": summary,
        "instances": runs,
    }

    out_dir = Path(output_dir) if output_dir else PROJECT_ROOT / "output"
    out_file = out_dir / f"run-{now.strftime('%d-%m-%y-%H-%M')}.json"
    write_json(out_file, result)

    print_summary(result["summary"], algos, total_time, out_file, log)
    result["output_file"] = str(out_file)
    return result
