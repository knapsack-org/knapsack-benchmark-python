"""Default settings of 'fptas' (block cfg["fptas"]; port of kp_algo_fptas_config.m)."""


def kp_algo_fptas_config() -> dict:
    return {
        "epsilon": 0.1,            # accuracy: value >= (1 - epsilon) * optimum; smaller = slower
        "repeats": 5,              # fast: timed several times, median and min reported
    }
