"""Benchmark adapter of 'bnb' (port of kb_algo_bnb.m)."""
from __future__ import annotations

from .bnb import knapsack_bnb


def algo_bnb(v, w, C, acfg, seed):
    """algo_bnb(v, w, C, acfg, seed): acfg = cfg["bnb"], seed = cfg["seed"] + 1000 * k."""
    _, items, info = knapsack_bnb(v, w, C, acfg["max_nodes"])
    return {"label": "branch and bound (Dantzig bound, depth-first)", "exact": True,
            "proven_optimal": info["proven_optimal"], "items": items,
            "array_bytes": info["array_bytes"],
            "operations": info["nodes"], "operations_unit": "nodes",
            "details": {"nodes": info["nodes"], "node_limit": acfg["max_nodes"],
                        "node_limit_reached": not info["proven_optimal"]}}
