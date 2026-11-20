"""Benchmark adapter and JSON description of 'qubo_chz' (port of kp_algo_qubo_chz_output.m).

run(v, w, C, acfg, seed)  runs kp_algo_qubo_chz_main, times its phases (build, solve, decode),
                          returns the common result dict
entry(acfg, env)          entry of the JSON "algorithms" array
JSON Schema of both: kp_algo_qubo_chz_output.schema.json (next to this file)
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
