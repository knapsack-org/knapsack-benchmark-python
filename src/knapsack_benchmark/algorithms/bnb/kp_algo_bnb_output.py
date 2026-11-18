"""Benchmark adapter and JSON description of 'bnb' (port of kp_algo_bnb_output.m).

run(v, w, C, acfg, seed)  runs kp_algo_bnb_main, returns the common result dict
entry(acfg, env)          entry of the JSON "algorithms" array
SCHEMA                    JSON Schema of that entry ("entry") and of results.bnb.details ("details")
"""
from __future__ import annotations

from .kp_algo_bnb_loader import kp_algo_bnb_loader
from .kp_algo_bnb_main import kp_algo_bnb_main


def run(v, w, C, acfg, seed):
    items, info = kp_algo_bnb_main(v, w, C, acfg, seed)
    return {"label": kp_algo_bnb_loader()["label"], "exact": True,
            "proven_optimal": info["proven_optimal"], "items": items,
            "working_memory_bytes": info["working_memory_bytes"],
            "operations": info["nodes"], "operations_unit": "nodes",
            "details": {"nodes": info["nodes"], "node_limit": acfg["max_nodes"],
                        "node_limit_reached": not info["proven_optimal"]}}


def entry(acfg, env):
    L = kp_algo_bnb_loader()
    return {"id": L["id"], "label": L["label"], "description": L["description"],
            "short_label": L["short_label"],
            "exact": L["exact"], "reference": L["reference"], "config": acfg}


SCHEMA = {
    "entry": {
    "type": "object", "additionalProperties": False,
    "required": ["id", "label", "description", "short_label", "exact", "reference", "config"],
    "properties": {
        "id": {"enum": ["bnb"]}, "label": {"type": "string"},
        "description": {"type": "string"},
        "short_label": {"type": "string"}, "exact": {"type": "boolean"},
        "reference": {"type": "boolean"},
        "config": {
            "type": "object", "additionalProperties": False,
            "required": ["max_nodes", "repeats"],
            "properties": {"max_nodes": {"type": "integer", "minimum": 1},
                           "repeats": {"type": "integer", "minimum": 1}},
        },
    },
},
    "details": {
        "type": "object", "additionalProperties": False,
        "required": ["nodes", "node_limit", "node_limit_reached"],
        "properties": {"nodes": {"type": "integer", "minimum": 0},
                       "node_limit": {"type": "integer", "minimum": 1},
                       "node_limit_reached": {"type": "boolean"}},
    },
}
