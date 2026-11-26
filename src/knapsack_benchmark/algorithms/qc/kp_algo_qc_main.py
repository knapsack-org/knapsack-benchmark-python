"""0-1 knapsack -> QUBO -> multi-start tabu search -> decoded items (port of kp_algo_qc_main.m).

Today the code of QUBO variant B ('qubo_b'); modules/ also hold qaoa.qaoa (simulated QAOA)
and greedy.greedy (ratio greedy). The commented block below the solve step shows how to call
each of them instead.
"""
from __future__ import annotations

from .modules import qubo as q
# from .modules.qaoa import qaoa        # QAOA (commented call below)
# from .modules.greedy import greedy    # Greedy (commented call below)


def kp_algo_qc_main(v, w, C, acfg, seed, mark=None):
    """kp_algo_qc_main(v, w, C, acfg, seed, mark) -> (items, info).

    acfg = cfg["qc"] (penalty, tabu, qaoa); seed = seed of the random tabu starts;
    mark = optional phase hook, called as mark("build"), mark("solve"), mark("decode")
    at the end of each phase. items are the decoded (and, if needed, repaired) 1-based
    items; info: penalty, variables, slack_bits, model_memory_bytes, energy, mode, the tabu
    statistics (iterations, move_evaluations, working_memory_bytes) and the decoded
    solution info["sol"].
    """
    mark = mark or (lambda name: None)
    penalty = q.penalty_value(v, acfg["penalty"])
    opts = dict(acfg["tabu"], seed=seed)

    Q, c, d, slack_bits = q.knapsack2qubo(v, w, C, penalty)
    mark("build")

    if opts["mode"] == "all-bits":
        x, energy, stats = q.qubo_tabu(Q, c, d, opts)
    else:
        x, energy, stats = q.qubo_tabu_slack(v, w, C, penalty, Q, c, d, opts)
    # Other solvers of modules/ (uncomment one line and its import, comment out the tabu call above):
    # x, energy, stats = q.qubo_tabu_slack(v, w, C, penalty, Q, c, d, opts)   # QUBO: tabu (active above)
    # x, energy, stats = qaoa(Q, c, d, dict(acfg["qaoa"], seed=seed))        # QAOA: needs
    #                    # variables = n + slack bits <= acfg["qaoa"]["max_qubits"] (QaoaTooLarge)
    # return greedy(v, w, C)                                                  # Greedy: no QUBO,
    #                    # no decode; its info has other keys than the details below
    # QAOA and Greedy report other statistics: update kp_algo_qc_output.py (details) and
    # kp_algo_qc_output.schema.json with the switch; tabu.mode is then unused.
    mark("solve")

    sol = q.decode(x, v, w, C)
    mark("decode")

    model_bytes = int(Q.nbytes + c.nbytes + 8)
    return sol["final_items"], {
        "penalty": penalty, "variables": int(len(c)), "slack_bits": slack_bits,
        "model_memory_bytes": model_bytes, "energy": energy, "mode": opts["mode"],
        "iterations": stats.iterations, "move_evaluations": stats.move_evaluations,
        "working_memory_bytes": stats.array_bytes, "sol": sol}
