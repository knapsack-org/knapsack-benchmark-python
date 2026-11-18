"""Parameters of the benchmark (port of benchmark_config.m).

``benchmark_config()`` returns the settings used by ``run_benchmark``:
    seed        master seed (below)
    instances   instance generator, from instances/config_instances.py
    algorithms  ids of every folder of algorithms/ (alphabetical)
    <id>        settings of algorithm <id>, from algorithms/<id>/kp_algo_<id>_config.py
    timing      Python-only measurement options (below)
There are no run-time overrides: to change a setting, edit the file that defines it.
"""
from __future__ import annotations

from .helpers.discover import algorithm_ids, contract_module
from .instances.config_instances import config_instances


def benchmark_config() -> dict:
    ids = algorithm_ids()
    cfg = {
        "seed": 2026,              # master seed: same seed -> same instances and results
        "instances": config_instances(),
        "algorithms": ids,
    }
    for algo_id in ids:
        cfg[algo_id] = getattr(contract_module(algo_id, "config"), f"kp_algo_{algo_id}_config")()
    cfg["timing"] = {
        "trace_memory": False,     # True: extra untimed run per algorithm under tracemalloc
                                   # (peak bytes in cost.traced_peak_memory_bytes; ~6x slower)
    }
    return cfg
