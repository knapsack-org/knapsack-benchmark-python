"""0-1 knapsack -> QUBO -> multi-start tabu search -> decoded items (port of kp_algo_qubo_chz_main.m).

Independent copy of 'qubo': uses only its own module (modules/qubo_chz.py) and
settings (cfg["qubo_chz"]), so it can be modified without touching 'qubo'.
"""
from __future__ import annotations

from .modules import qubo_chz as q


def kp_algo_qubo_chz_main(v, w, C, acfg, seed, mark=None):
    """kp_algo_qubo_chz_main(v, w, C, acfg, seed, mark) -> (items, info).

    acfg = cfg["qubo_chz"]; seed = seed of the random tabu starts (plus acfg["seed_offset"]);
    mark = optional phase hook, called as mark("build"), mark("solve"), mark("decode")
    at the end of each phase. items are the decoded (and, if needed, repaired) 1-based
    items; info: penalty, variables, slack_bits, model_memory_bytes, energy, mode, the tabu
    statistics (iterations, move_evaluations, working_memory_bytes) and the decoded
    solution info["sol"].
    """
    mark = mark or (lambda name: None)
    penalty = q.penalty_value(v, acfg["penalty"])
    opts = dict(acfg["tabu"], seed=seed + acfg["seed_offset"])

    Q, c, d, slack_bits = q.knapsack2qubo(v, w, C, penalty)
    mark("build")

    if opts["mode"] == "all-bits":
        x, energy, stats = q.qubo_tabu(Q, c, d, opts)
    else:
        x, energy, stats = q.qubo_tabu_slack(v, w, C, penalty, Q, c, d, opts)
    mark("solve")

    sol = q.decode(x, v, w, C)
    mark("decode")

    model_bytes = int(Q.nbytes + c.nbytes + 8)
    return sol["final_items"], {
        "penalty": penalty, "variables": int(len(c)), "slack_bits": slack_bits,
        "model_memory_bytes": model_bytes, "energy": energy, "mode": opts["mode"],
        "iterations": stats.iterations, "move_evaluations": stats.move_evaluations,
        "working_memory_bytes": stats.array_bytes, "sol": sol}
