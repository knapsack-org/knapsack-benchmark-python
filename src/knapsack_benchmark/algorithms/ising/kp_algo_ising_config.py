"""Default settings of 'ising' (block cfg["ising"]; port of kp_algo_ising_config.m)."""


def kp_algo_ising_config() -> dict:
    return {
        "penalty": "auto",         # 'auto' = max(values) + 1, or a number
        "restarts": 5,             # independent annealing runs from random spins
        "steps_factor": 2000,      # proposals per restart = factor * N (N = items + slack spins)
        "t0_factor": 100.0,        # start temperature = factor * P * max(weights)
        "t_end_factor": 1.0,       # end temperature = factor * P * max(weights)
        "repeats": 1,              # randomised and slower: 1 run
    }
