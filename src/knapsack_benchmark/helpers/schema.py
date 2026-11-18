"""Check a value against a JSON Schema subset (port of kb_validate_schema.m).

Supported keywords: type (object, array, string, number, integer, boolean, null, or a
list of them), enum, minimum, properties, required, additionalProperties (False only),
items. NumPy scalars and arrays are accepted as the JSON writer converts them; NaN is null.
"""
from __future__ import annotations

import math
import numbers

import numpy as np


class SchemaError(ValueError):
    """A value does not match its schema."""


def _is_number(x) -> bool:
    return (isinstance(x, numbers.Real) and not isinstance(x, (bool, np.bool_))
            and math.isfinite(float(x)))


_TYPES = {
    "object": lambda x: isinstance(x, dict),
    "array": lambda x: isinstance(x, (list, tuple, np.ndarray)),
    "string": lambda x: isinstance(x, str),
    "boolean": lambda x: isinstance(x, (bool, np.bool_)),
    "number": _is_number,
    "integer": lambda x: _is_number(x) and float(x).is_integer(),
    "null": lambda x: x is None or (isinstance(x, float) and math.isnan(x)),
}


def validate(x, schema: dict, where: str = "$") -> None:
    """Raise SchemaError (message starts with WHERE) if X does not match SCHEMA."""
    if "type" in schema:
        types = [schema["type"]] if isinstance(schema["type"], str) else schema["type"]
        if not any(_TYPES[t](x) for t in types):
            raise SchemaError(f"{where}: expected {' or '.join(types)}, got {type(x).__name__}")
    if "enum" in schema and x not in schema["enum"]:
        raise SchemaError(f"{where}: value {x!r} not in enum")
    if "minimum" in schema and _is_number(x) and x < schema["minimum"]:
        raise SchemaError(f"{where}: {x} < minimum {schema['minimum']}")
    if isinstance(x, dict):
        for key in schema.get("required", []):
            if key not in x:
                raise SchemaError(f'{where}: missing required field "{key}"')
        props = schema.get("properties", {})
        for key, value in x.items():
            if key in props:
                validate(value, props[key], f"{where}.{key}")
            elif schema.get("additionalProperties") is False:
                raise SchemaError(f'{where}: unexpected field "{key}"')
    if isinstance(x, (list, tuple, np.ndarray)) and "items" in schema:
        for i, item in enumerate(x):
            validate(item, schema["items"], f"{where}[{i}]")
