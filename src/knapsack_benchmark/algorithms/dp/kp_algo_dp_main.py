"""Exact 0-1 knapsack by dynamic programming (port of kp_algo_dp_main.m)."""
from __future__ import annotations

import numpy as np


def kp_algo_dp_main(v, w, C, acfg=None, seed=None, mark=None) -> tuple[list[int], dict]:
    """Table m[i, j] = best value with the first i items and capacity j, O(n*C).

    One row is computed at a time with NumPy. Integer weights and capacity
    required; settings, seed and phase marks are not used. Returns (1-based items, info)
    with info = {"value": optimum, "operations": n * (C + 1) (table cells),
    "working_memory_bytes": bytes of the arrays}.
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
    return sorted(items), {"value": best, "operations": n * (C + 1),
                           "working_memory_bytes": array_bytes}
