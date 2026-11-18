"""Settings of 'qubo_chz' (block cfg["qubo_chz"]; port of kp_algo_qubo_chz_config.m).

Own copy of the qubo settings (same values when created), so qubo_chz can be
tuned without touching qubo.
"""


def kp_algo_qubo_chz_config() -> dict:
    return {
        "penalty": "auto",
        "seed_offset": 0,              # added to the tabu seed: 0 -> same random starts as qubo
        "tabu": {
            "mode": "slack-optimal",
            "restarts": 20,
            "max_iter_factor": 100,
            "stall_factor": 20,
            "tenure_min": 10,
        },
        "repeats": 1,
    }
