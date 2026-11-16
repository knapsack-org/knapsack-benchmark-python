"""Exact 0-1 knapsack as an integer linear program (counterpart of kb_knapsack_ilp.m).

    max v'x  s.t.  w'x <= C,  x binary

Solved with ``scipy.optimize.milp`` (HiGHS), the same engine as MATLAB's
``intlinprog`` since R2024a.
"""
from __future__ import annotations

import contextlib
import os
import sys

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


@contextlib.contextmanager
def _silence_native_output():
    """Mute stdout/stderr at the file-descriptor level: some HiGHS builds print
    internal debug lines from C++ even when display is off."""
    try:
        sys.stdout.flush()
        sys.stderr.flush()
        saved = [os.dup(1), os.dup(2)]
    except (OSError, ValueError):          # no real file descriptors (e.g. some IDEs)
        yield
        return
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        yield
    finally:
        os.dup2(saved[0], 1)
        os.dup2(saved[1], 2)
        for fd in (*saved, devnull):
            os.close(fd)


def knapsack_ilp(v, w, C) -> tuple[float, list[int], dict]:
    """Returns (best value, 1-based items, info) with
    info = {solver, status, proven_optimal, nodes, mip_gap, array_bytes}.
    array_bytes covers the problem data only (the solver's memory is not visible)."""
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    with _silence_native_output():
        res = milp(c=-v, integrality=np.ones_like(v), bounds=Bounds(0, 1),
                   constraints=LinearConstraint(w[np.newaxis, :], -np.inf, C),
                   options={"mip_rel_gap": 0})
    x = np.zeros_like(v) if res.x is None else np.round(res.x)
    take = x > 0.5
    nodes = getattr(res, "mip_node_count", None)
    info = {
        "solver": "scipy.optimize.milp (HiGHS)",
        "status": int(res.status),
        "proven_optimal": bool(res.status == 0),
        "nodes": None if nodes is None else int(nodes),
        "mip_gap": None if getattr(res, "mip_gap", None) is None else float(res.mip_gap),
        "array_bytes": int(2 * v.nbytes + w.nbytes + x.nbytes),
    }
    items = [int(i) + 1 for i in np.flatnonzero(take)]
    return float(v[take].sum()), items, info
