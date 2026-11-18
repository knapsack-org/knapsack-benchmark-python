"""Benchmark adapter and JSON description of 'ga' (port of kp_algo_ga_output.m)."""
from __future__ import annotations

from .kp_algo_ga_loader import kp_algo_ga_loader
from .kp_algo_ga_main import kp_algo_ga_main

_LABEL = kp_algo_ga_loader()["label"]


def run(v, w, C, acfg, seed) -> dict:
    """Run kp_algo_ga_main, return the common result dict."""
    items, info = kp_algo_ga_main(v, w, C, acfg, seed)
    return {"label": _LABEL, "exact": False, "proven_optimal": False, "items": items,
            "working_memory_bytes": info["working_memory_bytes"],
            "operations": info["evaluations"], "operations_unit": "fitness evaluations",
            "details": {"evaluations": info["evaluations"], "generations": info["generations"]}}


def entry(acfg, env=None) -> dict:
    """Entry of the JSON "algorithms" array."""
    L = kp_algo_ga_loader()
    return {"id": L["id"], "label": _LABEL, "description": L["description"],
            "short_label": L["short_label"], "exact": L["exact"],
            "reference": L["reference"], "config": acfg}


SCHEMA = {
    "entry": {
        "type": "object", "additionalProperties": False,
        "required": ["id", "label", "description", "short_label", "exact", "reference", "config"],
        "properties": {
            "id": {"enum": ["ga"]}, "label": {"type": "string"}, "description": {"type": "string"},
            "short_label": {"type": "string"},
            "exact": {"type": "boolean"}, "reference": {"type": "boolean"},
            "config": {
                "type": "object", "additionalProperties": False,
                "required": ["pop_size", "generations", "tournament", "crossover_rate",
                             "mutation_factor", "repeats"],
                "properties": {"pop_size": {"type": "integer", "minimum": 2},
                               "generations": {"type": "integer", "minimum": 0},
                               "tournament": {"type": "integer", "minimum": 1},
                               "crossover_rate": {"type": "number", "minimum": 0},
                               "mutation_factor": {"type": "number", "minimum": 0},
                               "repeats": {"type": "integer", "minimum": 1}}}}},
    "details": {
        "type": "object", "additionalProperties": False,
        "required": ["evaluations", "generations"],
        "properties": {"evaluations": {"type": "integer", "minimum": 0},
                       "generations": {"type": "integer", "minimum": 0}}}}
