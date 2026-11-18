"""Ratio greedy with a best-single-item fix (port of kp_algo_greedy_main.m)."""
from __future__ import annotations

import numpy as np


def kp_algo_greedy_main(v, w, C, acfg=None, seed=None, mark=None) -> tuple[list[int], dict]:
    """Sort by v/w (decreasing, ties keep the index order), take every item that still fits,
    then return the better of that packing and the single most valuable item that fits
    (guarantee: at least half of the optimum). O(n log n).

    Returns (1-based items, info) with info = operations (= n items scanned),
    greedy_value, single_value, chose_single, working_memory_bytes.
    """
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    n = v.size
    order = np.argsort(-(v / w), kind="stable")
    take = np.zeros(n, bool)
    room = float(C)
    for i in order:
        if w[i] <= room:
            take[i] = True
            room -= w[i]
    greedy_value = float(v[take].sum())

    fits = np.flatnonzero(w <= C)
    single = -1
    single_value = 0.0
    if fits.size:
        single = int(fits[np.argmax(v[fits])])          # lowest index on ties
        single_value = float(v[single])
    chose_single = single_value > greedy_value
    if chose_single:
        take = np.zeros(n, bool)
        take[single] = True
    items = [int(i) + 1 for i in np.flatnonzero(take)]
    info = {"operations": n, "greedy_value": greedy_value, "single_value": single_value,
            "chose_single": chose_single,
            "working_memory_bytes": int(v.nbytes + w.nbytes + order.nbytes + take.nbytes)}
    return items, info
