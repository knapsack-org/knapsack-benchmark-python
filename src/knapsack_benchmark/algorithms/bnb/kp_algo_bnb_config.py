"""Settings of 'bnb' (block cfg["bnb"]; port of kp_algo_bnb_config.m)."""


def kp_algo_bnb_config() -> dict:
    return {
        "max_nodes": 5_000_000,    # node limit (then the result is not proven optimal)
        "repeats": 1,              # can explode on strongly correlated instances: 1 run
    }
