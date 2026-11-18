"""Identity of 'fptas' for discover_algorithms (port of kp_algo_fptas_loader.m)."""
from __future__ import annotations


def kp_algo_fptas_loader() -> dict:
    return {
        "id": "fptas",                    # must equal the folder name
        "label": "FPTAS (Profit Scaling)",
        "description": "Values are scaled down by epsilon*vmax/n and a minimum-weight table over the scaled profits is filled; the packing found is at least (1 - epsilon) times the optimum.",
        "short_label": "FPTAS",           # algorithm chip in Knapview
        "exact": False,
        "reference": False,
        "available": lambda: True,
        "environment": lambda: {},     # nothing to add to environment.algorithms
    }
