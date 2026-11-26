"""QUBO approach to the 0-1 knapsack (port of modules/kb_knapsack2qubo.m, kb_qubo_tabu*.m,
kb_decode.m, kb_encode_slack.m).

Model (same as MATLAB's ``knapsack2qubo``):
    f(x, s) = -sum(v*x) + penalty * (sum(w*x) + s - C)**2 = x'Qx + c'x + d
with the slack s in 0..C binary-encoded on K bits of weights 1, 2, 4, ...,
C - (2**(K-1) - 1). x = [items (n); slack bits (K)]; Q symmetric, zero diagonal.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from ....helpers.rng import lcg, mround, seed_state


def slack_coefficients(M: int) -> list[int]:
    k = max(1, math.ceil(math.log2(M + 1)))
    return [2 ** j for j in range(k - 1)] + [M - (2 ** (k - 1) - 1)]


def knapsack2qubo(v, w, M, penalty: float = 1.0):
    """Return (Q, c, d, number of slack bits). With penalty > max(v) the QUBO
    minimum is the knapsack optimum."""
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    M = int(M)
    b = slack_coefficients(M)
    a = np.concatenate([w, b])
    Q = penalty * np.outer(a, a)
    np.fill_diagonal(Q, 0.0)                       # x_i^2 = x_i -> moved to c
    c = np.concatenate([-v, np.zeros(len(b))]) + penalty * (a ** 2 - 2 * M * a)
    d = penalty * M ** 2
    return Q, c, d, len(b)


def encode_slack(s: float, M: int) -> np.ndarray:
    """Slack bits for value s in 0..M (weights 1, 2, 4, ..., remainder)."""
    k = max(1, math.ceil(math.log2(M + 1)))
    r = M - (2 ** (k - 1) - 1)
    bits = np.zeros(k)
    if s > 2 ** (k - 1) - 1:
        bits[k - 1] = 1
        s -= r
    for j in range(1, k):
        bits[j - 1] = math.floor(s / 2 ** (j - 1)) % 2
    return bits


def energy(Q, c, d, x) -> float:
    return float(x @ Q @ x + c @ x + d)


@dataclass
class TabuStats:
    iterations: int
    restarts: int
    tenure: int
    move_evaluations: int
    array_bytes: int = 0   # Q, c and the search vectors (like whos in MATLAB)


def qubo_tabu_slack(v, w, C, penalty, Q, c, d, opts: dict):
    """Tabu search on item bits with the slack bits set optimally (default mode).

    For fixed items the best slack is C - W if the packing fits, else 0; minimising
    the QUBO over the slack bits exactly leaves E(items) = -V + penalty*max(0, W-C)**2.
    One item flip per iteration, tabu tenure, aspiration, multi-start.
    Returns (full QUBO vector, energy recomputed from Q, c, d, TabuStats).
    """
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    n = v.size
    max_iter = opts["max_iter_factor"] * n
    stall_limit = opts["stall_factor"] * n
    tenure = opts["tenure_min"] + mround(n / 10)
    state = seed_state(opts["seed"])

    best = np.zeros(n)
    best_e = 0.0                                   # empty knapsack
    total_iter = 0
    for _ in range(opts["restarts"]):
        u, state = lcg(state, n)
        x = (u < 0.5).astype(float)
        W, V = float(w @ x), float(v @ x)
        e = -V + penalty * max(0.0, W - C) ** 2
        run_best = e
        if e < best_e:
            best_e, best = e, x.copy()
        tabu_until = np.zeros(n)
        stall = 0
        it = 0
        for it in range(1, max_iter + 1):
            s = 1 - 2 * x                          # +1 add item, -1 remove item
            W2 = W + s * w
            V2 = V + s * v
            delta = (-V2 + penalty * np.maximum(0.0, W2 - C) ** 2) - e
            allowed = (tabu_until < it) | (e + delta < best_e)
            if not allowed.any():
                allowed[:] = True
            delta = np.where(allowed, delta, np.inf)
            j = int(np.argmin(delta))
            x[j] += s[j]
            W, V = W2[j], V2[j]
            e += delta[j]
            tabu_until[j] = it + tenure
            if e < best_e:
                best_e, best = e, x.copy()
            if e < run_best:
                run_best, stall = e, 0
            else:
                stall += 1
                if stall > stall_limit:
                    break
        total_iter += it

    Wb = float(w @ best)
    x_full = np.concatenate([best, encode_slack(max(0.0, C - Wb) * (Wb <= C), int(C))])
    vectors = 10 * n * 8                           # x, best, tabu_until, s, W2, V2, delta, ...
    array_bytes = int(Q.nbytes + c.nbytes + v.nbytes + w.nbytes + x_full.nbytes + vectors)
    stats = TabuStats(total_iter, opts["restarts"], tenure, total_iter * n, array_bytes)
    return x_full, energy(Q, c, d, x_full), stats


def qubo_tabu(Q, c, d, opts: dict):
    """Plain multi-start single-bit-flip tabu search on all QUBO bits ('all-bits')."""
    N = len(c)
    max_iter = opts["max_iter_factor"] * N
    stall_limit = opts["stall_factor"] * N
    tenure = opts["tenure_min"] + mround(N / 10)
    state = seed_state(opts["seed"])
    best_x, best_f = np.zeros(N), float(d)
    total_iter = 0
    for _ in range(opts["restarts"]):
        u, state = lcg(state, N)
        x = (u < 0.5).astype(float)
        g = c + 2 * (Q @ x)                        # flip gain of bit i: (1 - 2 x_i) g_i
        f = energy(Q, c, d, x)
        run_best = f
        tabu_until = np.zeros(N)
        stall = 0
        it = 0
        for it in range(1, max_iter + 1):
            delta = (1 - 2 * x) * g
            allowed = (tabu_until < it) | (f + delta < best_f)
            if not allowed.any():
                allowed[:] = True
            delta = np.where(allowed, delta, np.inf)
            j = int(np.argmin(delta))
            s = 1 - 2 * x[j]
            x[j] += s
            f += delta[j]
            g = g + 2 * s * Q[:, j]
            tabu_until[j] = it + tenure
            if f < best_f:
                best_f, best_x = f, x.copy()
            if f < run_best:
                run_best, stall = f, 0
            else:
                stall += 1
                if stall > stall_limit:
                    break
        total_iter += it
    array_bytes = int(Q.nbytes + c.nbytes + 6 * N * 8)   # x, best_x, g, delta, tabu_until, ...
    return best_x, best_f, TabuStats(total_iter, opts["restarts"], tenure, total_iter * N,
                                     array_bytes)


def decode(x, v, w, C) -> dict:
    """QUBO vector -> knapsack solution (counterpart of quboResult2knapsack).

    If the packing is overweight, items with the lowest value/weight ratio are
    removed until it fits; raw and repaired results are both reported.
    Items are 1-based.
    """
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    n = v.size
    take = np.round(np.asarray(x)[:n]) > 0
    sol = {
        "items": [int(i) + 1 for i in np.flatnonzero(take)],
        "value": float(v[take].sum()),
        "weight": float(w[take].sum()),
    }
    sol["feasible"] = sol["weight"] <= C
    sol["repaired"] = False
    if not sol["feasible"]:
        sol["repaired"] = True
        ratio = v / w
        while w[take].sum() > C:
            idx = np.flatnonzero(take)
            take[idx[np.argmin(ratio[idx])]] = False
    sol["final_items"] = [int(i) + 1 for i in np.flatnonzero(take)]
    sol["final_value"] = float(v[take].sum())
    sol["final_weight"] = float(w[take].sum())
    return sol


def penalty_value(values, rule) -> float:
    """'auto' -> max(value) + 1 (every infeasible packing costs more than it gains)."""
    return float(np.max(values)) + 1 if isinstance(rule, str) else float(rule)
