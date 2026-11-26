"""QAOA on the QUBO f(x) = x'Qx + c'x + d, simulated on a state vector (port of modules/kb_qc_qaoa.m).

- E(z) = f(z) for every basis state z of the N = len(c) qubits (bit j of z = x[j]);
- start |+>^N; each layer l applies the cost phase exp(-1j*gamma[l]*Es) with the energies
  scaled to Es = (E - min E) / (max E - min E) in [0, 1], then the mixer exp(-1j*beta[l]*X)
  on every qubit;
- angles: deterministic search of the expected Es (no scipy optimiser, so Python = MATLAB):
  layer by layer a grid x grid search of (gamma, beta) on (0, 2pi) x (0, pi) with the earlier
  layers fixed, then ``refine`` rounds of +-h coordinate moves on every angle (h halved after
  each round); a move or grid point is taken only if it improves by more than 1e-12;
- ``shots`` states sampled with the project LCG from the final state; x is the sampled state of
  lowest E (first sampled on ties), energy = f(x).
2**N complex amplitudes: N > max_qubits raises QaoaTooLarge.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from ....helpers.rng import lcg, seed_state


class QaoaTooLarge(ValueError):
    """More qubits than opts["max_qubits"] (MATLAB identifier kb_qc_qaoa:tooLarge)."""


@dataclass
class QaoaStats:
    iterations: int                 # objective evaluations
    move_evaluations: int           # same (operations of the benchmark)
    array_bytes: int                # bits, energies, state vector, cumulative probabilities
    gamma: list = field(default_factory=list)
    beta: list = field(default_factory=list)
    expected_energy: float = 0.0    # scaled, of the chosen angles


def qaoa(Q, c, d, opts: dict):
    """qaoa(Q, c, d, opts) -> (x, energy, stats), same outputs as qubo.qubo_tabu.

    opts: layers, shots, grid, refine, max_qubits, seed.
    """
    Q = np.asarray(Q, float)
    c = np.asarray(c, float).ravel()
    N = c.size
    if N > opts["max_qubits"]:
        raise QaoaTooLarge(f"QAOA: {N} qubits > max_qubits = {opts['max_qubits']} (2**N amplitudes).")
    S = 2 ** N
    idx = np.arange(S)
    B = np.empty((S, N), bool)                     # B[z, j] = bit j of z
    for j in range(N):
        B[:, j] = (idx >> j) & 1 == 1
    E = d + np.zeros(S)                            # integer energies: exact in doubles
    for j in range(N):
        bj = B[:, j].astype(float)
        E = E + (c[j] + Q[j, j]) * bj
        for i in range(j):
            if Q[i, j] + Q[j, i] != 0:
                E = E + (Q[i, j] + Q[j, i]) * (B[:, i].astype(float) * bj)
    lo = E.min()
    span = E.max() - lo
    if span == 0:
        span = 1.0
    Es = (E - lo) / span

    def evolve(g, b):
        q = np.full(S, 1 / math.sqrt(S), complex)
        for t in range(len(g)):
            q = q * np.exp(-1j * g[t] * Es)
            cb = math.cos(b[t])
            sb = -1j * math.sin(b[t])
            for j in range(N):                     # exp(-1j*beta*X) on qubit j: pairs (bit 0, bit 1)
                R = q.reshape(-1, 2, 2 ** j)
                a0 = R[:, 0, :].copy()
                a1 = R[:, 1, :].copy()
                R[:, 0, :] = cb * a0 + sb * a1
                R[:, 1, :] = sb * a0 + cb * a1
                q = R.reshape(-1)
        return q

    def expected(g, b):
        return float(np.sum(np.abs(evolve(g, b)) ** 2 * Es))

    evals = 0
    G = opts["grid"]
    layers = opts["layers"]
    gamma = [0.0] * layers
    beta = [0.0] * layers
    best_f = math.inf
    for l in range(layers):                        # layer by layer, earlier layers fixed
        best_f = math.inf
        g_best = b_best = 0.0
        for gi in range(1, G + 1):
            for bi in range(1, G + 1):
                gamma[l] = 2 * math.pi * (gi - 0.5) / G
                beta[l] = math.pi * (bi - 0.5) / G
                f = expected(gamma[:l + 1], beta[:l + 1])
                evals += 1
                if f < best_f - 1e-12:
                    best_f, g_best, b_best = f, gamma[l], beta[l]
        gamma[l], beta[l] = g_best, b_best
    h = [2 * math.pi / G, math.pi / G]             # step for gamma, beta
    for _ in range(opts["refine"]):
        for l in range(layers):
            for kind in (0, 1):
                for s in (1, -1):
                    g, b = list(gamma), list(beta)
                    if kind == 0:
                        g[l] = g[l] + s * h[0]
                    else:
                        b[l] = b[l] + s * h[1]
                    f = expected(g, b)
                    evals += 1
                    if f < best_f - 1e-12:
                        best_f, gamma, beta = f, g, b
        h = [h[0] / 2, h[1] / 2]

    psi = evolve(gamma, beta)
    cp = np.cumsum(np.abs(psi) ** 2)
    u, _ = lcg(seed_state(opts["seed"]), opts["shots"])
    best_z, energy = 0, math.inf
    for k in range(opts["shots"]):
        z = min(int(np.searchsorted(cp, u[k] * cp[-1], side="left")), S - 1)
        if E[z] < energy:
            energy, best_z = float(E[z]), z
    x = B[best_z].astype(float)
    nbytes = int(B.nbytes + E.nbytes + Es.nbytes + psi.nbytes + cp.nbytes)
    return x, energy, QaoaStats(evals, evals, nbytes, gamma, beta, best_f)
