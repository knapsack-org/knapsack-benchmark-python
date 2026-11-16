"""Exact 0-1 knapsack by dynamic programming (port of kb_knapsack_dp.m)."""
from __future__ import annotations

import numpy as np


def knapsack_dp(v, w, C) -> tuple[float, list[int], dict]:
    """Table m[i, j] = best value with the first i items and capacity j, O(n*C).

    One row is computed at a time with NumPy. Integer weights and capacity
    required. Returns (best value, 1-based items, info) with
    info = {"operations": n * (C + 1)} (table cells), "array_bytes": bytes of the arrays.
    """
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    n = v.size
    C = int(C)
    M = np.zeros((n + 1, C + 1))
    for i in range(n):
        M[i + 1] = M[i]
        wi = int(w[i])
        if wi <= C:
            j = np.arange(wi, C + 1)
            M[i + 1, j] = np.maximum(M[i, j], M[i, j - wi] + v[i])
    best = float(M[n, C])
    items: list[int] = []
    j = C
    for i in range(n, 0, -1):
        if M[i, j] != M[i - 1, j]:
            items.append(i)               # 1-based
            j -= int(w[i - 1])
    array_bytes = M.nbytes + v.nbytes + w.nbytes
    return best, sorted(items), {"operations": n * (C + 1), "array_bytes": array_bytes}
