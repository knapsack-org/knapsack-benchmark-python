"""FPTAS for the 0-1 knapsack: dynamic programming on scaled profits (port of kp_algo_fptas_main.m)."""
from __future__ import annotations

import numpy as np


def kp_algo_fptas_main(v, w, C, acfg, seed=None, mark=None) -> tuple[list[int], dict]:
    """Ibarra-Kim scheme. With n' the items that fit alone and vmax their largest value, every
    value is scaled to s_i = floor(v_i * n' / (epsilon * vmax)); minw[p] = least weight reaching
    scaled profit p (table over the items, strict improvement only, so the lowest-index set wins).
    The packing with the largest p such that minw[p] <= C is returned: its value is at least
    (1 - epsilon) times the optimum. Items with s_i = 0 are never taken.

    Returns (1-based items, info) with info = operations (table cells), scale, scaled_total,
    working_memory_bytes.
    """
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    epsilon = acfg["epsilon"]
    fit = np.flatnonzero(w <= C)
    if fit.size == 0:
        return [], {"operations": 0, "scale": 0.0, "scaled_total": 0, "working_memory_bytes": 0}
    vmax = float(v[fit].max())
    scaled = np.floor(v[fit] * fit.size / (epsilon * vmax)).astype(np.int64)
    total = int(scaled.sum())
    minw = np.full(total + 1, np.inf)
    minw[0] = 0.0
    take = np.zeros((fit.size, total + 1), bool)
    for k, i in enumerate(fit):
        s = int(scaled[k])
        if s == 0:
            continue
        cand = minw[:total + 1 - s] + w[i]
        better = cand < minw[s:]
        take[k, s:] = better
        minw[s:] = np.where(better, cand, minw[s:])
    p = int(np.flatnonzero(minw <= C).max())
    items = []
    for k in range(fit.size - 1, -1, -1):
        if take[k, p]:
            items.append(int(fit[k]) + 1)
            p -= int(scaled[k])
    items.sort()
    return items, {"operations": int(fit.size * (total + 1)),
                          "scale": epsilon * vmax / fit.size, "scaled_total": total,
                          "working_memory_bytes": int(minw.nbytes + take.nbytes + v.nbytes + w.nbytes)}
