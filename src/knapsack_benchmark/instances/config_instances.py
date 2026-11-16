"""Default settings of the instance generator (block cfg["instances"]; port of kb_config_instances.m).

Used by ``generate_instances`` with the master seed ``cfg["seed"]``.
"""


def config_instances() -> dict:
    return {
        "count": 100,              # number of generated knapsack instances
        "min_items": 10,           # smallest instance (number of items)
        "max_items": 48,           # largest instance
        "max_coefficient": 100,    # weights in 1..R (values depend on the family)
        "capacity_ratio": 0.5,     # capacity = floor(ratio * sum(weights))
    }
