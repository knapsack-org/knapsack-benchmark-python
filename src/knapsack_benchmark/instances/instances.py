"""Reproducible 0-1 knapsack instances (classic Pisinger families)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ..helpers.rng import mround, randi, seed_state

FAMILIES = ("uncorrelated", "weakly_correlated", "strongly_correlated")
INSTANCES_FORMAT = "knapsack-instances"   # instance set file, format_version 1 (knapsack-server contracts)


@dataclass
class Instance:
    family: str
    weights: np.ndarray   # float array of integers
    values: np.ndarray
    capacity: int
    id: int = 0           # global instance id (1-based), also inside a shard


def instance_set(instances: list[Instance], instance_config: dict) -> dict:
    """Content of an instance set file (``instances.json``)."""
    return {"format": INSTANCES_FORMAT, "format_version": 1, "instance_config": instance_config,
            "instances": [{"id": i.id, "family": i.family, "n": int(i.values.size), "capacity": i.capacity,
                           "weights": i.weights, "values": i.values} for i in instances]}


def read_instances(path) -> tuple[list[Instance], dict]:
    """Instances and instance_config of an instance set file (``--instances``)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("format") != INSTANCES_FORMAT or data.get("format_version") != 1:
        raise ValueError(f"{path}: not a {INSTANCES_FORMAT} v1 file")
    return [Instance(i["family"], np.array(i["weights"], float), np.array(i["values"], float),
                     int(i["capacity"]), int(i["id"])) for i in data["instances"]], data["instance_config"]


def check_correlation(correlation: dict) -> list[str]:
    """Families of a correlation block; ValueError on invalid settings (as kb_generate_instances.m)."""
    families = correlation["families"]
    if isinstance(families, str):
        families = [families]
    families = list(families)
    if (not families or not all(isinstance(f, str) and f in FAMILIES for f in families)
            or len(set(families)) != len(families)):
        raise ValueError(f"correlation.families: 1 to 3 distinct names among {', '.join(FAMILIES)}.")
    for key in ("weak_noise_ratio", "strong_offset_ratio"):
        r = correlation[key]
        if isinstance(r, bool) or not isinstance(r, (int, float)) or not 0 <= r <= 1:
            raise ValueError(f"correlation.{key} must be in [0, 1].")
    return families


def generate_instances(count: int, seed: int, min_items: int, max_items: int,
                       R: int, capacity_ratio: float, correlation: dict | None = None) -> list[Instance]:
    """Same generator as ``kb_generate_instances.m``.

    Families rotate in the order of ``correlation["families"]``:
    uncorrelated        v ~ U(1, R)
    weakly_correlated   v = w + U(-k, k), at least 1,  k = floor(weak_noise_ratio * R)
    strongly_correlated v = w + floor(strong_offset_ratio * R)
    Weights w ~ U(1, R); capacity = floor(capacity_ratio * sum(w)).
    The number of items grows linearly from ``min_items`` to ``max_items``.
    ``correlation`` = block cfg["instances"]["correlation"] (default: config_instances()).
    """
    if correlation is None:
        from .config_instances import config_instances
        correlation = config_instances()["correlation"]
    families = check_correlation(correlation)
    weak = int(np.floor(correlation["weak_noise_ratio"] * R))
    strong = int(np.floor(correlation["strong_offset_ratio"] * R))
    state = seed_state(seed)
    out: list[Instance] = []
    for k in range(1, count + 1):
        if count > 1:
            n = mround(min_items + (max_items - min_items) * (k - 1) / (count - 1))
        else:
            n = min_items
        family = families[(k - 1) % len(families)]
        w, state = randi(state, 1, R, n)
        if family == "uncorrelated":
            v, state = randi(state, 1, R, n)
        elif family == "weakly_correlated":
            noise, state = randi(state, -weak, weak, n)
            v = np.maximum(w + noise, 1)
        else:
            v = w + strong
        out.append(Instance(family, w, v, int(np.floor(capacity_ratio * w.sum())), k))
    return out
