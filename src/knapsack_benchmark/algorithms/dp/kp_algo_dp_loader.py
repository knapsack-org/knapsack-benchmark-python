"""Identity of 'dp' for discover_algorithms (port of kp_algo_dp_loader.m).

'dp' is the reference: its result is the optimum the others are compared with.
"""
from __future__ import annotations


def kp_algo_dp_loader() -> dict:
    return {
        "id": "dp",                     # must equal the folder name
        "label": "Dynamic Programming 0-1",
        "description": ("Exact table of the best value for the first i items and every capacity "
                        "up to C, built row by row in O(n*C) time and memory; its optimum is the "
                        "reference of the benchmark."),
        "short_label": "DP",           # algorithm chip in Knapview
        "exact": True,
        "reference": True,
        "available": lambda: True,
        "environment": lambda: {},
    }
