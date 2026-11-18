"""Settings of 'qubo' (block cfg["qubo"]; port of kp_algo_qubo_config.m)."""


def kp_algo_qubo_config() -> dict:
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
        "repeats": 1,                  # deterministic and slow: 1 run
    }
