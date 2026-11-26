"""Instance correlation settings, QUBO variant B and QC (ADR 0023).

The QAOA expectations are the Octave 11.3 values of kb_qc_qaoa on the same input (parity).
"""
import numpy as np
import pytest

from knapsack_benchmark.algorithms.greedy.kp_algo_greedy_main import kp_algo_greedy_main
from knapsack_benchmark.algorithms.qc.kp_algo_qc_config import kp_algo_qc_config
from knapsack_benchmark.algorithms.qc.kp_algo_qc_main import kp_algo_qc_main
from knapsack_benchmark.algorithms.qc.modules import qubo as qc_qubo
from knapsack_benchmark.algorithms.qc.modules.greedy import greedy
from knapsack_benchmark.algorithms.qc.modules.qaoa import QaoaTooLarge, qaoa
from knapsack_benchmark.algorithms.qubo.kp_algo_qubo_config import kp_algo_qubo_config
from knapsack_benchmark.algorithms.qubo.kp_algo_qubo_main import kp_algo_qubo_main
from knapsack_benchmark.algorithms.qubo_b.kp_algo_qubo_b_config import kp_algo_qubo_b_config
from knapsack_benchmark.algorithms.qubo_b.kp_algo_qubo_b_main import kp_algo_qubo_b_main
from knapsack_benchmark.config import benchmark_config
from knapsack_benchmark.instances.config_instances import config_instances
from knapsack_benchmark.instances.instances import generate_instances

V = [92, 57, 49, 68, 60, 43, 67, 84, 87, 72]     # P01, optimum 309
W = [23, 31, 29, 44, 53, 38, 63, 85, 89, 82]
C = 165


def corr(**kw):
    return dict(config_instances()["correlation"], **kw)


def test_correlation_defaults_and_settings():
    default = generate_instances(30, 2026, 10, 20, 100, 0.5)
    same = generate_instances(30, 2026, 10, 20, 100, 0.5, corr())
    assert all(np.array_equal(a.values, b.values) and a.family == b.family for a, b in zip(default, same))
    assert [i.family for i in default[:3]] == ["uncorrelated", "weakly_correlated", "strongly_correlated"]

    strong = generate_instances(6, 3, 5, 9, 50, 0.5, corr(families=["strongly_correlated"], strong_offset_ratio=0.2))
    assert all(i.family == "strongly_correlated" and np.array_equal(i.values, i.weights + 10) for i in strong)
    flat = generate_instances(6, 3, 5, 9, 50, 0.5, corr(families=["weakly_correlated"], weak_noise_ratio=0))
    assert all(np.array_equal(i.values, i.weights) for i in flat)
    order = generate_instances(4, 3, 5, 9, 50, 0.5, corr(families=["strongly_correlated", "uncorrelated"]))
    assert [i.family for i in order] == ["strongly_correlated", "uncorrelated"] * 2
    one = generate_instances(2, 3, 5, 9, 50, 0.5, corr(families="uncorrelated"))   # string = one family
    assert [i.family for i in one] == ["uncorrelated"] * 2


@pytest.mark.parametrize("bad", [dict(families=[]), dict(families=["uncorrelated", "uncorrelated"]),
                                 dict(families=["anti_correlated"]), dict(weak_noise_ratio=-0.1),
                                 dict(strong_offset_ratio=1.5), dict(weak_noise_ratio="0.1")])
def test_correlation_invalid(bad):
    with pytest.raises(ValueError):
        generate_instances(3, 1, 5, 9, 50, 0.5, corr(**bad))


def test_correlation_request_override():
    cfg = benchmark_config({"instances": {"correlation": {"families": ["uncorrelated"]}}})
    assert cfg["instances"]["correlation"] == corr(families=["uncorrelated"])
    with pytest.raises(ValueError):
        benchmark_config({"instances": {"correlation": {"nope": 1}}})


def test_qubo_b_and_qc_equal_qubo():
    assert kp_algo_qubo_b_config() == kp_algo_qubo_config()
    qc_cfg = kp_algo_qc_config()
    assert {k: x for k, x in qc_cfg.items() if k != "qaoa"} == kp_algo_qubo_config()
    cases = [(V, W, C)] + [(i.values, i.weights, i.capacity) for i in generate_instances(12, 2026, 10, 48, 100, 0.5)]
    for k, (v, w, c) in enumerate(cases):
        a, ia = kp_algo_qubo_main(v, w, c, kp_algo_qubo_config(), 2026 + k)
        b, ib = kp_algo_qubo_b_main(v, w, c, kp_algo_qubo_b_config(), 2026 + k)
        q, iq = kp_algo_qc_main(v, w, c, qc_cfg, 2026 + k)
        assert a == b == q and ia["energy"] == ib["energy"] == iq["energy"]
        assert ia["move_evaluations"] == ib["move_evaluations"] == iq["move_evaluations"]


def test_qc_greedy_is_greedy():
    for i in generate_instances(12, 7, 5, 40, 100, 0.5):
        assert greedy(i.values, i.weights, i.capacity) == kp_algo_greedy_main(i.values, i.weights, i.capacity)


def test_qaoa_mathworks_example():
    v, w = [5, 2, 8, 4, 3], [9, 8, 4, 5, 2]
    Q, c, d, _ = qc_qubo.knapsack2qubo(v, w, 17, max(v) + 1)
    x, e, s = qaoa(Q, c, d, dict(kp_algo_qc_config()["qaoa"], seed=1))
    assert list(x.astype(int)) == [0, 0, 1, 1, 1, 0, 1, 1, 0, 0] and e == -15   # same as Octave
    assert float(x @ Q @ x + c @ x + d) == e
    assert np.allclose(s.gamma, [3.46884188833873, 7.00313362362725], atol=1e-12)
    assert np.allclose(s.beta, [2.81434341884086, 3.01069295969022], atol=1e-12)
    assert abs(s.expected_energy - 0.0232939696574762) < 1e-13 and s.iterations == 320
    sol = qc_qubo.decode(x, v, w, 17)
    assert sol["feasible"] and sol["final_items"] == [3, 4, 5] and sol["final_value"] == 15


def test_qaoa_too_large():
    Q, c, d, _ = qc_qubo.knapsack2qubo(V, W, C, max(V) + 1)     # 10 items + 8 slack bits
    with pytest.raises(QaoaTooLarge):
        qaoa(Q, c, d, dict(kp_algo_qc_config()["qaoa"], seed=1, max_qubits=17))
