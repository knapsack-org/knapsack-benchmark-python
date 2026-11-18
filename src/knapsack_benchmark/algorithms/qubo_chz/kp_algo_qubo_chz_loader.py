"""Identity of 'qubo_chz' for discover_algorithms (port of kp_algo_qubo_chz_loader.m)."""
from __future__ import annotations


def kp_algo_qubo_chz_loader() -> dict:
    return {
        "id": "qubo_chz",                     # must equal the folder name
        "label": "QUBO CHZ + Tabu Search",
        "description": ("Independent copy of QUBO + Tabu Search with its own modules and "
                        "settings, to be modified for experiments without touching qubo."),
        "short_label": "QUBO CHZ",           # algorithm chip in Knapview
        "exact": False,
        "reference": False,
        "available": lambda: True,
        "environment": lambda: {},
    }
