"""Knapsack -> Ising Hamiltonian -> simulated annealing on the spins (port of kp_algo_ising_main.m)."""
from __future__ import annotations

import math

import numpy as np

from ....helpers.rng import M31, lcg, seed_state


def penalty_value(v, rule) -> float:
    """'auto' (any string) -> max(values) + 1, else the given number."""
    return float(max(v) + 1) if isinstance(rule, str) else float(rule)


def slack_weights(C) -> np.ndarray:
    """Weights of the K = max(1, ceil(log2(C + 1))) slack bits: 1, 2, 4, ..., last one truncated
    so that the largest representable slack is exactly C (same encoding as the qubo algorithm)."""
    C = int(C)
    K = max(1, C.bit_length())
    b = 2.0 ** np.arange(K)
    b[-1] = C - (2 ** (K - 1) - 1)
    return b


def knapsack2ising(v, w, C, P):
    """Ising model of the penalty form f = -sum v x + P (sum w x + s - C)^2, s = slack bits.

    With z = [x; y] and a = [w; b] the QUBO is Q = P (a a' - diag(a.a)), c = [-v; 0] + P (a.a - 2 C a),
    d = P C^2. Substituting z = (1 + sigma) / 2 gives, for sigma in {-1, +1}^N,
        H(sigma) = 1/2 sigma' J sigma + h' sigma + E0,
        J = Q / 2, h = Q 1 / 2 + c / 2, E0 = d + 1' Q 1 / 4 + 1' c / 2,
    with J symmetric and zero on the diagonal. H(sigma) equals the QUBO energy of z.
    Returns J, h, E0 and the number of slack bits.
    """
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    b = slack_weights(C)
    a = np.concatenate([w, b])
    c = np.concatenate([-v, np.zeros(b.size)]) + P * (a * a - 2 * C * a)
    Q = P * (np.outer(a, a) - np.diag(a * a))
    J = Q / 2
    h = Q.sum(axis=1) / 2 + c / 2
    E0 = P * C * C + Q.sum() / 4 + c.sum() / 2
    return J, h, float(E0), int(b.size)


def ising_anneal(J, h, E0, acfg, seed, scale) -> tuple[np.ndarray, float, dict]:
    """Single-spin-flip simulated annealing of H. Flipping spin j changes H by -2 s_j g_j, where
    g = h + J s is the local field (updated in O(N) after an accepted flip). Each restart starts from
    s_i = +1 if u_i < 0.5 else -1 and runs steps_factor * N proposals; acceptance if dH <= 0 or
    u < exp(-dH / T); T falls geometrically from t0_factor * scale to t_end_factor * scale
    (scale = P * max(w), the energy of flipping one heavy item).
    Returns the best spins, their H and statistics."""
    N = h.size
    steps = int(acfg["steps_factor"] * N)
    t0, t1 = acfg["t0_factor"] * scale, acfg["t_end_factor"] * scale
    alpha = (t1 / t0) ** (1.0 / (steps - 1)) if steps > 1 else 1.0
    state = seed_state(seed)
    best_H, best_s = math.inf, None
    proposals = accepted = 0
    for _ in range(acfg["restarts"]):
        u, state = lcg(state, N)
        s = np.where(u < 0.5, 1.0, -1.0)
        g = h + J @ s
        H = 0.5 * float(s @ (g + h)) + E0
        if H < best_H:
            best_H, best_s = H, s.copy()
        T = t0
        for _ in range(steps):
            state = (16807 * state) % M31
            j = min(int(state / M31 * N), N - 1)
            dH = -2.0 * s[j] * g[j]
            proposals += 1
            ok = dH <= 0
            if not ok:
                state = (16807 * state) % M31
                ok = state / M31 < math.exp(-dH / T)
            if ok:
                g += (-2.0 * s[j]) * J[:, j]
                s[j] = -s[j]
                H += dH
                accepted += 1
                if H < best_H:
                    best_H, best_s = H, s.copy()
            T *= alpha
    return best_s, best_H, {"proposals": proposals, "accepted": accepted,
                            "t_start": t0, "t_end": t1}


def decode(s, v, w, C) -> dict:
    """Spin solution -> knapsack: item i is taken when s_i = +1 (slack spins ignored). An overweight
    packing is repaired by removing, one at a time, the taken item with the lowest v/w (lowest index
    on ties); both the raw and the final packing are reported."""
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    n = v.size
    take = s[:n] > 0
    sol = {"items": [int(i) + 1 for i in np.flatnonzero(take)],
           "value": float(v[take].sum()), "weight": float(w[take].sum())}
    sol["feasible"] = bool(sol["weight"] <= C)
    sol["repaired"] = not sol["feasible"]
    if sol["repaired"]:
        ratio = v / w
        while w[take].sum() > C:
            idx = np.flatnonzero(take)
            take[idx[int(np.argmin(ratio[idx]))]] = False
    sol["final_items"] = [int(i) + 1 for i in np.flatnonzero(take)]
    return sol
