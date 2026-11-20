"""Benchmark adapter and JSON description of 'fptas' (port of kp_algo_fptas_output.m)."""
from __future__ import annotations

from .kp_algo_fptas_loader import kp_algo_fptas_loader
from .kp_algo_fptas_main import kp_algo_fptas_main

_LABEL = kp_algo_fptas_loader()["label"]


def run(v, w, C, acfg, seed) -> dict:
    """Run kp_algo_fptas_main, return the common result dict (no randomness: seed unused)."""
    items, info = kp_algo_fptas_main(v, w, C, acfg, seed)
    return {"label": _LABEL, "exact": False, "proven_optimal": False, "items": items,
            "working_memory_bytes": info["working_memory_bytes"],
            "operations": info["operations"], "operations_unit": "table cells",
            "details": {"epsilon": acfg["epsilon"], "scale": info["scale"],
                        "scaled_profit_total": info["scaled_total"],
                        "table_cells": info["operations"]}}


def entry(acfg, env=None) -> dict:
    """Entry of the JSON "algorithms" array."""
    L = kp_algo_fptas_loader()
    return {"id": L["id"], "label": _LABEL, "description": L["description"],
            "short_label": L["short_label"], "exact": L["exact"],
            "reference": L["reference"], "config": acfg}
