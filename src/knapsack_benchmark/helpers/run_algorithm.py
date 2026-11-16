"""Run one algorithm with its timing repeats and build its result (port of kb_run_algorithm.m)."""
from __future__ import annotations

from importlib import import_module

import numpy as np

from .measure import measure


def adapter(name: str):
    """The benchmark adapter algorithms/<name>/algo_<name>.py:algo_<name>."""
    module = import_module(f"..algorithms.{name}.algo_{name}", __package__)
    return getattr(module, f"algo_{name}")


def run_algorithm(name, v, w, C, cfg, k, optimum) -> dict:
    acfg = cfg[name]
    algo = adapter(name)
    seed = cfg["seed"] + 1000 * k     # per-instance seed (used by the randomised algorithms)
    out, cost = measure(lambda: algo(v, w, C, acfg, seed),
                        acfg["repeats"], cfg["timing"]["trace_memory"])
    items = out["items"]
    idx = np.array(items, dtype=int) - 1
    value = float(v[idx].sum()) if items else 0.0
    weight = float(w[idx].sum()) if items else 0.0
    # working memory = bytes of the algorithm's own arrays (same idea as whos in MATLAB)
    cost = {**{k2: cost[k2] for k2 in ("repeats", "wall_time_s", "wall_time_min_s", "cpu_time_s")},
            "working_memory_bytes": out["array_bytes"],
            **{k2: cost[k2] for k2 in cost if k2.startswith(("traced", "process"))}}
    cost["operations"] = out["operations"]
    cost["operations_unit"] = out["operations_unit"]
    return {
        "algorithm": out["label"],
        "exact": out["exact"],
        "proven_optimal": out["proven_optimal"],
        "value": value,
        "items": items,
        "weight": weight,
        "feasible": weight <= C,
        "is_optimal": value == optimum,
        "gap_percent": 100 * (optimum - value) / optimum if optimum > 0 else 0.0,
        "cost": cost,
        "details": out["details"],
    }
