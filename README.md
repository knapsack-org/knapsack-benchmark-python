# knapsack-benchmark-python

Python version of [`knapsack-benchmark-matlab`](../knapsack-benchmark-matlab): the same benchmark of five 0-1 knapsack algorithms, on the same 100 generated instances, with the same JSON output structure.

| Key | Algorithm | Type | Module |
|---|---|---|---|
| `dp` | Dynamic programming 0-1 | exact (reference optimum) | `algorithms/dp/dp.py`, NumPy row-by-row table, O(n·C) |
| `bnb` | Branch and bound | exact | `algorithms/bnb/bnb.py`, depth-first, Dantzig (LP) bound, greedy start |
| `ilp` | Integer linear programming | exact | `algorithms/ilp/ilp.py`, `scipy.optimize.milp` (HiGHS, same engine as MATLAB `intlinprog`) |
| `qubo` | QUBO + tabu search | heuristic | `algorithms/qubo/qubo.py` |
| `qubo_chz` | QUBO CHZ: independent copy of `qubo` | heuristic | `algorithms/qubo_chz/qubo_chz.py`, own settings `qubo_chz` |

Every algorithm is run on each instance and measured on **quality** (value, items, feasibility, gap to the DP optimum, proven optimality) and **execution cost** (wall time, CPU time, working memory, process memory, operations). Output: `./output/run-dd-mm-yy-hh-mm.json`.

## Install

Python ≥ 3.10.

```
cd knapsack-benchmark-python
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -e ".[memory,test]"   # numpy, scipy (+ psutil for process memory, pytest)
```

## Run

```
knapsack-benchmark                       # or: python -m knapsack_benchmark
```

About 45 s for the 100 instances (most of it is the two QUBO tabu searches).

Options:

```
knapsack-benchmark -n 10                                  # number of instances
knapsack-benchmark -a dp,bnb,ilp                          # subset of algorithms
knapsack-benchmark --seed 7 -o results/                   # other seed / output folder
knapsack-benchmark --set qubo_chz.tabu.restarts=50        # any option (dotted key = JSON value), repeatable
knapsack-benchmark --set bnb.max_nodes=100000 --set bnb.repeats=3
knapsack-benchmark --config my_options.json               # overrides from a JSON file
knapsack-benchmark --trace-memory                         # + tracemalloc peak (slow, ~6x)
knapsack-benchmark -q                                     # no console output
```

From Python:

```python
from knapsack_benchmark import run_benchmark
res = run_benchmark({"instances": {"count": 10}, "qubo_chz": {"tabu": {"restarts": 50}}})
print(res["summary"]["algorithms"]["qubo_chz"]["mean_gap_percent"], res["output_file"])
```

Tests (`tests/test_p01.py`: P01 = 309 for DP, B&B, ILP; MathWorks `knapsack2qubo` example; tabu searches; slack encoding; `qubo_chz` = `qubo`. `tests/test_parity.py`: identical results to the Octave run):

```
pytest                     # all (≈ 50 s)
pytest -m "not slow"       # without the full 100-instance run (≈ 3 s)
```

## Project layout

```
knapsack-benchmark-python/
├── pyproject.toml             package "knapsack-benchmark", CLI "knapsack-benchmark"
├── src/knapsack_benchmark/
│   ├── cli.py                 command line
│   ├── benchmark.py           run_benchmark: generate → run each algorithm (measured) → compare → JSON
│   ├── config.py              all parameters (same keys and defaults as benchmark_config.m)
│   ├── helpers/
│   │   ├── check_algorithms.py    validate the requested algorithm ids
│   │   ├── run_algorithm.py       run one algorithm with its repeats → result + cost
│   │   ├── add_ratios_vs_dp.py    cost ratios to dp
│   │   ├── summary.py             per-algorithm / per-family summary
│   │   ├── write_json.py          JSON output
│   │   ├── printing.py            console output
│   │   ├── rng.py             Park–Miller generator (same numbers as kb_lcg.m)
│   │   └── measure.py         time / CPU / memory measurement
│   ├── instances/
│   │   ├── instances.py       100 reproducible instances (Pisinger families)
│   │   └── config_instances.py    generator settings (block cfg["instances"])
│   └── algorithms/            one subpackage per algorithm (+ config_<id>.py settings, algo_<id>.py adapter), same layout as the MATLAB src/algorithms/
│       ├── dp/dp.py           dynamic programming 0-1
│       ├── bnb/bnb.py         branch and bound
│       ├── ilp/ilp.py         integer linear programming (scipy milp / HiGHS)
│       ├── qubo/qubo.py       knapsack → QUBO, tabu searches, decode, slack encoding
│       └── qubo_chz/qubo_chz.py   independent copy of qubo.py, to be modified separately
├── tests/test_p01.py, tests/test_parity.py
└── output/                    run-dd-mm-yy-hh-mm.json files (git-ignored)
```

## Correspondence with the MATLAB/Octave project

