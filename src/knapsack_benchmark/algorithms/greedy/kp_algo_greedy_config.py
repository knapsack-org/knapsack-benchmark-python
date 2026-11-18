"""Default settings of 'greedy' (block cfg["greedy"]; port of kp_algo_greedy_config.m)."""


def kp_algo_greedy_config() -> dict:
    return {
        "repeats": 20,             # very fast: timed many times, median and min reported
    }
