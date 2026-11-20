"""Benchmark adapter and JSON description of 'sa' (port of kp_algo_sa_output.m)."""
from __future__ import annotations

from .kp_algo_sa_loader import kp_algo_sa_loader
from .kp_algo_sa_main import kp_algo_sa_main

_LABEL = kp_algo_sa_loader()["label"]


def run(v, w, C, acfg, seed) -> dict:
    """Run kp_algo_sa_main, return the common result dict."""
    items, info = kp_algo_sa_main(v, w, C, acfg, seed)
    return {"label": _LABEL, "exact": False, "proven_optimal": False, "items": items,
            "working_memory_bytes": info["working_memory_bytes"],
            "operations": info["proposals"], "operations_unit": "move evaluations",
            "details": {"penalty": info["penalty"], "proposals": info["proposals"],
                        "accepted": info["accepted"], "t_start": info["t_start"],
                        "t_end": info["t_end"]}}


def entry(acfg, env=None) -> dict:
    """Entry of the JSON "algorithms" array."""
    L = kp_algo_sa_loader()
    return {"id": L["id"], "label": _LABEL, "description": L["description"],
            "short_label": L["short_label"], "exact": L["exact"],
            "reference": L["reference"], "config": acfg}
