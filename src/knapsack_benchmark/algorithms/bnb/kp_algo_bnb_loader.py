"""Identity of 'bnb' for discover_algorithms (port of kp_algo_bnb_loader.m)."""
from __future__ import annotations


def kp_algo_bnb_loader() -> dict:
    return {
        "id": "bnb",                     # must equal the folder name
        "label": "Branch and Bound (Dantzig Bound, Depth-First)",
        "description": ("Exact depth-first search over take/skip decisions, items sorted by "
                        "value/weight; a node is pruned when its Dantzig bound (LP relaxation) "
                        "cannot beat the best packing found, starting from the greedy packing."),
        "short_label": "BnB",           # algorithm chip in Knapview
        "exact": True,
        "reference": False,
        "available": lambda: True,
        "environment": lambda: {},
    }
