"""JSON output: raw.json, instances.json, --describe (port of kb_write_json.m)."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


def _clean(obj):
    """Make OBJ JSON-safe: NumPy scalars -> Python, NaN/inf -> null."""
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return _clean(obj.tolist())
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        x = float(obj)
        if not math.isfinite(x):
            return None
        return int(x) if x.is_integer() and abs(x) < 2 ** 53 else x
    return obj


def to_json(data) -> str:
    return json.dumps(_clean(data), indent=2)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_json(data) + "\n", encoding="utf-8")
