"""Identity of 'ilp' for discover_algorithms (port of kp_algo_ilp_loader.m).

Available whenever scipy is installed (a dependency of the project).
"""
from __future__ import annotations

from .kp_algo_ilp_main import SOLVER


def kp_algo_ilp_loader() -> dict:
    return {
        "id": "ilp",                     # must equal the folder name
        "label": "Integer Linear Programming",
        "description": ("Exact integer linear program: maximise the packed value subject to the "
                        "capacity, with binary variables, solved by a MILP solver (glpk or "
                        "intlinprog in MATLAB, HiGHS in Python)."),
        "short_label": "ILP",           # algorithm chip in Knapview
        "exact": True,
        "reference": False,
        "available": lambda: True,
        "environment": lambda: {"solver": SOLVER},   # -> environment.algorithms.ilp
    }
