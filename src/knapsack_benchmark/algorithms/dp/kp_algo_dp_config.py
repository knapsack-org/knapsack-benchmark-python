"""Settings of 'dp' (block cfg["dp"]; port of kp_algo_dp_config.m)."""


def kp_algo_dp_config() -> dict:
    return {
        "repeats": 5,              # fast: timed several times, median and min reported
    }
