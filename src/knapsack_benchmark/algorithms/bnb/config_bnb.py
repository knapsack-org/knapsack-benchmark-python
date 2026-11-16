"""Default settings of 'bnb' (block cfg["bnb"]; port of kb_config_bnb.m)."""


def config_bnb() -> dict:
    return {
        "max_nodes": 5_000_000,    # node limit (then the result is not proven optimal)
        "repeats": 1,              # can explode on strongly correlated instances: 1 run
    }
