"""Benchmark of 0-1 knapsack algorithms: Python version of knapsack-benchmark-matlab.

Algorithms: ``dp`` (dynamic programming, reference), ``bnb`` (branch and bound),
``ilp`` (integer linear programming, SciPy/HiGHS), ``qubo`` (QUBO + tabu search)
and ``qubo_chz`` (independent copy of ``qubo``).
"""
from .benchmark import run_benchmark
from .config import benchmark_config

__all__ = ["run_benchmark", "benchmark_config"]
__version__ = "0.1.0"
