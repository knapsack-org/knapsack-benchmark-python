"""Benchmark runner: Python port of run_benchmark.m (ADR 0014).

The algorithms of ``algorithms/<id>/`` (see helpers/discover.py), all or those of a run
request plus the reference, are run and measured on every instance (generated here, or read
from an instance set file). The raw results go to ``raw.json`` (format ``knapsack-raw`` v1):
Node's ``knapsack-output`` (knapsack-server) computes optimum, gaps, ratios and the summary
and writes the run file. A progress line ``@@progress {...}`` is printed before and after
each algorithm on each instance.
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
from .helpers.discover import discover_algorithms, output_schema
from .helpers.measure import process_memory
from .helpers.printing import print_instance, print_progress
from .helpers.run_algorithm import run_algorithm
from .helpers.write_json import write_json
from .instances.instances import generate_instances, instance_set, read_instances

PROJECT = "knapsack-benchmark-python"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _environment(algos: list[dict]) -> dict:
    environment = {
        "interpreter": "Python",
        "version": platform.python_version(),
        "computer": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "process_memory_available": process_memory() is not None,
    }
    env_algos = {a["id"]: a["environment"] for a in algos if a["environment"]}
    if env_algos:
        environment["algorithms"] = env_algos
    return environment


def _catalog(algos: list[dict], cfg: dict) -> dict:
    """``algorithms`` entries and ``algorithm_schemas`` (kp_algo_<id>_output.schema.json)."""
    return {"algorithms": [a["output"].entry(cfg[a["id"]], a["environment"]) for a in algos],
            "algorithm_schemas": {a["id"]: output_schema(a["id"]) for a in algos}}


def describe() -> dict:
    """What ``--describe`` prints: every available algorithm with its default settings."""
    algos, _ = discover_algorithms()
    return {"project": PROJECT, "environment": _environment(algos), **_catalog(algos, benchmark_config())}


def run_benchmark(request: dict | None = None, instances_file=None, out_dir=None) -> dict:
    """Run the benchmark; write ``raw.json`` (and ``instances.json`` when the instances are
    generated here) to OUT_DIR, default ``output/run-dd-mm-yy-hh-mm/``.

    REQUEST: run request dict (seed, instances, algorithms, algorithm_config; absent fields
    come from the settings files). INSTANCES_FILE: instance set file used instead of the
    generator. Returns the raw dict plus ``output_dir``."""
    request = request or {}
    algos, skipped = discover_algorithms(request.get("algorithms"))
    for s in skipped:
        warnings.warn(f'Algorithm "{s["id"]}" skipped: {s["reason"]}.', stacklevel=2)
    ids = [a["id"] for a in algos]
    ref_algo = next(a for a in algos if a["reference"])
    ref = ref_algo["id"]

    if instances_file:
        instances, instance_config = read_instances(instances_file)
        cfg = benchmark_config({"seed": instance_config["seed"], **request})
        cfg["instances"] = {k: x for k, x in instance_config.items() if k != "seed"}
    else:
        cfg = benchmark_config(request)
        ic = cfg["instances"]
        instances = generate_instances(ic["count"], cfg["seed"], ic["min_items"], ic["max_items"],
                                       ic["max_coefficient"], ic["capacity_ratio"], ic["correlation"])
        instance_config = {"seed": cfg["seed"], **ic}
    print(f"{PROJECT} | {', '.join(ids)} | reference {ref} | "
          f"{len(instances)} instances | Python {platform.python_version()}")

    runs = []
    t_total = time.perf_counter()
    for inst in instances:
        results = {}
        for a in [ref_algo] + [a for a in algos if a is not ref_algo]:   # reference first, as before
            print_progress(inst.id, a["id"], "start")
            # per-instance seed from the global instance id, so a shard gives the same results (P7)
            results[a["id"]] = run_algorithm(a, inst.values, inst.weights, inst.capacity, cfg, inst.id)
            print_progress(inst.id, a["id"], "done")
        runs.append({"id": inst.id, "results": {i: results[i] for i in ids}})
        print_instance(inst, runs[-1]["results"], ids, ref)
    total_time = time.perf_counter() - t_total

    now = datetime.now()
    raw = {
        "format": "knapsack-raw",
        "format_version": 1,
        "project": PROJECT,
        "created": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "environment": _environment(algos),
        **_catalog(algos, cfg),
        "skipped_algorithms": skipped,
        "reference_algorithm": ref,
        "parameters": cfg,
        "instance_config": instance_config,
        "instances": runs,
        "timing": {"total_time_seconds": total_time},
    }
    out = Path(out_dir) if out_dir else PROJECT_ROOT / "output" / f"run-{now.strftime('%d-%m-%y-%H-%M')}"
    write_json(out / "raw.json", raw)
    if not instances_file:
        write_json(out / "instances.json", instance_set(instances, instance_config))
    print(f"Total {total_time:.1f} s\nOutput: {out}")
    raw["output_dir"] = str(out)
    return raw
