"""Identity of 'greedy' for discover_algorithms (port of kp_algo_greedy_loader.m)."""
from __future__ import annotations


def kp_algo_greedy_loader() -> dict:
    return {
        "id": "greedy",                    # must equal the folder name
        "label": "Greedy by Value/Weight Ratio + Best Single Item",
        "description": "Takes the items in decreasing value/weight order while they fit, then returns the better of that packing and the most valuable single item; one pass of O(n log n), at least half of the optimum.",
        "short_label": "Greedy",           # algorithm chip in Knapview
        "exact": False,
        "reference": False,
        "available": lambda: True,
        "environment": lambda: {},     # nothing to add to environment.algorithms
    }
