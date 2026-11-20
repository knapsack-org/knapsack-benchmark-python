"""Console output (port of kb_print_instance.m, kb_print_progress.m)."""
from __future__ import annotations

import json

PROGRESS_PREFIX = "@@progress "   # read by the knapsack-server worker-agent


def print_progress(instance: int, algorithm: str, event: str, log=print) -> None:
    """``@@progress {"instance":<id>,"algorithm":"<id>","event":"start"|"done"}``, flushed at once."""
    log(PROGRESS_PREFIX + json.dumps({"instance": instance, "algorithm": algorithm, "event": event},
                                     separators=(",", ":")), flush=True)


def print_instance(inst, results: dict, algos: list[str], ref: str, log=print) -> None:
    """One line per instance: optimum (value of REF), time and gap of each algorithm."""
    opt = results[ref]["value"]
    line = f"{inst.id:3d} {inst.family:<20} n={inst.values.size:2d} opt={opt:5.0f} |"
    for a in algos:
        x = results[a]
        gap = "" if x["value"] == opt else f" gap {100 * (opt - x['value']) / opt if opt > 0 else 0:.2f}%"
        line += f" {a} {x['cost']['wall_time_s']:8.4f}s{gap} |"
    log(line)
