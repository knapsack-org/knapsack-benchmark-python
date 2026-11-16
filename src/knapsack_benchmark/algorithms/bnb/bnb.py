"""Exact 0-1 knapsack by depth-first branch and bound (port of kb_knapsack_bnb.m)."""
from __future__ import annotations

import math

import numpy as np


def knapsack_bnb(v, w, C, max_nodes: float = math.inf) -> tuple[float, list[int], dict]:
    """Items sorted by value/weight (stable); "take" is tried before "skip".

    A node is pruned when floor(Dantzig bound) <= best value found (LP
    relaxation: greedy fill + fraction of the critical item; values are
    integers). The greedy solution is the initial lower bound. Iterative
    backtracking, O(n) memory. ``max_nodes`` stops the search early
    (info["proven_optimal"] is then False).
    Returns (best value, 1-based items, info) with info = {nodes, proven_optimal,
    array_bytes}.
    """
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    n = v.size
    order = np.argsort(-(v / w), kind="stable")
    vs, ws = v[order], w[order]
    Wc = np.concatenate([[0.0], np.cumsum(ws)])     # Wc[i] = weight of the first i sorted items
    Vc = np.concatenate([[0.0], np.cumsum(vs)])

    bx = np.zeros(n)                                # greedy initial solution
    load = 0.0
    for i in range(n):
        if load + ws[i] <= C:
            bx[i] = 1
            load += ws[i]
    best = float(vs @ bx)

    x = np.zeros(n)
    k = 0                                           # next item to decide (0-based)
    load = val = 0.0
    nodes = 0
    proven = True
    while True:
        nodes += 1
        if nodes > max_nodes:
            proven = False
            break
        if val > best:
            best = val
            bx = x.copy()

        back = False
        if k >= n:
            back = True
        else:
            cap = C - load
            over = np.flatnonzero(Wc[k + 1:] - Wc[k] > cap)
            if over.size == 0:
                ub = val + Vc[n] - Vc[k]            # all remaining items fit
            else:
                j = k + over[0]                     # critical item
                ub = val + Vc[j] - Vc[k] + vs[j] * (cap - (Wc[j] - Wc[k])) / ws[j]
            if math.floor(ub + 1e-9) <= best:
                back = True                         # prune
            elif load + ws[k] <= C:
                x[k] = 1                            # take item k
                load += ws[k]
                val += vs[k]
                k += 1
            else:
                x[k] = 0                            # item k does not fit: skip
                k += 1

        if back:                                    # undo the last "take", try "skip"
            taken = np.flatnonzero(x[:k])
            if taken.size == 0:
                break
            i = int(taken[-1])
            x[i] = 0
            load -= ws[i]
            val -= vs[i]
            k = i + 1

    items = sorted(int(order[i]) + 1 for i in np.flatnonzero(bx))
    array_bytes = sum(a.nbytes for a in (v, w, order, vs, ws, Wc, Vc, x, bx))
    return best, items, {"nodes": nodes, "proven_optimal": proven, "array_bytes": array_bytes}
