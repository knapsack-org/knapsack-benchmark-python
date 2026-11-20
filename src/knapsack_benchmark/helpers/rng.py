"""Portable pseudo-random numbers (Park-Miller minimal standard LCG).

Same sequence as ``kb_lcg`` / ``kb_randi`` / ``kb_seed`` in knapsack-benchmark-matlab,
so MATLAB, Octave and Python generate identical instances and tabu starts.
All products stay below 2**53, so floating point is exact.
"""
from __future__ import annotations

import numpy as np

M31 = 2147483647


def seed_state(seed: int) -> int:
    """Turn any integer seed into a valid generator state (1 .. 2**31 - 2)."""
    return int(abs(int(seed))) % 2147483646 + 1


def lcg(state: int, count: int = 1) -> tuple[np.ndarray, int]:
    """Return ``count`` numbers in (0, 1) and the updated state."""
    u = np.empty(count)
    for i in range(count):
        state = (16807 * state) % M31
        u[i] = state / M31
    return u, state


def lcg_powers(count: int) -> np.ndarray:
    """16807**k mod M31 for k = 1 .. count (int64). ``lcg_powers(count) * state % M31`` are the
    states after 1 .. count draws from ``state`` (products < 2**62, exact): the stream of ``lcg``
    in one vector operation (``states / M31`` are its numbers)."""
    p = np.empty(count, np.int64)
    p[:1], k = 16807, 1
    while k < count:                               # doubling: p[k + i] = p[i] * p[k - 1]
        m = min(k, count - k)
        p[k:k + m] = p[:m] * p[k - 1] % M31
        k += m
    return p


def randi(state: int, lo: int, hi: int, count: int = 1) -> tuple[np.ndarray, int]:
    """``count`` integers uniformly drawn from ``lo..hi`` (as floats, like MATLAB)."""
    u, state = lcg(state, count)
    r = np.minimum(lo + np.floor(u * (hi - lo + 1)), hi)
    return r, state


def mround(x: float) -> int:
    """MATLAB/Octave ``round`` for non-negative numbers (halves away from zero)."""
    return int(np.floor(x + 0.5))
