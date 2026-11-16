"""Benchmark adapter of 'qubo_chz' (port of kb_algo_qubo_chz.m).

Independent copy of algo_qubo.py: uses only qubo_chz.py and the settings
cfg["qubo_chz"], so it can be modified without touching 'qubo'. Identical to
'qubo' when created (same model, solver, seeds -> same results).
"""
from __future__ import annotations

import time

from . import qubo_chz as qz


def algo_qubo_chz(v, w, C, acfg, seed):
    """algo_qubo_chz(v, w, C, acfg, seed): acfg = cfg["qubo_chz"], seed = cfg["seed"] + 1000 * k."""
    penalty = qz.penalty_value(v, acfg["penalty"])
    opts = dict(acfg["tabu"], seed=seed + acfg["seed_offset"])

    t = time.perf_counter()
    Q, c, d, slack_bits = qz.knapsack2qubo(v, w, C, penalty)
    t_build = time.perf_counter() - t

    t = time.perf_counter()
    if opts["mode"] == "all-bits":
        x, energy, stats = qz.qubo_tabu(Q, c, d, opts)
    else:
        x, energy, stats = qz.qubo_tabu_slack(v, w, C, penalty, Q, c, d, opts)
    t_solve = time.perf_counter() - t

    t = time.perf_counter()
    sol = qz.decode(x, v, w, C)
    t_decode = time.perf_counter() - t

    return {"label": f"QUBO CHZ + tabu search ({opts['mode']})", "exact": False,
            "proven_optimal": False, "items": sol["final_items"],
            "array_bytes": max(stats.array_bytes, int(Q.nbytes + c.nbytes + 8)),
            "operations": stats.move_evaluations, "operations_unit": "move evaluations",
            "details": {"penalty": penalty, "variables": int(len(c)), "slack_bits": slack_bits,
                        "model_memory_bytes": int(Q.nbytes + c.nbytes + 8),
                        "energy": energy, "iterations": stats.iterations,
                        "raw_items": sol["items"], "raw_value": sol["value"],
                        "raw_weight": sol["weight"],
                        "feasible_before_repair": sol["feasible"], "repaired": sol["repaired"],
                        "build_time_s": t_build, "solve_time_s": t_solve,
                        "decode_time_s": t_decode}}
