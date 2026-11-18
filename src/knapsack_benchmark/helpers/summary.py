"""Per-algorithm and per-family summary statistics of a run (port of kb_summary.m)."""
from __future__ import annotations

import statistics
from typing import Any


def _stat(values, fn):
    vals = [x for x in values if x is not None]
    return fn(vals) if vals else None


def summarize(runs: list[dict], algos: list[str], total_time: float) -> dict:
    s: dict[str, Any] = {"num_instances": len(runs), "total_time_seconds": total_time}
    per = {}
    for name in algos:
        res = [r["results"][name] for r in runs]
        fam = [r["family"] for r in runs]
        gaps = [x["gap_percent"] for x in res]
        t = [x["cost"]["wall_time_s"] for x in res]
        m = [x["cost"]["working_memory_bytes"] for x in res]
        ops = [x["cost"]["operations"] for x in res]
        p = {
            "algorithm": res[0]["algorithm"],
            "exact": res[0]["exact"],
            "num_optimal": sum(x["is_optimal"] for x in res),
            "num_proven_optimal": sum(bool(x["proven_optimal"]) for x in res),
            "num_feasible": sum(x["feasible"] for x in res),
            "mean_gap_percent": statistics.mean(gaps),
            "max_gap_percent": max(gaps),
            "total_wall_time_s": sum(t),
            "mean_wall_time_s": statistics.mean(t),
            "median_wall_time_s": statistics.median(t),
            "max_wall_time_s": max(t),
            "mean_cpu_time_s": statistics.mean(x["cost"]["cpu_time_s"] for x in res),
            "mean_working_memory_bytes": _stat(m, statistics.mean),
            "median_working_memory_bytes": _stat(m, statistics.median),
            "max_working_memory_bytes": _stat(m, max),
            "mean_operations": _stat(ops, statistics.mean),
            "max_operations": _stat(ops, max),
            "operations_unit": res[0]["cost"]["operations_unit"],
            "median_time_ratio_vs_reference": _stat([x["cost_ratio_vs_reference"]["time"] for x in res],
                                             statistics.median),
            "median_memory_ratio_vs_reference": _stat([x["cost_ratio_vs_reference"]["memory"] for x in res],
                                               statistics.median),
            "by_family": [],
        }
        for f in sorted(set(fam)):
            sel = [i for i, ff in enumerate(fam) if ff == f]
            p["by_family"].append({
                "family": f,
                "count": len(sel),
                "num_optimal": sum(res[i]["is_optimal"] for i in sel),
                "mean_gap_percent": statistics.mean(gaps[i] for i in sel),
                "mean_wall_time_s": statistics.mean(t[i] for i in sel),
                "max_wall_time_s": max(t[i] for i in sel),
                "mean_working_memory_bytes": _stat([m[i] for i in sel], statistics.mean),
            })
        per[name] = p
    s["algorithms"] = per
    s["ranking_by_median_time"] = sorted(algos, key=lambda a: per[a]["median_wall_time_s"])
    return s
