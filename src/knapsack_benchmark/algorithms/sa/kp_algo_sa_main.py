"""Simulated annealing on the item bits (port of kp_algo_sa_main.m)."""
from __future__ import annotations

import math

import numpy as np

from ...helpers.rng import M31, lcg, seed_state


def penalty_value(v, rule) -> float:
    """'auto' (any string) -> max(values) + 1, else the given number."""
    return float(max(v) + 1) if isinstance(rule, str) else float(rule)


def kp_algo_sa_main(v, w, C, acfg, seed, mark=None) -> tuple[list[int], dict]:
    """Single-bit-flip simulated annealing, energy E(x) = -V(x) + P * max(0, W(x) - C)**2.

    Each restart starts from x_i = [u_i < 0.5] and runs steps = steps_factor * n proposals; one
    proposal flips a random item (u -> j = floor(u * n)), accepted if dE <= 0 or u < exp(-dE / T).
    The temperature falls geometrically from t0_factor * max(v) to t_end_factor * max(v).
    The best FEASIBLE packing seen (empty packing at least) is returned. The uniforms come from
    the portable LCG, inlined in the loop (same sequence as kb_lcg).
    """
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    n = v.size
    vl, wl = v.tolist(), w.tolist()
    P = penalty_value(v, acfg["penalty"])
    steps = int(acfg["steps_factor"] * n)
    vmax = float(v.max())
    t0, t1 = acfg["t0_factor"] * vmax, acfg["t_end_factor"] * vmax
    alpha = (t1 / t0) ** (1.0 / (steps - 1)) if steps > 1 else 1.0
    state = seed_state(seed)
    best_v, best_x = 0.0, [0] * n
    proposals = accepted = 0
    for _ in range(acfg["restarts"]):
        u, state = lcg(state, n)
        x = [1 if ui < 0.5 else 0 for ui in u]
        W = sum(wl[i] for i in range(n) if x[i])
        V = sum(vl[i] for i in range(n) if x[i])
        E = -V + P * max(0.0, W - C) ** 2
        if W <= C and V > best_v:
            best_v, best_x = V, x[:]
        T = t0
        for _ in range(steps):
            state = (16807 * state) % M31
            j = min(int(state / M31 * n), n - 1)
            if x[j]:
                W2, V2 = W - wl[j], V - vl[j]
            else:
                W2, V2 = W + wl[j], V + vl[j]
            dE = (-V2 + P * max(0.0, W2 - C) ** 2) - E
            proposals += 1
            ok = dE <= 0
            if not ok:
                state = (16807 * state) % M31
                ok = state / M31 < math.exp(-dE / T)
            if ok:
                x[j] ^= 1
                W, V, E = W2, V2, E + dE
                accepted += 1
                if W <= C and V > best_v:
                    best_v, best_x = V, x[:]
            T *= alpha
    items = [i + 1 for i in range(n) if best_x[i]]
    info = {"penalty": P, "proposals": proposals, "accepted": accepted, "t_start": t0, "t_end": t1,
            "working_memory_bytes": int(v.nbytes + w.nbytes + 2 * n)}
    return items, info
