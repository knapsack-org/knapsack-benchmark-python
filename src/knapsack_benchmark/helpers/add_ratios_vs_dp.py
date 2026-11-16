"""Cost ratios to DP (port of kb_add_ratios_vs_dp.m)."""
from __future__ import annotations


def add_ratios_vs_dp(results: dict) -> None:
    """Cost of each algorithm relative to DP (> 1 = costlier)."""
    ref = results.get("dp", {}).get("cost")
    for r in results.values():
        ratios = {"time": None, "cpu": None, "memory": None}
        if ref is not None:
            ratios["time"] = r["cost"]["wall_time_s"] / max(ref["wall_time_s"], 1e-12)
            ratios["cpu"] = r["cost"]["cpu_time_s"] / max(ref["cpu_time_s"], 1e-12)
            if r["cost"]["working_memory_bytes"] and ref["working_memory_bytes"]:
                ratios["memory"] = r["cost"]["working_memory_bytes"] / ref["working_memory_bytes"]
        r["cost_ratio_vs_dp"] = ratios
