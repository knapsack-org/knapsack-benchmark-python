"""Identity of 'qubo_b' for discover_algorithms (port of kp_algo_qubo_b_loader.m)."""
from __future__ import annotations


def kp_algo_qubo_b_loader() -> dict:
    return {
        "id": "qubo_b",                     # must equal the folder name
        "label": "QUBO B + Tabu Search",
        "description": ("Variant B (same code as variant A for now). Heuristic: the knapsack written as a QUBO (capacity as a squared penalty "
                        "with a binary-encoded slack), minimised by a multi-start tabu search, "
                        "then decoded and repaired if infeasible."),
        "short_label": "QUBO B",           # algorithm chip in Knapview
        "exact": False,
        "reference": False,
        "available": lambda: True,
        "environment": lambda: {},
    }
