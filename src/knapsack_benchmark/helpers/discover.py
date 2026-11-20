"""Find the benchmarked algorithms by scanning ``algorithms/`` (port of kb_discover_algorithms.m).

Every sub-package ``algorithms/<id>/`` (names starting with ``.`` or ``_`` are
ignored) must hold ``kp_algo_<id>_loader.py``, ``_main.py``, ``_config.py`` and
``_output.py`` + ``_output.schema.json`` (see documentation/implementation/adding-an-algorithm.md).
"""
from __future__ import annotations

import json
import re
from importlib import import_module
from pathlib import Path

ALGORITHMS_DIR = Path(__file__).resolve().parents[1] / "algorithms"
_PACKAGE = __package__.rsplit(".", 1)[0] + ".algorithms"   # knapsack_benchmark.algorithms
PARTS = ("loader.py", "main.py", "config.py", "output.py", "output.schema.json")


class DiscoveryError(ValueError):
    """An algorithm folder breaks the folder contract."""


def algorithm_ids() -> list[str]:
    """Ids of every algorithm folder, alphabetical (available or not)."""
    return sorted(p.name for p in ALGORITHMS_DIR.iterdir()
                  if p.is_dir() and not p.name.startswith((".", "_")))


def selected_ids(only: list[str] | None = None) -> list[str]:
    """Ids of every algorithm folder (alphabetical), or only those of ONLY plus the reference."""
    ids = algorithm_ids()
    if only is None:
        return ids
    unknown = sorted(set(only) - set(ids))
    if unknown:
        raise DiscoveryError(f"Unknown algorithm(s): {', '.join(unknown)}.")
    return [i for i in ids
            if i in only or getattr(contract_module(i, "loader"), f"kp_algo_{i}_loader")()["reference"]]


def output_schema(algo_id: str) -> dict:
    """``algorithms/<id>/kp_algo_<id>_output.schema.json``: JSON Schemas of its entry, config, details."""
    path = ALGORITHMS_DIR / algo_id / f"kp_algo_{algo_id}_output.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def contract_module(algo_id: str, part: str):
    """The module ``algorithms/<id>/kp_algo_<id>_<part>.py``."""
    return import_module(f"{_PACKAGE}.{algo_id}.kp_algo_{algo_id}_{part}")


def discover_algorithms(only: list[str] | None = None) -> tuple[list[dict], list[dict]]:
    """Return (algos, skipped), both in alphabetical order of the ids: every algorithm, or
    those of ONLY plus the reference.

    algos: one dict per algorithm that can run here, keys id, label, short_label,
    exact, reference, environment (dict) and output (the kp_algo_<id>_output module).
    skipped: [{"id", "reason"}] for algorithms whose loader says they are not available.
    Raises DiscoveryError on a bad folder name, a missing contract file, a loader id
    that differs from the folder name, or not exactly one available exact reference.
    """
    algos, skipped = [], []
    for algo_id in selected_ids(only):
        if not re.fullmatch(r"[a-z][a-z0-9_]*", algo_id):
            raise DiscoveryError(f'Algorithm folder "{algo_id}": name must match [a-z][a-z0-9_]*.')
        for part in PARTS:
            name = f"kp_algo_{algo_id}_{part}"
            if not (ALGORITHMS_DIR / algo_id / name).is_file():
                raise DiscoveryError(f'Algorithm "{algo_id}": missing {name}.')
        loader = getattr(contract_module(algo_id, "loader"), f"kp_algo_{algo_id}_loader")()
        if loader["id"] != algo_id:
            raise DiscoveryError(f'Folder "{algo_id}" has a loader with id "{loader["id"]}".')
        if not loader["available"]():
            skipped.append({"id": algo_id, "reason": "not available in this environment"})
            continue
        algos.append({k: loader[k] for k in ("id", "label", "short_label", "exact", "reference")}
                     | {"environment": loader["environment"](),
                        "output": contract_module(algo_id, "output")})
    refs = [a for a in algos if a["reference"]]
    if len(refs) != 1 or not refs[0]["exact"]:
        raise DiscoveryError("Exactly one available exact algorithm must have reference = True "
                             f"(found {len(refs)}).")
    return algos, skipped
