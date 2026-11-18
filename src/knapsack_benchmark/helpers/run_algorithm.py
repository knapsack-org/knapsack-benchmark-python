"""Run one algorithm with its timing repeats and build its result (port of kb_run_algorithm.m)."""
from __future__ import annotations

import numpy as np

from .measure import measure
from .schema import validate


def run_algorithm(algo: dict, v, w, C, cfg, k) -> dict:
    """ALGO is one entry of discover_algorithms(); its adapter ``output.run`` is timed
    cfg[id]["repeats"] times and its details are checked against ``output.SCHEMA``.
    ``is_optimal`` / ``gap_percent`` are filled by the caller once the reference
    optimum is known (placeholders False / None here)."""
    algo_id = algo["id"]
    acfg = cfg[algo_id]
    seed = cfg["seed"] + 1000 * k     # per-instance seed (used by the randomised algorithms)
    out, cost = measure(lambda: algo["output"].run(v, w, C, acfg, seed),
                        acfg["repeats"], cfg["timing"]["trace_memory"])
    validate(out["details"], algo["output"].SCHEMA["details"], f"{algo_id}.details")
    items = out["items"]
    idx = np.array(items, dtype=int) - 1
    value = float(v[idx].sum()) if items else 0.0
    weight = float(w[idx].sum()) if items else 0.0
    # working memory = bytes of the algorithm's own arrays (same idea as whos in MATLAB)
    cost = {**{k2: cost[k2] for k2 in ("repeats", "wall_time_s", "wall_time_min_s", "cpu_time_s")},
            "working_memory_bytes": out["working_memory_bytes"],
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
        "is_optimal": False,
        "gap_percent": None,
        "cost": cost,
        "details": out["details"],
    }
