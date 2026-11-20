"""Shared check: a value against its kp_algo_<id>_output.schema.json part (keys only; Node's ajv checks the rest)."""
import pytest


def _conforms(x, schema, where="$"):
    if isinstance(x, dict) and "properties" in schema:
        missing = set(schema.get("required", [])) - set(x)
        extra = set(x) - set(schema["properties"]) if schema.get("additionalProperties") is False else set()
        assert not missing and not extra, f"{where}: missing {missing}, unexpected {extra}"
        for key, value in x.items():
            if key in schema["properties"]:
                _conforms(value, schema["properties"][key], f"{where}.{key}")


@pytest.fixture
def conforms():
    return _conforms
