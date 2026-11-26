"""Settings of 'qc' (block cfg["qc"]; port of kp_algo_qc_config.m)."""


def kp_algo_qc_config() -> dict:
    return {
        "penalty": "auto",             # 'auto' = max(values) + 1, or a number
        "tabu": {
            "mode": "slack-optimal",   # 'slack-optimal' (flip item bits, slack bits set optimally)
                                       # or 'all-bits' (plain single-bit-flip tabu on the whole QUBO)
            "restarts": 20,            # independent tabu searches from random starts
            "max_iter_factor": 100,    # iterations per restart = factor * N (N = searched bits)
            "stall_factor": 20,        # stop a restart after factor * N iterations without improvement
            "tenure_min": 10,          # tabu tenure = tenure_min + round(N / 10)
        },
        "qaoa": {                      # used only by the (commented) QAOA call of kp_algo_qc_main
            "layers": 2,               # QAOA depth p (cost + mixer layers)
            "shots": 200,              # states sampled from the final state vector
            "grid": 12,                # grid points per angle in the layer-by-layer search
            "refine": 4,               # rounds of +-h coordinate moves (h halved each round)
            "max_qubits": 20,          # N = items + slack bits; 2**N amplitudes (20 -> ~16 MB)
        },
        "repeats": 1,                  # deterministic and slow: 1 run
    }
