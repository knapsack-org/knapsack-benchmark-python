"""Registry and loading functions of the benchmarked algorithms (port of algorithm_loader.m).

Each id has a package ``algorithms/<id>/`` with ``config_<id>.py`` (default settings
block ``cfg[<id>]``) and ``algo_<id>.py`` (benchmark adapter). Add a new id to
``ALGORITHMS``.
"""
from __future__ import annotations

from importlib import import_module

ALGORITHMS = ("dp", "bnb", "ilp", "qubo", "qubo_chz")


def _function(name: str, kind: str):
    module = import_module(f".{name}.{kind}_{name}", __package__)
    return getattr(module, f"{kind}_{name}")


def default_configs() -> dict:
    """Default settings blocks, one key per id of ALGORITHMS."""
    return {name: _function(name, "config")() for name in ALGORITHMS}


def check_algorithms(requested) -> list[str]:
    """The requested ids as a list; ValueError on an unknown id."""
    algos = list(requested)
    for a in algos:
        if a not in ALGORITHMS:
            raise ValueError(f'Unknown algorithm "{a}"')
    return algos


def adapter(name: str):
    """The benchmark adapter ``algorithms/<name>/algo_<name>.py:algo_<name>``."""
    return _function(name, "algo")
