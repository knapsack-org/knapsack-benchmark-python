"""Benchmark adapter of 'ilp' (port of kb_algo_ilp.m)."""
from __future__ import annotations

from .ilp import knapsack_ilp


def algo_ilp(v, w, C, acfg, seed):
    """algo_ilp(v, w, C, acfg, seed): acfg = cfg["ilp"], seed = cfg["seed"] + 1000 * k."""
    _, items, info = knapsack_ilp(v, w, C)
    return {"label": f"integer linear programming ({info['solver']})", "exact": True,
            "proven_optimal": info["proven_optimal"], "items": items,
            "array_bytes": info["array_bytes"],
            "operations": info["nodes"], "operations_unit": "nodes",
            "details": {"solver": info["solver"], "status": info["status"],
                        "mip_gap": info["mip_gap"]}}
