"""Execution cost measurement (time, CPU, memory)."""
from __future__ import annotations

import gc
import statistics
import time
import tracemalloc
from typing import Any, Callable

try:
    import psutil
    _PROCESS = psutil.Process()
except Exception:  # psutil is optional
    _PROCESS = None


def process_memory() -> int | None:
    """Resident memory (RSS, bytes) of this Python process, or None without psutil.
    Process-wide snapshot: indicative only."""
    if _PROCESS is None:
        return None
    try:
        return int(_PROCESS.memory_info().rss)
    except Exception:
        return None


def measure(fn: Callable[[], Any], repeats: int, trace_memory: bool = False) -> tuple[Any, dict]:
    """Run FN and measure it.

    1. optional extra run under tracemalloc (untimed) -> peak bytes allocated by
       Python and NumPy during the call. tracemalloc slows Python loops down a
       lot (the QUBO tabu search ~10x), so it is off by default;
    2. REPEATS timed runs: wall time (perf_counter) and CPU time (process_time).
    Returns (result of the last run, cost dict).
    """
    peak = None
    if trace_memory:
        gc.collect()
        tracemalloc.start()
        fn()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    mem_before = process_memory()
    times = []
    cpu0 = time.process_time()
    out = None
    for _ in range(repeats):
        t = time.perf_counter()
        out = fn()
        times.append(time.perf_counter() - t)
    cpu = (time.process_time() - cpu0) / repeats
    mem_after = process_memory()

    cost = {
        "repeats": repeats,
        "wall_time_s": statistics.median(times),
        "wall_time_min_s": min(times),
        "cpu_time_s": cpu,
        "traced_peak_memory_bytes": peak,
        "process_memory_before_bytes": mem_before,
        "process_memory_after_bytes": mem_after,
        "process_memory_delta_bytes": (None if mem_before is None or mem_after is None
                                       else mem_after - mem_before),
    }
    return out, cost
