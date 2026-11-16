"""Reproducible 0-1 knapsack instances (classic Pisinger families)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..helpers.rng import mround, randi, seed_state

FAMILIES = ("uncorrelated", "weakly_correlated", "strongly_correlated")


@dataclass
class Instance:
    family: str
    weights: np.ndarray   # float array of integers
    values: np.ndarray
    capacity: int


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
        out.append(Instance(family, w, v, int(np.floor(capacity_ratio * w.sum()))))
    return out
