"""Reference instance P01 (optimum 309, items 1 2 3 4 6) and unit checks
(Python counterpart of tests/test_p01.m)."""
import numpy as np
import pytest

from knapsack_benchmark.algorithms.qubo import qubo as q
from knapsack_benchmark.algorithms.qubo_chz import qubo_chz as qz
from knapsack_benchmark.algorithms.bnb.bnb import knapsack_bnb
from knapsack_benchmark.config import benchmark_config
from knapsack_benchmark.algorithms.dp.dp import knapsack_dp
from knapsack_benchmark.algorithms.ilp.ilp import knapsack_ilp
from knapsack_benchmark.instances.instances import generate_instances

W = [23, 31, 29, 44, 53, 38, 63, 85, 89, 82]
V = [92, 57, 49, 68, 60, 43, 67, 84, 87, 72]
C = 165


@pytest.mark.parametrize("solver", [knapsack_dp, knapsack_bnb, knapsack_ilp])
def test_exact_solvers_p01(solver):
    best, items, _ = solver(V, W, C)
    assert best == 309 and items == [1, 2, 3, 4, 6]


def test_bnb_node_limit():
    best, _, info = knapsack_bnb(V, W, C, max_nodes=3)
    assert best <= 309


def test_mathworks_knapsack2qubo_example():
    Q, c, d, k = q.knapsack2qubo([5, 2, 8, 4, 3], [9, 8, 4, 5, 2], 17, 1)
    assert len(c) == 10 and d == 289 and k == 5
    x = np.array([1, 0, 1, 0, 1, 0, 1, 0, 0, 0], float)   # items 1,3,5 + slack 2
    assert q.energy(Q, c, d, x) == -16


def _opts(seed=1):
    return dict(benchmark_config()["qubo"]["tabu"], seed=seed)


def test_qubo_tabu_p01():
    P = max(V) + 1
    Q, c, d, _ = q.knapsack2qubo(V, W, C, P)
    x, f, _ = q.qubo_tabu_slack(V, W, C, P, Q, c, d, _opts())
    sol = q.decode(x, V, W, C)
    assert sol["feasible"] and sol["final_value"] == 309 and f == -309
    x, f, _ = q.qubo_tabu(Q, c, d, _opts())               # all-bits: consistent energy
    assert abs(q.energy(Q, c, d, x) - f) < 1e-9 and q.decode(x, V, W, C)["final_weight"] <= C


def test_qubo_chz_matches_qubo():
    P = max(V) + 1
    Qa, ca, da, _ = q.knapsack2qubo(V, W, C, P)
    Qb, cb, db, _ = qz.knapsack2qubo(V, W, C, P)
    assert np.array_equal(Qa, Qb) and np.array_equal(ca, cb) and da == db
    xa, fa, _ = q.qubo_tabu_slack(V, W, C, P, Qa, ca, da, _opts())
    xb, fb, _ = qz.qubo_tabu_slack(V, W, C, P, Qb, cb, db, _opts())
    assert np.array_equal(xa, xb) and fa == fb == -309


@pytest.mark.parametrize("mod", [q, qz])
def test_slack_encoding(mod):
    for s in range(18):
        assert (mod.encode_slack(s, 17) * np.array([1, 2, 4, 8, 2])).sum() == s


def test_instances_match_matlab():
    """First instance of the default run is the same as in the MATLAB/Octave project."""
    inst = generate_instances(100, 2026, 10, 48, 100, 0.5)
    assert len(inst) == 100
    assert inst[0].family == "uncorrelated" and inst[0].values.size == 10
    assert inst[0].capacity == 285 and knapsack_dp(inst[0].values, inst[0].weights, 285)[0] == 345
