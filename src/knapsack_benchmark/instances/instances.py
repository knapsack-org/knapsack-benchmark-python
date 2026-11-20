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


def generate_instances(count: int, seed: int, min_items: int, max_items: int,
                       R: int, capacity_ratio: float) -> list[Instance]:
    """Same generator as ``kb_generate_instances.m``.

    uncorrelated        v ~ U(1, R)
    weakly_correlated   v = w + U(-R/10, R/10), at least 1
    strongly_correlated v = w + R/10
    Weights w ~ U(1, R); capacity = floor(capacity_ratio * sum(w)).
    The number of items grows linearly from ``min_items`` to ``max_items``.
    """
    state = seed_state(seed)
    out: list[Instance] = []
    for k in range(1, count + 1):
        if count > 1:
            n = mround(min_items + (max_items - min_items) * (k - 1) / (count - 1))
        else:
            n = min_items
        family = FAMILIES[(k - 1) % len(FAMILIES)]
        w, state = randi(state, 1, R, n)
        if family == "uncorrelated":
            v, state = randi(state, 1, R, n)
        elif family == "weakly_correlated":
            noise, state = randi(state, -(R // 10), R // 10, n)
            v = np.maximum(w + noise, 1)
        else:
            v = w + R // 10
        out.append(Instance(family, w, v, int(np.floor(capacity_ratio * w.sum())), k))
    return out
