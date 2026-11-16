"""Benchmark adapter of 'dp' (port of kb_algo_dp.m)."""
from __future__ import annotations

from .dp import knapsack_dp


def algo_dp(v, w, C, acfg, seed):
    """algo_dp(v, w, C, acfg, seed): acfg = cfg["dp"], seed = cfg["seed"] + 1000 * k."""
    _, items, info = knapsack_dp(v, w, C)
    return {"label": "dynamic programming 0-1", "exact": True, "proven_optimal": True,
            "items": items, "array_bytes": info["array_bytes"],
            "operations": info["operations"], "operations_unit": "table cells",
            "details": {"table_cells": info["operations"]}}
