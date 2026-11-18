"""Benchmark of 0-1 knapsack algorithms: Python version of knapsack-benchmark-matlab.

Algorithms: one self-contained package per algorithm in ``algorithms/<id>/``, found by
``helpers.discover.discover_algorithms`` (``dp`` is the reference).
"""
from .benchmark import run_benchmark
from .config import benchmark_config

__all__ = ["run_benchmark", "benchmark_config"]
__version__ = "0.1.0"
