"""Benchmark adapter and JSON description of 'greedy' (port of kp_algo_greedy_output.m)."""
from __future__ import annotations

from .kp_algo_greedy_loader import kp_algo_greedy_loader
from .kp_algo_greedy_main import kp_algo_greedy_main

_LABEL = kp_algo_greedy_loader()["label"]


def run(v, w, C, acfg, seed) -> dict:
    """Run kp_algo_greedy_main, return the common result dict (no randomness: seed unused)."""
    items, info = kp_algo_greedy_main(v, w, C, acfg, seed)
    return {"label": _LABEL, "exact": False, "proven_optimal": False, "items": items,
            "working_memory_bytes": info["working_memory_bytes"],
            "operations": info["operations"], "operations_unit": "items scanned",
            "details": {"greedy_value": info["greedy_value"], "single_value": info["single_value"],
                        "chose_single": info["chose_single"]}}


def entry(acfg, env=None) -> dict:
    """Entry of the JSON "algorithms" array."""
    L = kp_algo_greedy_loader()
    return {"id": L["id"], "label": _LABEL, "description": L["description"],
            "short_label": L["short_label"], "exact": L["exact"],
            "reference": L["reference"], "config": acfg}
