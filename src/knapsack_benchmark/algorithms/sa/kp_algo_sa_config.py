"""Default settings of 'sa' (block cfg["sa"]; port of kp_algo_sa_config.m)."""


def kp_algo_sa_config() -> dict:
    return {
        "penalty": "auto",         # 'auto' = max(values) + 1, or a number
        "restarts": 10,            # independent annealing runs from random starts
        "steps_factor": 500,       # proposals per restart = factor * n
        "t0_factor": 1.0,          # start temperature = factor * max(values)
        "t_end_factor": 0.01,      # end temperature = factor * max(values)
        "repeats": 1,              # randomised and slower: 1 run
    }
