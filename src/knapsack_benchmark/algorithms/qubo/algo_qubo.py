"""Benchmark adapter of 'qubo' (port of kb_algo_qubo.m): build the QUBO, run the tabu search, decode."""
from __future__ import annotations

import time

from . import qubo as q


def algo_qubo(v, w, C, acfg, seed):
    """algo_qubo(v, w, C, acfg, seed): acfg = cfg["qubo"], seed = cfg["seed"] + 1000 * k."""
    penalty = q.penalty_value(v, acfg["penalty"])
    opts = dict(acfg["tabu"], seed=seed)

    t = time.perf_counter()
    Q, c, d, slack_bits = q.knapsack2qubo(v, w, C, penalty)
    t_build = time.perf_counter() - t

    t = time.perf_counter()
    if opts["mode"] == "all-bits":
        x, energy, stats = q.qubo_tabu(Q, c, d, opts)
    else:
        x, energy, stats = q.qubo_tabu_slack(v, w, C, penalty, Q, c, d, opts)
    t_solve = time.perf_counter() - t

    t = time.perf_counter()
    sol = q.decode(x, v, w, C)
    t_decode = time.perf_counter() - t

    return {"label": f"QUBO + tabu search ({opts['mode']})", "exact": False,
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
