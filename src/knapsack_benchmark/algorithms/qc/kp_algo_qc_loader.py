"""Identity of 'qc' for discover_algorithms (port of kp_algo_qc_loader.m)."""
from __future__ import annotations


def kp_algo_qc_loader() -> dict:
    return {
        "id": "qc",                     # must equal the folder name
        "label": "QC (QUBO + Tabu Search)",
        "description": ("Heuristic (quantum computing experiments): today the QUBO variant B code, the "
                        "knapsack written as a QUBO minimised by a multi-start tabu search, then decoded "
                        "and repaired. Its modules also hold a simulated QAOA and a ratio greedy."),
        "short_label": "QC",           # algorithm chip in Knapview
        "exact": False,
        "reference": False,
        "available": lambda: True,
        "environment": lambda: {},
    }
