"""Default parameters (same keys and values as benchmark_config.m).

Each algorithm has its own settings block ``cfg[<id>]``, whose defaults come from
``algorithms/<id>/config_<id>.py``; the registry ``ALGORITHMS`` is in
``algorithms/algorithm_loader.py``. The instance generator's block ``cfg["instances"]``
comes from ``instances/config_instances.py``.
"""
from __future__ import annotations

import copy

from .algorithms.algorithm_loader import ALGORITHMS, default_configs
from .instances.config_instances import config_instances


def _defaults() -> dict:
    cfg = {
        "seed": 2026,              # master seed: same seed -> same instances and results
        "instances": config_instances(),  # instance generator: instances/config_instances.py
        "algorithms": list(ALGORITHMS),   # benchmarked, in this order (dp = reference)
    }
    cfg.update(default_configs())  # settings blocks cfg["dp"], cfg["bnb"], ... (each has "repeats")
    cfg["timing"] = {
        "trace_memory": False,     # extra untimed run per algorithm under tracemalloc (slow)
    }
    return cfg


def benchmark_config(overrides: dict | None = None) -> dict:
    """Defaults, with OVERRIDES merged field by field (nested dicts are merged).

    Example: benchmark_config({"qubo_chz": {"tabu": {"restarts": 50}}})
    """
    cfg = _defaults()
    if overrides:
        _merge(cfg, overrides, "")
    return cfg


def _merge(base: dict, over: dict, prefix: str) -> None:
    for key, value in over.items():
        if key not in base:
            raise KeyError(f'Unknown option "{prefix}{key}"')
        if isinstance(base[key], dict) and isinstance(value, dict):
            _merge(base[key], value, f"{prefix}{key}.")
        else:
            base[key] = copy.deepcopy(value)
