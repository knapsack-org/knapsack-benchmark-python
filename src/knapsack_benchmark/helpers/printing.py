"""Console output (port of kb_print_instance.m, kb_print_summary.m, kb_human_bytes.m)."""
from __future__ import annotations


def human_bytes(b) -> str:
    if b is None:
        return "n/a"
    if b >= 2 ** 20:
        return f"{b / 2 ** 20:.1f}MB"
    if b >= 2 ** 10:
        return f"{b / 2 ** 10:.1f}kB"
    return f"{int(b)}B"


def print_instance(r: dict, algos: list[str], log=print) -> None:
    """One line per instance: optimum, time and gap of each algorithm."""
    line = f"{r['id']:3d} {r['family']:<20} n={r['n']:2d} opt={r['optimum']:5.0f} |"
    for a in algos:
        x = r["results"][a]
        gap = "" if x["is_optimal"] else f" gap {x['gap_percent']:.2f}%"
        line += f" {a} {x['cost']['wall_time_s']:8.4f}s{gap} |"
    log(line)


def print_summary(s: dict, algos: list[str], total_time: float, out_file, log=print) -> None:
    """Summary table, ranking and output file."""
    log(f"\n{'algo':<9} {'optimal':>8} {'mean gap':>9} {'total t(s)':>11} {'median t(s)':>12} "
        f"{'median mem':>11} {'x time ref':>10} {'mean ops':>12}")
    for a in algos:
        p = s["algorithms"][a]
        ratio = p["median_time_ratio_vs_reference"]
        ops = p["mean_operations"]
        log(f"{a:<9} {p['num_optimal']:>4}/{s['num_instances']:<3} {p['mean_gap_percent']:8.2f}% "
            f"{p['total_wall_time_s']:11.3f} {p['median_wall_time_s']:12.5f} "
            f"{human_bytes(p['median_working_memory_bytes']):>11} "
            f"{(ratio if ratio is not None else float('nan')):10.1f} "
            f"{(ops if ops is not None else float('nan')):12.0f}")
    log(f"Fastest (median time): {' < '.join(s['ranking_by_median_time'])}\n"
        f"Total {total_time:.1f} s\nOutput: {out_file}")
