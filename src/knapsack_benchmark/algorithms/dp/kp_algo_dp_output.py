"""Benchmark adapter and JSON description of 'dp' (port of kp_algo_dp_output.m).

run(v, w, C, acfg, seed)  runs kp_algo_dp_main, returns the common result dict
entry(acfg, env)          entry of the JSON "algorithms" array
SCHEMA                    JSON Schema of that entry ("entry") and of results.dp.details ("details")
"""
from __future__ import annotations

from .kp_algo_dp_loader import kp_algo_dp_loader
from .kp_algo_dp_main import kp_algo_dp_main


def run(v, w, C, acfg, seed):
    items, info = kp_algo_dp_main(v, w, C, acfg, seed)
    return {"label": kp_algo_dp_loader()["label"], "exact": True, "proven_optimal": True,
            "items": items, "working_memory_bytes": info["working_memory_bytes"],
            "operations": info["operations"], "operations_unit": "table cells",
            "details": {"table_cells": info["operations"]}}


def entry(acfg, env):
    L = kp_algo_dp_loader()
    return {"id": L["id"], "label": L["label"], "description": L["description"],
            "short_label": L["short_label"],
            "exact": L["exact"], "reference": L["reference"], "config": acfg}


SCHEMA = {
    "entry": {
    "type": "object", "additionalProperties": False,
    "required": ["id", "label", "description", "short_label", "exact", "reference", "config"],
    "properties": {
        "id": {"enum": ["dp"]}, "label": {"type": "string"},
        "description": {"type": "string"},
        "short_label": {"type": "string"}, "exact": {"type": "boolean"},
        "reference": {"type": "boolean"},
        "config": {
            "type": "object", "additionalProperties": False, "required": ["repeats"],
            "properties": {"repeats": {"type": "integer", "minimum": 1}},
        },
    },
},
    "details": {
        "type": "object", "additionalProperties": False, "required": ["table_cells"],
        "properties": {"table_cells": {"type": "integer", "minimum": 0}},
    },
}
