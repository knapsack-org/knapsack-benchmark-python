# knapsack-benchmark-python

Python version of [`knapsack-benchmark-matlab`](../knapsack-benchmark-matlab): the same benchmark of nine 0-1 knapsack algorithms (`bnb`, `dp`, `fptas`, `ga`, `greedy`, `ilp`, `ising`, `qubo`, `sa`; the table lists the first five), on the same generated instances, with the same raw output (ADR 0014).

| Key | Algorithm | Type | Module |
|---|---|---|---|
| `bnb` | Branch and bound | exact | `algorithms/bnb/kp_algo_bnb_main.py`, depth-first, Dantzig (LP) bound, greedy start |
| `dp` | Dynamic programming 0-1 | exact (reference optimum) | `algorithms/dp/kp_algo_dp_main.py`, NumPy row-by-row table, O(n·C) |
| `ilp` | Integer linear programming | exact | `algorithms/ilp/kp_algo_ilp_main.py`, `scipy.optimize.milp` (HiGHS, same engine as MATLAB `intlinprog`) |
| `qubo` | QUBO + tabu search | heuristic | `algorithms/qubo/kp_algo_qubo_main.py` (module `modules/qubo.py`) |

The algorithms are found by scanning `algorithms/` (one package per algorithm, see [Adding an algorithm](#adding-an-algorithm)) and run in alphabetical order. Every algorithm is run on each instance and measured on **quality** (value, items, feasibility, gap to the optimum of the reference algorithm `dp`, proven optimality) and **execution cost** (wall time, CPU time, working memory, process memory, operations). Output: the raw results `raw.json` (and `instances.json`) in `./output/run-dd-mm-yy-hh-mm/`; the run file (`schema_version` 4: optimum, gaps, ratios, summary) is built from them by `knapsack-output` in [knapsack-server](https://github.com/knapsack-org/knapsack-server).

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
knapsack-benchmark [--request req.json] [--instances inst.json] [--out DIR]   # or: python -m knapsack_benchmark ...
knapsack-benchmark --describe        # algorithms, default settings and JSON Schemas as JSON (catalog)
```

| Option | Meaning |
|---|---|
| `--request` | run request JSON (knapsack-server `RunRequest`): `seed`, `instances` (`count`, `min_items`, `max_items`, `max_coefficient`, `capacity_ratio`), `algorithms` (ids; the reference `dp` is always added), `algorithm_config` (`{<id>: partial settings}`, merged into the defaults; an unknown key is an error). Absent fields come from the settings files; `environments` is ignored |
| `--instances` | instance set JSON (`format: "knapsack-instances"`, the `instances.json` of an earlier run or a knapsack-server shard) used instead of the generator; the per-instance seed stays `seed + 1000 * id` with the file's global ids |
| `--out` | output directory (default `output/run-dd-mm-yy-hh-mm/`) |

Output: `raw.json` (`format: "knapsack-raw"`, `format_version` 1: algorithm entries and schemas, parameters, raw results per instance without `is_optimal`, `gap_percent`, `cost_ratio_vs_reference`) and, without `--instances`, `instances.json`. stdout has one line per instance plus progress lines `@@progress {"instance":<id>,"algorithm":"<id>","event":"start"|"done"}` before and after each algorithm. A full run file: `pnpm -C <knapsack-server> knapsack-output <out dir>`.

The settings files: `config.py` (master seed, `timing.trace_memory` for the tracemalloc peak), `instances/config_instances.py` (number and size of instances) and `algorithms/<id>/kp_algo_<id>_config.py` (settings of one algorithm, e.g. `bnb.max_nodes`, `qubo.tabu.mode`).

From Python: `from knapsack_benchmark import run_benchmark; raw = run_benchmark(request, instances_file, out_dir)` (all optional; returns the raw dict, with `output_dir`).

Tests (`tests/test_p01.py`: every discovered algorithm on P01 through its adapter, keys checked against its schema file; `--describe`; request, `--instances` and shard (global seeds) round trip; P01 = 309 for DP, B&B, ILP; MathWorks `knapsack2qubo` example; tabu searches; slack encoding. `tests/test_parity.py`: identical results to the Octave run; the slow test runs the CLI with `bnb`, `ilp`, `qubo` on the 100 instances into a temporary folder):

```
pytest                     # all (≈ 75 s)
pytest -m "not slow"       # without the 100-instance run (≈ 8 s)
```

## Project layout

```
knapsack-benchmark-python/
├── pyproject.toml             package "knapsack-benchmark", CLI "knapsack-benchmark"
├── src/knapsack_benchmark/
│   ├── cli.py                 command line (--request, --instances, --out, --describe)
│   ├── benchmark.py           run_benchmark(): discover → generate or read instances → run each algorithm (measured) → raw.json
│   ├── config.py              master seed + settings collected from instances/ and algorithms/<id>, request overrides (same keys as benchmark_config.m)
│   ├── helpers/               generic code, no algorithm names
│   │   ├── discover.py            scan algorithms/, check the folder contract, reference, availability, request filter, schema files
│   │   ├── run_algorithm.py       run one algorithm with its repeats → raw result + cost
│   │   ├── phase_timer.py         phase timer passed to kp_algo_<id>_main as mark
│   │   ├── write_json.py          JSON output
│   │   ├── printing.py            console output, progress lines
│   │   ├── rng.py             Park–Miller generator (same numbers as kb_lcg.m)
│   │   └── measure.py         time / CPU / memory measurement
│   ├── instances/
│   │   ├── instances.py       100 reproducible instances (Pisinger families)
│   │   └── config_instances.py    generator settings (block cfg["instances"])
│   └── algorithms/            one self-contained package per algorithm, same layout as the MATLAB src/algorithms/
│       ├── bnb/               kp_algo_bnb_{loader,main,config,output}.py: branch and bound
│       ├── dp/                kp_algo_dp_*.py: dynamic programming 0-1 (reference)
│       ├── ilp/               kp_algo_ilp_*.py: integer linear programming (scipy milp / HiGHS)
│       └── qubo/              kp_algo_qubo_*.py + modules/qubo.py: knapsack → QUBO, tabu searches, decode, slack encoding
├── tests/test_p01.py, tests/test_parity.py
└── output/                    run-dd-mm-yy-hh-mm/ folders (git-ignored)
```

## Adding an algorithm

Everything about an algorithm lives in `algorithms/<id>/` (`<id>` matches `[a-z][a-z0-9_]*`; the folder is a package with `__init__.py`); nothing else is edited. Copy the package of a similar algorithm, rename its files and functions, and adapt:

| File | Role |
|---|---|
| `kp_algo_<id>_loader.py` | `kp_algo_<id>_loader()` → dict: `id` (= folder name), `label` (capitalised words, e.g. `Branch and Bound (Dantzig Bound, Depth-First)`), `description` (one or two sentences, written to its `algorithms[]` entry), `short_label` (Knapview chip), `exact`, `reference` (exactly one algorithm, `dp`), `available` (callable; False → skipped with a warning), `environment` (callable → dict written to `environment.algorithms.<id>`) |
| `kp_algo_<id>_main.py` | the maths: `kp_algo_<id>_main(v, w, C, acfg, seed, mark=None)` → `(items, info)`; `mark("phase")` (optional) ends a timed phase |
| `kp_algo_<id>_config.py` | `kp_algo_<id>_config()` → settings block `cfg[<id>]`, always with `repeats` |
| `kp_algo_<id>_output.py` | `run(v, w, C, acfg, seed)` (calls `_main`, times its phases with `helpers.phase_timer`, returns the common result) and `entry(acfg, env)` (its `algorithms[]` entry) |
| `kp_algo_<id>_output.schema.json` | JSON Schema 2020-12 of its `entry` (with `config` as an object), `config` and `details`; byte-identical to the MATLAB file (knapsack-server `scripts/check-schemas.mjs`), checked by knapsack-server's output formatter |
| `modules/` | helper modules of `_main` (optional, with `__init__.py`) |

Algorithms may import `helpers/` but never another algorithm's package: shared code is copied. `discover_algorithms` stops with `DiscoveryError` on a missing contract file or an id that differs from the folder name. See also `documentation/implementation/adding-an-algorithm.md`.

## Correspondence with the MATLAB/Octave project

| MATLAB / Octave | Python |
|---|---|
| `run_benchmark.m` | `benchmark.run_benchmark`, CLI `knapsack-benchmark` |
| `kb_discover_algorithms.m`, `kb_phase_timer.m`, `kb_print_progress.m` | `helpers/discover.py`, `helpers/phase_timer.py`, `helpers/printing.py` |
| `benchmark_config.m` | `config.benchmark_config` (same keys) |
| `kb_generate_instances.m`, `kb_lcg.m`, `kb_randi.m`, `kb_seed.m` | `instances/instances.py`, `helpers/rng.py` |
| `algorithms/<id>/kp_algo_<id>_{loader,main,config,output}.m` | `algorithms/<id>/kp_algo_<id>_{loader,main,config,output}.py` (same names) |
| `kp_algo_ilp_main.m` (glpk / intlinprog) | `kp_algo_ilp_main.py` (scipy `milp`, HiGHS) |
| `qubo/modules/kb_*.m` (6 files) | `qubo/modules/qubo.py` |
| `whos` working memory | `nbytes` of the algorithm's arrays |
| `memory()` process memory | `psutil` RSS (optional) |
| `tic`/`toc`, `cputime` | `time.perf_counter`, `time.process_time` |

Item indices in the JSON are **1-based**, as in the MATLAB version, so both outputs can be compared directly.

## Parity with the Octave run

Checked against the Octave 11.3 run of the MATLAB project (100 instances, seed 2026; unchanged in the v2 run `run-16-11-26-16-38.json` and the v3 run `run-18-11-26-19-12.json`):

- **identical instances** (weights, values, capacities);
- **DP, B&B, QUBO: identical results** on all 100 instances: values, items, B&B node counts, tabu iteration counts, QUBO energies;
- **ILP: identical optimal values**; on 30 instances with several optimal packings, HiGHS (Python) and GLPK (Octave) return different, equally optimal, item sets.

| | Optimal | Mean gap | Max gap |
|---|---|---|---|
| `dp`, `bnb`, `ilp` | 100 / 100 | 0 % | 0 % |
| `qubo` | 44 / 100 | 1.02 % | 4.80 % |

## Execution cost: Python vs Octave (same 100 instances)

Median per instance, measured on different machines (Python in a Linux container, Octave 11.3 on Windows): use the orders of magnitude, not the exact ratios.

| Algorithm | Python median time | Octave median time | Python working memory | Octave working memory |
|---|---|---|---|---|
| `dp` | 0.21 ms | 2.7 ms | 171 kB | 171 kB |
| `bnb` | 0.50 ms | 6.0 ms | 2.1 kB | 2.3 kB |
| `ilp` | 12.6 ms (HiGHS) | 1.6 ms (GLPK) | 0.9 kB | 0.9 kB |
| `qubo` | 0.19 s | 0.64 s | 15 kB | 15 kB |
| Total run | 45 s | 153 s | | |

GLPK through Octave is faster than HiGHS through SciPy on these tiny problems (HiGHS has a larger fixed set-up cost); the other algorithms run faster in Python/NumPy than in Octave. The Octave `qubo` times predate the phase-3 speed-ups (about 3× faster since, same results).

## Cost measures

Each algorithm result has a `cost` object (same fields as the MATLAB version):

| Field | Meaning |
|---|---|
| `wall_time_s` / `wall_time_min_s` | median / fastest wall-clock time over the repeats (`perf_counter`). Repeats: dp 5, bnb 1, ilp 3, qubo 1 (`repeats` in `kp_algo_<id>_config.py`) |
| `cpu_time_s` | CPU time per run (`process_time`) |
| `working_memory_bytes` | bytes of the algorithm's own NumPy arrays (DP table; B&B vectors; ILP problem data, not the solver's internal memory; QUBO Q, c and search vectors). Same idea as `whos` in MATLAB, so the two versions are comparable |
| `traced_peak_memory_bytes` | only with `timing.trace_memory = True` in `config.py`: peak allocated by Python + NumPy during an extra untimed run (`tracemalloc`) |
| `process_memory_before/after/delta_bytes` | process RSS from `psutil` (optional), `null` without it. Process-wide snapshot: indicative only |
| `operations` + `operations_unit` | dp: table cells · bnb: nodes · ilp: HiGHS B&B nodes · qubo: move evaluations |

`cost_ratio_vs_reference` (`time`, `cpu`, `memory`; > 1 means costlier than the reference algorithm `dp`) and the `summary` (per-algorithm statistics, a `by_family` breakdown, `ranking_by_median_time`) are computed by knapsack-server's `knapsack-output` from `raw.json`; the run file format (`schema_version` 4) is described in the `documentation` repo (`functional/output-format.md`). The Python output adds `environment.numpy` / `environment.scipy`, `details.mip_gap` for ILP and `cost.traced_peak_memory_bytes`.

## Method

Same as the MATLAB project (see its README): Pisinger instance families with sizes 10 → 48 items; DP table; depth-first branch and bound with the Dantzig bound; ILP max v'x s.t. w'x ≤ C, x binary; QUBO f = −Σvᵢxᵢ + P(Σwᵢxᵢ + s − C)² with binary-encoded slack and P = max(v) + 1, solved by a multi-start tabu search on the item bits with optimal slack bits.
