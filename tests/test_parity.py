"""Parity with the MATLAB/Octave project: same instances and same results.

Expected values come from the Octave 11.3 run of knapsack-benchmark-matlab
(100 instances, seed 2026, 5 algorithms; unchanged in the v2 run run-16-11-26-16-38.json
and the v3 run run-18-11-26-19-12.json).
DP, B&B, QUBO and QUBO CHZ match it exactly (values, items, B&B nodes, tabu
iterations, energies); ILP matches on values (HiGHS and GLPK may return a
different optimal item set when several optima exist).
"""
import pytest

from pathlib import Path

from knapsack_benchmark.algorithms.bnb.kp_algo_bnb_main import kp_algo_bnb_main
from knapsack_benchmark.algorithms.dp.kp_algo_dp_main import kp_algo_dp_main
from knapsack_benchmark.instances.instances import generate_instances
from knapsack_benchmark.benchmark import run_benchmark

# QUBO final values of the 100 instances (Octave reference runs)
QUBO_100 = [345, 218, 369, 476, 315, 378, 495, 275, 484, 489, 397, 394, 568, 429, 437, 709, 506, 650,
    571, 436, 679, 782, 547, 580, 765, 589, 477, 751, 603, 622, 780, 514, 655, 903, 698,
    759, 930, 627, 786, 1028, 611, 745, 1042, 754, 825, 1071, 745, 788, 942, 684, 925,
    1327, 824, 989, 1240, 912, 930, 1169, 855, 979, 1531, 948, 960, 1351, 990, 1169, 1393,
    1246, 1119, 1223, 927, 1026, 1553, 937, 1310, 1597, 1077, 1378, 1578, 1061, 1231,
    1774, 1002, 1374, 1739, 1177, 1209, 1629, 1204, 1190, 1566, 1181, 1412, 1943, 1243,
    1584, 1980, 1221, 1541, 1863]


def test_bnb_nodes_and_optimum():
    inst = generate_instances(100, 2026, 10, 48, 100, 0.5)
    nodes = []
    for i in inst:
        opt = kp_algo_dp_main(i.values, i.weights, i.capacity)[1]["value"]
        _, info = kp_algo_bnb_main(i.values, i.weights, i.capacity)
        assert info["value"] == opt and info["proven_optimal"]
        nodes.append(info["nodes"])
    assert sum(nodes) == 489151 and max(nodes) == 284157 == nodes[95]   # same as Octave


@pytest.mark.slow
def test_full_run_matches_octave():
    res = run_benchmark()                 # writes output/run-*.json, removed below
    Path(res["output_file"]).unlink()
    assert res["schema_version"] == 3 and res["reference_algorithm"] == "dp"
    ids = [a["id"] for a in res["algorithms"]]
    assert ids == sorted(ids) and {"bnb", "dp", "ilp", "qubo", "qubo_chz"} <= set(ids)
    s = res["summary"]["algorithms"]
    for a in ("dp", "bnb", "ilp"):
        assert s[a]["num_optimal"] == 100
    for a in ("qubo", "qubo_chz"):
        assert s[a]["num_optimal"] == 44
        assert s[a]["num_feasible"] == 100
        assert abs(s[a]["mean_gap_percent"] - 1.0215814662272313) < 1e-9
    for a in ("qubo", "qubo_chz"):
        assert [r["results"][a]["value"] for r in res["instances"]] == QUBO_100
    for r in res["instances"]:
        assert r["results"]["ilp"]["value"] == r["optimum"]
