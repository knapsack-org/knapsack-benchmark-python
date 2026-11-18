"""Benchmark adapter and JSON description of 'ising' (port of kp_algo_ising_output.m)."""
from __future__ import annotations

from ...helpers.phase_timer import phase_timer
from .kp_algo_ising_loader import kp_algo_ising_loader
from .kp_algo_ising_main import kp_algo_ising_main

_ID = "ising"
_LABEL = kp_algo_ising_loader()["label"]


def run(v, w, C, acfg, seed) -> dict:
    """Run kp_algo_ising_main, time its phases (build, solve, decode), return the common result dict."""
    mark, t = phase_timer()
    items, info = kp_algo_ising_main(v, w, C, acfg, seed, mark)
    sol = info["sol"]
    return {"label": _LABEL, "exact": False, "proven_optimal": False, "items": items,
            "working_memory_bytes": info["working_memory_bytes"],
            "operations": info["proposals"], "operations_unit": "move evaluations",
            "details": {"penalty": info["penalty"], "variables": info["variables"],
                        "slack_bits": info["slack_bits"],
                        "model_memory_bytes": info["model_memory_bytes"], "energy": info["energy"],
                        "proposals": info["proposals"], "accepted": info["accepted"],
                        "raw_items": sol["items"], "raw_value": sol["value"],
                        "raw_weight": sol["weight"],
                        "feasible_before_repair": sol["feasible"], "repaired": sol["repaired"],
                        "build_time_s": t["build"], "solve_time_s": t["solve"],
                        "decode_time_s": t["decode"]}}


def entry(acfg, env=None) -> dict:
    """Entry of the JSON "algorithms" array."""
    L = kp_algo_ising_loader()
    return {"id": L["id"], "label": _LABEL, "description": L["description"],
            "short_label": L["short_label"], "exact": L["exact"],
            "reference": L["reference"], "config": acfg}


_INT = {"type": "integer", "minimum": 0}
_NUM = {"type": "number"}
SCHEMA = {
    "entry": {
        "type": "object", "additionalProperties": False,
        "required": ["id", "label", "description", "short_label", "exact", "reference", "config"],
        "properties": {
            "id": {"enum": [_ID]}, "label": {"type": "string"}, "description": {"type": "string"},
            "short_label": {"type": "string"},
            "exact": {"type": "boolean"}, "reference": {"type": "boolean"},
            "config": {
                "type": "object", "additionalProperties": False,
                "required": ["penalty", "restarts", "steps_factor", "t0_factor", "t_end_factor",
                             "repeats"],
                "properties": {"penalty": {"type": ["string", "number"]},
                               "restarts": {"type": "integer", "minimum": 1},
                               "steps_factor": {"type": "number", "minimum": 0},
                               "t0_factor": {"type": "number", "minimum": 0},
                               "t_end_factor": {"type": "number", "minimum": 0},
                               "repeats": {"type": "integer", "minimum": 1}}}}},
    "details": {
        "type": "object", "additionalProperties": False,
        "required": ["penalty", "variables", "slack_bits", "model_memory_bytes", "energy",
                     "proposals", "accepted", "raw_items", "raw_value", "raw_weight",
                     "feasible_before_repair", "repaired", "build_time_s", "solve_time_s",
                     "decode_time_s"],
        "properties": {"penalty": _NUM, "variables": {"type": "integer", "minimum": 1},
                       "slack_bits": _INT, "model_memory_bytes": _INT, "energy": _NUM,
                       "proposals": _INT, "accepted": _INT,
                       "raw_items": {"type": "array", "items": {"type": "integer", "minimum": 1}},
                       "raw_value": _NUM, "raw_weight": _NUM,
                       "feasible_before_repair": {"type": "boolean"}, "repaired": {"type": "boolean"},
                       "build_time_s": {"type": "number", "minimum": 0},
                       "solve_time_s": {"type": "number", "minimum": 0},
                       "decode_time_s": {"type": "number", "minimum": 0}}}}