| MATLAB / Octave | Python |
|---|---|
| `run_benchmark.m` | `benchmark.run_benchmark`, CLI `knapsack-benchmark` |
| `benchmark_config.m` | `config.benchmark_config` (same keys) |
| `kb_generate_instances.m`, `kb_lcg.m`, `kb_randi.m`, `kb_seed.m` | `instances/instances.py`, `helpers/rng.py` |
| `kb_knapsack_dp.m` | `algorithms.dp.dp.knapsack_dp` |
| `kb_knapsack_bnb.m` | `algorithms.bnb.bnb.knapsack_bnb` |
| `kb_knapsack_ilp.m` (glpk / intlinprog) | `algorithms.ilp.ilp.knapsack_ilp` (scipy `milp`, HiGHS) |
| `kb_knapsack2qubo.m`, `kb_qubo_tabu_slack.m`, `kb_qubo_tabu.m`, `kb_decode.m`, `kb_encode_slack.m` | `algorithms/qubo/qubo.py` |
| `kb_chz_*.m` | `algorithms/qubo_chz/qubo_chz.py` |
| `whos` working memory | `nbytes` of the algorithm's arrays |
| `memory()` process memory | `psutil` RSS (optional) |
| `tic`/`toc`, `cputime` | `time.perf_counter`, `time.process_time` |

Item indices in the JSON are **1-based**, as in the MATLAB version, so both outputs can be compared directly.

## Parity with the Octave run

Checked against the Octave 11.3 run of the MATLAB project (`run-14-11-26-14-00.json`, 100 instances, seed 2026):

- **identical instances** (weights, values, capacities);
- **DP, B&B, QUBO, QUBO CHZ: identical results** on all 100 instances: values, items, B&B node counts, tabu iteration counts, QUBO energies;
- **ILP: identical optimal values**; on 30 instances with several optimal packings, HiGHS (Python) and GLPK (Octave) return different, equally optimal, item sets.

| | Optimal | Mean gap | Max gap |
|---|---|---|---|
| `dp`, `bnb`, `ilp` | 100 / 100 | 0 % | 0 % |
| `qubo`, `qubo_chz` | 44 / 100 | 1.02 % | 4.80 % |

## Execution cost: Python vs Octave (same 100 instances)

Median per instance, measured on different machines (Python in a Linux container, Octave 11.3 on Windows): use the orders of magnitude, not the exact ratios.

| Algorithm | Python median time | Octave median time | Python working memory | Octave working memory |
|---|---|---|---|---|
| `dp` | 0.21 ms | 2.7 ms | 171 kB | 171 kB |
| `bnb` | 0.50 ms | 6.0 ms | 2.1 kB | 2.3 kB |
| `ilp` | 12.6 ms (HiGHS) | 1.6 ms (GLPK) | 0.9 kB | 0.9 kB |
| `qubo` / `qubo_chz` | 0.19 s | 0.64 s | 15 kB | 15 kB |
| Total run | 45 s | 153 s | | |

GLPK through Octave is faster than HiGHS through SciPy on these tiny problems (HiGHS has a larger fixed set-up cost); the other algorithms run faster in Python/NumPy than in Octave.

## Cost measures

Each algorithm result has a `cost` object (same fields as the MATLAB version):

| Field | Meaning |
|---|---|
| `wall_time_s` / `wall_time_min_s` | median / fastest wall-clock time over the repeats (`perf_counter`). Repeats: dp 5, bnb 1, ilp 3, qubo 1, qubo_chz 1 (`timing.repeats_*`) |
| `cpu_time_s` | CPU time per run (`process_time`) |
| `working_memory_bytes` | bytes of the algorithm's own NumPy arrays (DP table; B&B vectors; ILP problem data, not the solver's internal memory; QUBO Q, c and search vectors). Same idea as `whos` in MATLAB, so the two versions are comparable |
| `traced_peak_memory_bytes` | only with `--trace-memory`: peak allocated by Python + NumPy during an extra untimed run (`tracemalloc`) |
| `process_memory_before/after/delta_bytes` | process RSS from `psutil` (optional), `null` without it. Process-wide snapshot: indicative only |
| `operations` + `operations_unit` | dp: table cells · bnb: nodes · ilp: HiGHS B&B nodes · qubo, qubo_chz: move evaluations |

plus `cost_ratio_vs_dp` (`time`, `cpu`, `memory`; > 1 means costlier than DP). The `summary` has per-algorithm statistics, a `by_family` breakdown and `ranking_by_median_time`. The JSON structure is described in the MATLAB project's README, including `schema_version` (currently 2, same value in both projects; increased on any breaking change of the structure); the Python output adds `environment.numpy` / `environment.scipy`, `details.mip_gap` for ILP and `cost.traced_peak_memory_bytes`.

## Method

Same as the MATLAB project (see its README): Pisinger instance families with sizes 10 → 48 items; DP table; depth-first branch and bound with the Dantzig bound; ILP max v'x s.t. w'x ≤ C, x binary; QUBO f = −Σvᵢxᵢ + P(Σwᵢxᵢ + s − C)² with binary-encoded slack and P = max(v) + 1, solved by a multi-start tabu search on the item bits with optimal slack bits.

**QUBO CHZ (`qubo_chz`).** `qubo_chz.py` is an independent copy of `qubo.py` with its own settings block (`qubo_chz.penalty`, `qubo_chz.seed_offset`, `qubo_chz.tabu`). Identical to `qubo` when created; modify it to experiment without affecting `qubo` (the test `test_qubo_chz_matches_qubo` will then fail on purpose: adjust or remove it).
