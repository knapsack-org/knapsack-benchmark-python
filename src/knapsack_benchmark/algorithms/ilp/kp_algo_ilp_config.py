"""Settings of 'ilp' (block cfg["ilp"]; port of kp_algo_ilp_config.m)."""


def kp_algo_ilp_config() -> dict:
    return {
        # Per solve: a hard instance (large, strongly correlated) stops here with its best packing,
        # reported as not proven optimal, instead of blocking the run.
        "time_limit_s": 10,
        "repeats": 3,
    }
