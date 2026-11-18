"""Identity of 'ising' for discover_algorithms (port of kp_algo_ising_loader.m)."""
from __future__ import annotations


def kp_algo_ising_loader() -> dict:
    return {
        "id": "ising",                    # must equal the folder name
        "label": "Ising Hamiltonian + Simulated Annealing",
        "description": "The penalty/slack QUBO rewritten as an Ising Hamiltonian on n + K spins and minimised by single-spin-flip annealing; the best spins are decoded and repaired if overweight.",
        "short_label": "Ising",           # algorithm chip in Knapview
        "exact": False,
        "reference": False,
        "available": lambda: True,
        "environment": lambda: {},     # nothing to add to environment.algorithms
    }
