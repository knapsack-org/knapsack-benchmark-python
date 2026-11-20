"""Parameters of the benchmark (port of benchmark_config.m).

``benchmark_config(request)`` returns the settings used by ``run_benchmark``:
    seed        master seed (below)
    instances   instance generator, from instances/config_instances.py
    algorithms  ids of the algorithm folders that run (alphabetical): all, or the
                request's ``algorithms`` plus the reference
    <id>        settings of algorithm <id>, from algorithms/<id>/kp_algo_<id>_config.py
    timing      Python-only measurement options (below)
A run request (ADR 0014) overrides ``seed``, fields of ``instances`` and, per algorithm,
fields of ``<id>`` (``algorithm_config``); everything else comes from the settings files.
"""
from __future__ import annotations

from .helpers.discover import contract_module, selected_ids
from .instances.config_instances import config_instances


def merge_settings(base: dict, override: dict, where: str) -> dict:
    """BASE with the values of OVERRIDE (nested dicts merged); an unknown key is an error."""
    out = dict(base)
    for key, value in override.items():
        if key not in base:
            raise ValueError(f'Unknown setting "{where}.{key}".')
        both_dicts = isinstance(base[key], dict) and isinstance(value, dict)
        out[key] = merge_settings(base[key], value, f"{where}.{key}") if both_dicts else value
    return out


def benchmark_config(request: dict | None = None) -> dict:
    request = request or {}
    ids = selected_ids(request.get("algorithms"))
    overrides = request.get("algorithm_config", {})
    cfg = {
        "seed": request.get("seed", 2026),   # master seed: same seed -> same instances and results
        "instances": merge_settings(config_instances(), request.get("instances", {}), "instances"),
        "algorithms": ids,
    }
    for algo_id in ids:
        defaults = getattr(contract_module(algo_id, "config"), f"kp_algo_{algo_id}_config")()
        cfg[algo_id] = merge_settings(defaults, overrides.get(algo_id, {}), algo_id)
    cfg["timing"] = {
        "trace_memory": False,     # True: extra untimed run per algorithm under tracemalloc
                                   # (peak bytes in cost.traced_peak_memory_bytes; ~6x slower)
    }
    return cfg
