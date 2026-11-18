"""Phase timer passed to kp_algo_<id>_main as its ``mark`` argument (port of kb_phase_timer.m)."""
from __future__ import annotations

import time


def phase_timer():
    """Return (mark, times): each ``mark(name)`` stores in ``times[name]`` the seconds
    since the previous mark (or since this call) and restarts the clock."""
    times: dict[str, float] = {}
    last = [time.perf_counter()]

    def mark(name: str) -> None:
        now = time.perf_counter()
        times[name] = now - last[0]
        last[0] = now

    return mark, times
