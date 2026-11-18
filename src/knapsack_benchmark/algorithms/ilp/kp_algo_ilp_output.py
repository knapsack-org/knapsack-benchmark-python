"""Benchmark adapter and JSON description of 'ilp' (port of kp_algo_ilp_output.m).

run(v, w, C, acfg, seed)  runs kp_algo_ilp_main, returns the common result dict
entry(acfg, env)          entry of the JSON "algorithms" array (env = loader environment)
SCHEMA                    JSON Schema of that entry ("entry") and of results.ilp.details ("details")
"""
from __future__ import annotations

from .kp_algo_ilp_loader import kp_algo_ilp_loader
from .kp_algo_ilp_main import kp_algo_ilp_main


def _label(solver: str) -> str:
    return f"{kp_algo_ilp_loader()['label']} ({solver})"


def run(v, w, C, acfg, seed):
    items, info = kp_algo_ilp_main(v, w, C, acfg, seed)
    return {"label": _label(info["solver"]), "exact": True,
            "proven_optimal": info["proven_optimal"], "items": items,
            "working_memory_bytes": info["working_memory_bytes"],
            "operations": info["nodes"], "operations_unit": "nodes",
            "details": {"solver": info["solver"], "status": info["status"],
                        "mip_gap": info["mip_gap"]}}


def entry(acfg, env):
    L = kp_algo_ilp_loader()
    return {"id": L["id"], "label": _label(env["solver"]), "description": L["description"],
            "short_label": L["short_label"],
            "exact": L["exact"], "reference": L["reference"], "config": acfg}


SCHEMA = {
    "entry": {
    "type": "object", "additionalProperties": False,
    "required": ["id", "label", "description", "short_label", "exact", "reference", "config"],
    "properties": {
        "id": {"enum": ["ilp"]}, "label": {"type": "string"},
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
        "type": "object", "additionalProperties": False,
        "required": ["solver", "status", "mip_gap"],
        "properties": {"solver": {"type": "string"}, "status": {"type": "integer"},
                       "mip_gap": {"type": ["number", "null"]}},
    },
}
