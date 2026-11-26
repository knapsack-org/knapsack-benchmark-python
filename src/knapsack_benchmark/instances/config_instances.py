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
        "correlation": {
            # rotated in this order
            "families": ["uncorrelated", "weakly_correlated", "strongly_correlated"],
            "weak_noise_ratio": 0.1,       # weakly:   v = max(w + U(-k, k), 1),  k = floor(ratio * R)
            "strong_offset_ratio": 0.1,    # strongly: v = w + floor(ratio * R)
        },
    }
