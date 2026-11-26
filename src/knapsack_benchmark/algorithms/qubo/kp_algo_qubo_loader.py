"""Identity of 'qubo' for discover_algorithms (port of kp_algo_qubo_loader.m)."""
from __future__ import annotations


def kp_algo_qubo_loader() -> dict:
    return {
        "id": "qubo",                     # must equal the folder name
        "label": "QUBO A + Tabu Search",
        "description": ("Variant A. Heuristic: the knapsack written as a QUBO (capacity as a squared penalty "
                        "with a binary-encoded slack), minimised by a multi-start tabu search, "
                        "then decoded and repaired if infeasible."),
        "short_label": "QUBO A",           # algorithm chip in Knapview
        "exact": False,
        "reference": False,
        "available": lambda: True,
        "environment": lambda: {},
    }
