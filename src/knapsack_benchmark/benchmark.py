"""Benchmark runner: Python port of run_benchmark.m.

Every algorithm found in ``algorithms/<id>/`` (see helpers/discover.py) is run and
measured on every generated instance; quality is compared with the optimum of the
reference algorithm; everything is written to ``<project>/output/run-dd-mm-yy-hh-mm.json``
with the same structure as the MATLAB/Octave version. There are no options: settings
are edited in the files listed in config.py.
"""
from __future__ import annotations

import platform
import time
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import scipy

from .config import benchmark_config
from .helpers.add_ratios import add_ratios
from .helpers.discover import discover_algorithms
from .helpers.measure import process_memory
from .helpers.printing import print_instance, print_summary
from .helpers.run_algorithm import run_algorithm
from .helpers.schema import validate
from .helpers.summary import summarize
from .helpers.write_json import write_json
from .instances.instances import generate_instances

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Version of the output JSON structure (same value as run_benchmark.m in the
# MATLAB/Octave project). Increase on any breaking change of the structure.
SCHEMA_VERSION = 3


def run_benchmark() -> dict:
    """Run the benchmark, write ``output/run-dd-mm-yy-hh-mm.json`` and return the result
    dict (with ``output_file``)."""
    cfg = benchmark_config()
    algos, skipped = discover_algorithms()
    for s in skipped:
        warnings.warn(f'Algorithm "{s["id"]}" skipped: {s["reason"]}.', stacklevel=2)
    ids = [a["id"] for a in algos]
    ref_algo = next(a for a in algos if a["reference"])
    ref = ref_algo["id"]

    ic = cfg["instances"]
    instances = generate_instances(ic["count"], cfg["seed"], ic["min_items"], ic["max_items"],
                                   ic["max_coefficient"], ic["capacity_ratio"])
    print(f"knapsack-benchmark-python | {', '.join(ids)} | reference {ref} | "
          f"{len(instances)} instances | Python {platform.python_version()}")

    runs = []
    t_total = time.perf_counter()
    for k, inst in enumerate(instances, start=1):
        v, w, C = inst.values, inst.weights, inst.capacity
        # reference first: its value is the optimum the others are compared with
        ref_result = run_algorithm(ref_algo, v, w, C, cfg, k)
        optimum = ref_result["value"]
        results = {}
        for a in algos:
            res = ref_result if a is ref_algo else run_algorithm(a, v, w, C, cfg, k)
            res["is_optimal"] = res["value"] == optimum
            res["gap_percent"] = 100 * (optimum - res["value"]) / optimum if optimum > 0 else 0.0
            results[a["id"]] = res
        add_ratios(results, ref)
        runs.append({"id": k, "family": inst.family, "n": int(v.size), "capacity": C,
                     "weights": w, "values": v, "optimum": optimum,
                     "optimal_items": ref_result["items"], "results": results})
        print_instance(runs[-1], ids)
    total_time = time.perf_counter() - t_total

    entries = []
    for a in algos:
        e = a["output"].entry(cfg[a["id"]], a["environment"])
        validate(e, a["output"].SCHEMA["entry"], f"algorithms.{a['id']}")
        entries.append(e)
    env_algos = {a["id"]: a["environment"] for a in algos if a["environment"]}

    environment = {
        "interpreter": "Python",
        "version": platform.python_version(),
        "computer": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "process_memory_available": process_memory() is not None,
    }
    if env_algos:
        environment["algorithms"] = env_algos

    now = datetime.now()
    result = {
        "project": "knapsack-benchmark-python",
        "schema_version": SCHEMA_VERSION,
        "algorithms": entries,
        "skipped_algorithms": skipped,
        "instance_config": {"seed": cfg["seed"], **ic},
        "reference_algorithm": ref,
        "description": (f"0-1 knapsack: {', '.join(e['label'] for e in entries)}, compared on "
                        f"quality (gap to the {ref} optimum) and execution cost "
                        "(time, CPU, memory, operations)"),
        "created": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "environment": environment,
        "parameters": cfg,
        "summary": summarize(runs, ids, total_time),
        "instances": runs,
    }

    out_file = PROJECT_ROOT / "output" / f"run-{now.strftime('%d-%m-%y-%H-%M')}.json"
    write_json(out_file, result)

    print_summary(result["summary"], ids, total_time, out_file)
    result["output_file"] = str(out_file)
    return result
