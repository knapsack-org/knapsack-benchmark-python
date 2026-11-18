"""Default settings of 'ga' (block cfg["ga"]; port of kp_algo_ga_config.m)."""


def kp_algo_ga_config() -> dict:
    return {
        "pop_size": 30,            # individuals per generation (one elite kept)
        "generations": 50,         # generations after the random start
        "tournament": 2,           # individuals drawn per parent selection
        "crossover_rate": 0.9,     # probability of uniform crossover (else copy of parent 1)
        "mutation_factor": 1.0,    # per-bit flip probability = factor / n
        "repeats": 1,              # randomised and slower: 1 run
    }
