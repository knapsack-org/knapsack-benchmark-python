"""Default settings of 'dp' (block cfg["dp"]; port of kb_config_dp.m)."""


def config_dp() -> dict:
    return {
        "repeats": 5,              # fast: timed several times, median and min reported
    }
