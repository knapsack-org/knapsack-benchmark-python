"""Cost ratios to the reference algorithm (port of kb_add_ratios.m)."""
from __future__ import annotations


def add_ratios(results: dict, ref: str) -> None:
    """Cost of each algorithm relative to the reference REF (> 1 = costlier)."""
    base = results[ref]["cost"]
    for r in results.values():
        ratios = {"time": r["cost"]["wall_time_s"] / max(base["wall_time_s"], 1e-12),
                  "cpu": r["cost"]["cpu_time_s"] / max(base["cpu_time_s"], 1e-12),
                  "memory": None}
        if r["cost"]["working_memory_bytes"] and base["working_memory_bytes"]:
            ratios["memory"] = r["cost"]["working_memory_bytes"] / base["working_memory_bytes"]
        r["cost_ratio_vs_reference"] = ratios
