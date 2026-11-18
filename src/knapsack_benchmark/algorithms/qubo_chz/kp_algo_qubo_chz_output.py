"""Benchmark adapter and JSON description of 'qubo_chz' (port of kp_algo_qubo_chz_output.m).

run(v, w, C, acfg, seed)  runs kp_algo_qubo_chz_main, times its phases (build, solve, decode),
                          returns the common result dict
entry(acfg, env)          entry of the JSON "algorithms" array
SCHEMA                    JSON Schema of that entry ("entry") and of results.qubo_chz.details ("details")
"""
from __future__ import annotations

from ...helpers.phase_timer import phase_timer
from .kp_algo_qubo_chz_loader import kp_algo_qubo_chz_loader
from .kp_algo_qubo_chz_main import kp_algo_qubo_chz_main


def _label(acfg) -> str:
    return f"{kp_algo_qubo_chz_loader()['label']} ({acfg['tabu']['mode']})"


def run(v, w, C, acfg, seed):
    mark, t = phase_timer()
    items, info = kp_algo_qubo_chz_main(v, w, C, acfg, seed, mark)
    sol = info["sol"]
    return {"label": _label(acfg), "exact": False, "proven_optimal": False, "items": items,
            "working_memory_bytes": max(info["working_memory_bytes"], info["model_memory_bytes"]),
            "operations": info["move_evaluations"], "operations_unit": "move evaluations",
            "details": {"penalty": info["penalty"], "variables": info["variables"],
                        "slack_bits": info["slack_bits"],
                        "model_memory_bytes": info["model_memory_bytes"],
                        "energy": info["energy"], "iterations": info["iterations"],
                        "raw_items": sol["items"], "raw_value": sol["value"],
                        "raw_weight": sol["weight"],
                        "feasible_before_repair": sol["feasible"], "repaired": sol["repaired"],
                        "build_time_s": t["build"], "solve_time_s": t["solve"],
                        "decode_time_s": t["decode"]}}


def entry(acfg, env):
    L = kp_algo_qubo_chz_loader()
    return {"id": L["id"], "label": _label(acfg), "description": L["description"],
            "short_label": L["short_label"],
            "exact": L["exact"], "reference": L["reference"], "config": acfg}


SCHEMA = {
    "entry": {
    "type": "object", "additionalProperties": False,
    "required": ["id", "label", "description", "short_label", "exact", "reference", "config"],
    "properties": {
        "id": {"enum": ["qubo_chz"]}, "label": {"type": "string"},
        "description": {"type": "string"},
        "short_label": {"type": "string"}, "exact": {"type": "boolean"},
        "reference": {"type": "boolean"},
        "config": {
            "type": "object", "additionalProperties": False,
            "required": ["penalty", "seed_offset", "tabu", "repeats"],
            "properties": {
                "penalty": {"type": ["string", "number"]},
                "seed_offset": {"type": "integer"},
                "tabu": {
                    "type": "object", "additionalProperties": False,
                    "required": ["mode", "restarts", "max_iter_factor", "stall_factor",
                                 "tenure_min"],
                    "properties": {
                        "mode": {"enum": ["slack-optimal", "all-bits"]},
                        "restarts": {"type": "integer", "minimum": 1},
                        "max_iter_factor": {"type": "number", "minimum": 0},
                        "stall_factor": {"type": "number", "minimum": 0},
                        "tenure_min": {"type": "integer", "minimum": 0},
                    },
                },
                "repeats": {"type": "integer", "minimum": 1},
            },
        },
    },
},
    "details": {
        "type": "object", "additionalProperties": False,
        "required": ["penalty", "variables", "slack_bits", "model_memory_bytes", "energy",
                     "iterations", "raw_items", "raw_value", "raw_weight",
                     "feasible_before_repair", "repaired", "build_time_s", "solve_time_s",
                     "decode_time_s"],
        "properties": {
            "penalty": {"type": "number"},
            "variables": {"type": "integer", "minimum": 1},
            "slack_bits": {"type": "integer", "minimum": 0},
            "model_memory_bytes": {"type": "integer", "minimum": 0},
            "energy": {"type": "number"},
            "iterations": {"type": "integer", "minimum": 0},
            "raw_items": {"type": "array", "items": {"type": "integer", "minimum": 1}},
            "raw_value": {"type": "number"},
            "raw_weight": {"type": "number"},
            "feasible_before_repair": {"type": "boolean"},
            "repaired": {"type": "boolean"},
            "build_time_s": {"type": "number", "minimum": 0},
            "solve_time_s": {"type": "number", "minimum": 0},
            "decode_time_s": {"type": "number", "minimum": 0},
        },
    },
}
