"""0-1 knapsack -> Ising Hamiltonian -> spin annealing -> decoded items (port of kp_algo_ising_main.m)."""
from __future__ import annotations

import numpy as np

from .modules.ising import decode, ising_anneal, knapsack2ising, penalty_value


def kp_algo_ising_main(v, w, C, acfg, seed, mark=None) -> tuple[list[int], dict]:
    """kp_algo_ising_main(v, w, C, acfg, seed, mark): acfg = cfg["ising"], seed = cfg["seed"] + 1000 * k;
    ``mark`` is the optional phase hook, called as mark("build"), mark("solve"), mark("decode").

    Returns the decoded (and, if needed, repaired) 1-based items and an info dict: penalty, variables,
    slack_bits, model_memory_bytes, energy (best H), proposals, accepted, working_memory_bytes, sol (the
    decoded solution of ``decode``).
    """
    mark = mark or (lambda name: None)
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    penalty = penalty_value(v, acfg["penalty"])

    J, h, E0, slack_bits = knapsack2ising(v, w, C, penalty)
    mark("build")

    s, energy, stats = ising_anneal(J, h, E0, acfg, seed, penalty * float(w.max()))
    mark("solve")

    sol = decode(s, v, w, C)
    mark("decode")

    model_bytes = int(J.nbytes + h.nbytes + 8)
    return sol["final_items"], {
        "penalty": penalty, "variables": int(h.size), "slack_bits": slack_bits,
        "model_memory_bytes": model_bytes, "energy": float(energy),
        "proposals": stats["proposals"], "accepted": stats["accepted"],
        "working_memory_bytes": model_bytes + int(2 * h.nbytes), "sol": sol}
