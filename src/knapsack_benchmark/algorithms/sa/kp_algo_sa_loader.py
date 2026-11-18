"""Identity of 'sa' for discover_algorithms (port of kp_algo_sa_loader.m)."""
from __future__ import annotations


def kp_algo_sa_loader() -> dict:
    return {
        "id": "sa",                    # must equal the folder name
        "label": "Simulated Annealing",
        "description": "Random single-item flips accepted with probability exp(-dE/T) on the penalised energy -V + P*max(0, W-C)^2, with a geometric cooling and several restarts; returns the best feasible packing seen.",
        "short_label": "SA",           # algorithm chip in Knapview
        "exact": False,
        "reference": False,
        "available": lambda: True,
        "environment": lambda: {},     # nothing to add to environment.algorithms
    }
