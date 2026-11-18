"""Unit checks of greedy, sa, ga, ising and fptas on P01 (optimum 309, items 1 2 3 4 6).

Python counterpart of the new checks at the end of tests/test_p01.m.
"""
import importlib

import numpy as np
import pytest

from knapsack_benchmark.algorithms.qubo.modules import qubo as q
from knapsack_benchmark.algorithms.ising.modules.ising import knapsack2ising
from knapsack_benchmark.helpers.schema import validate

W = np.array([23, 31, 29, 44, 53, 38, 63, 85, 89, 82], float)
V = np.array([92, 57, 49, 68, 60, 43, 67, 84, 87, 72], float)
C = 165
IDS = ["greedy", "sa", "ga", "ising", "fptas"]


def _mod(algo_id, part):
    return importlib.import_module(f"knapsack_benchmark.algorithms.{algo_id}.kp_algo_{algo_id}_{part}")


def _cfg(algo_id):
    return getattr(_mod(algo_id, "config"), f"kp_algo_{algo_id}_config")()


@pytest.mark.parametrize("algo_id", IDS)
def test_adapter_contract(algo_id):
    out = _mod(algo_id, "output")
    acfg = _cfg(algo_id)
    res = out.run(V, W, C, acfg, 2026)
    assert W[np.array(res["items"]) - 1].sum() <= C
    assert res["exact"] is False and res["proven_optimal"] is False
    validate(res["details"], out.SCHEMA["details"], f"{algo_id}.details")
    validate(out.entry(acfg, {}), out.SCHEMA["entry"], algo_id)


def test_greedy_half_guarantee():
    items, info = _mod("greedy", "main").kp_algo_greedy_main(V, W, C)
    assert V[np.array(items) - 1].sum() >= 309 / 2 and info["operations"] == 10


@pytest.mark.parametrize("eps", [0.05, 0.2, 0.5, 1.0])
def test_fptas_guarantee(eps):
    items, _ = _mod("fptas", "main").kp_algo_fptas_main(V, W, C, {"epsilon": eps})
    assert W[np.array(items) - 1].sum() <= C and V[np.array(items) - 1].sum() >= (1 - eps) * 309


def test_fptas_tiny_epsilon_is_exact():
    items, _ = _mod("fptas", "main").kp_algo_fptas_main(V, W, C, {"epsilon": 0.01})
    assert items == [1, 2, 3, 4, 6]


def test_ising_energy_equals_qubo_energy():
    v, w = np.array([5, 2, 8, 4, 3], float), np.array([9, 8, 4, 5, 2], float)
    Q, c, d, _ = q.knapsack2qubo(v, w, 17, 1)
    J, h, E0, K = knapsack2ising(v, w, 17, 1)
    assert K == 5 and np.array_equal(J, J.T) and not np.diag(J).any()
    rng = np.random.default_rng(0)
    for _ in range(50):
        z = rng.integers(0, 2, 10).astype(float)
        s = 2 * z - 1
        assert abs(0.5 * s @ J @ s + h @ s + E0 - q.energy(Q, c, d, z)) < 1e-9


@pytest.mark.parametrize("algo_id", ["sa", "ga", "ising"])
def test_randomised_algorithms_are_reproducible(algo_id):
    main = getattr(_mod(algo_id, "main"), f"kp_algo_{algo_id}_main")
    a, _ = main(V, W, C, _cfg(algo_id), 7)
    b, _ = main(V, W, C, _cfg(algo_id), 7)
    assert a == b
