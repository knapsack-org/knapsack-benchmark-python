"""Identity of 'ga' for discover_algorithms (port of kp_algo_ga_loader.m)."""
from __future__ import annotations


def kp_algo_ga_loader() -> dict:
    return {
        "id": "ga",                    # must equal the folder name
        "label": "Genetic Algorithm (Greedy Repair)",
        "description": "Population of bit strings evolved by tournament selection, uniform crossover and bit-flip mutation; every child is repaired by dropping the lowest value/weight items and refilling by ratio, one elite is kept.",
        "short_label": "GA",           # algorithm chip in Knapview
        "exact": False,
        "reference": False,
        "available": lambda: True,
        "environment": lambda: {},     # nothing to add to environment.algorithms
    }
