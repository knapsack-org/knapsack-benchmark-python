"""Reference instance P01 (optimum 309, items 1 2 3 4 6) and unit checks
(Python counterpart of tests/test_p01.m)."""
import json

import numpy as np
import pytest

from knapsack_benchmark.algorithms.bnb.kp_algo_bnb_main import kp_algo_bnb_main
from knapsack_benchmark.algorithms.dp.kp_algo_dp_main import kp_algo_dp_main
from knapsack_benchmark.algorithms.ilp.kp_algo_ilp_main import kp_algo_ilp_main
from knapsack_benchmark.algorithms.qubo.kp_algo_qubo_config import kp_algo_qubo_config
from knapsack_benchmark.algorithms.qubo.modules import qubo as q
from knapsack_benchmark.algorithms.qubo_chz.modules import qubo_chz as qz
from knapsack_benchmark.cli import main
from knapsack_benchmark.config import benchmark_config, merge_settings
from knapsack_benchmark.helpers.discover import DiscoveryError, discover_algorithms, output_schema
from knapsack_benchmark.instances.instances import generate_instances

W = [23, 31, 29, 44, 53, 38, 63, 85, 89, 82]
V = [92, 57, 49, 68, 60, 43, 67, 84, 87, 72]
C = 165


def test_every_algorithm_on_p01(conforms):
    """Every algorithm of algorithms/, as the benchmark runs it (no edit needed for a new one)."""
    cfg = benchmark_config()
    algos, _ = discover_algorithms()
    assert sum(a["reference"] for a in algos) == 1
    v, w = np.array(V, float), np.array(W, float)
    for a in algos:
        out = a["output"].run(v, w, C, cfg[a["id"]], cfg["seed"])
        idx = np.array(out["items"], dtype=int) - 1
        assert w[idx].sum() <= C, a["id"]
        if a["exact"]:
            assert v[idx].sum() == 309, a["id"]
        schema = output_schema(a["id"])
        entry = a["output"].entry(cfg[a["id"]], a["environment"])
        conforms(out["details"], schema["details"], f"{a['id']}.details")
        conforms(entry, schema["entry"], a["id"])
        conforms(entry["config"], schema["config"], f"{a['id']}.config")


def test_describe_lists_every_algorithm_with_schemas(capsys):
    assert main(["--describe"]) == 0
    d = json.loads(capsys.readouterr().out)
    ids = [e["id"] for e in d["algorithms"]]
    assert d["project"] == "knapsack-benchmark-python" and len(ids) == 10 and ids == sorted(ids)
    assert set(d["algorithm_schemas"]) == set(ids)
    for s in d["algorithm_schemas"].values():
        assert s["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert {"entry", "config", "details"} <= set(s)


def test_request_instances_file_and_shard(tmp_path):
    """Request overrides, instances.json round trip, and a shard with global ids gives the same results (P7)."""
    req = tmp_path / "req.json"
    req.write_text(json.dumps({"seed": 7, "instances": {"count": 3, "max_items": 12},
                               "algorithms": ["sa"], "algorithm_config": {"sa": {"restarts": 2}}}))
    assert main(["--request", str(req), "--out", str(tmp_path / "full")]) == 0
    full = json.loads((tmp_path / "full" / "raw.json").read_text())
    iset = json.loads((tmp_path / "full" / "instances.json").read_text())
    assert full["format"] == "knapsack-raw" and full["format_version"] == 1
    assert [a["id"] for a in full["algorithms"]] == ["dp", "sa"]     # reference always added
    assert full["algorithms"][1]["config"]["restarts"] == 2 and full["parameters"]["seed"] == 7
    assert full["instance_config"] == {"seed": 7, "count": 3, "min_items": 10, "max_items": 12,
                                       "max_coefficient": 100, "capacity_ratio": 0.5}
    assert iset["format"] == "knapsack-instances" and [i["id"] for i in iset["instances"]] == [1, 2, 3]
    assert all("is_optimal" not in r and "gap_percent" not in r
               for i in full["instances"] for r in i["results"].values())

    iset["instances"] = iset["instances"][1:2]                     # shard: instance 2 only
    shard = tmp_path / "shard.json"
    shard.write_text(json.dumps(iset))
    req.write_text(json.dumps({"algorithms": ["sa"], "algorithm_config": {"sa": {"restarts": 2}}}))
    assert main(["--request", str(req), "--instances", str(shard), "--out", str(tmp_path / "shard")]) == 0
    part = json.loads((tmp_path / "shard" / "raw.json").read_text())
    assert not (tmp_path / "shard" / "instances.json").exists()
    assert part["parameters"]["seed"] == 7 and [i["id"] for i in part["instances"]] == [2]
    same = ("value", "items", "details")
    for a in ("dp", "sa"):
        assert {k: part["instances"][0]["results"][a][k] for k in same} == \
               {k: full["instances"][1]["results"][a][k] for k in same}


def test_bad_requests():
    with pytest.raises(ValueError, match="sa.nope"):
        merge_settings({"repeats": 1}, {"nope": 1}, "sa")
    assert merge_settings({"a": 1, "t": {"x": 1, "y": 2}}, {"t": {"y": 3}}, "q") == {"a": 1, "t": {"x": 1, "y": 3}}
    with pytest.raises(DiscoveryError, match="Unknown algorithm"):
        discover_algorithms(["julia"])


@pytest.mark.parametrize("solver", [kp_algo_dp_main, kp_algo_bnb_main, kp_algo_ilp_main])
def test_exact_solvers_p01(solver):
    items, info = solver(V, W, C)
    assert info["value"] == 309 and items == [1, 2, 3, 4, 6]


def test_bnb_node_limit():
    _, info = kp_algo_bnb_main(V, W, C, {"max_nodes": 3})
    assert info["value"] <= 309


def test_mathworks_knapsack2qubo_example():
    Q, c, d, k = q.knapsack2qubo([5, 2, 8, 4, 3], [9, 8, 4, 5, 2], 17, 1)
    assert len(c) == 10 and d == 289 and k == 5
    x = np.array([1, 0, 1, 0, 1, 0, 1, 0, 0, 0], float)   # items 1,3,5 + slack 2
    assert q.energy(Q, c, d, x) == -16


def _opts(seed=1):
    return dict(kp_algo_qubo_config()["tabu"], seed=seed)


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
    assert inst[0].capacity == 285
    assert kp_algo_dp_main(inst[0].values, inst[0].weights, 285)[1]["value"] == 345
