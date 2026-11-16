"""Validate the requested algorithm ids (port of kb_check_algorithms.m)."""
from __future__ import annotations

from ..config import ALGORITHMS


def check_algorithms(requested) -> list[str]:
    algos = list(requested)
    for a in algos:
        if a not in ALGORITHMS:
            raise ValueError(f'Unknown algorithm "{a}"')
    return algos
