"""Tiny JSON-schema checker (type, properties, required, items, enum, min/maxItems, min/maxLength, minimum/maximum).

DeepSeek's JSON mode guarantees valid JSON, not a schema, so every structured call is validated here and re-asked once
with the error text if it fails. No third-party dependency; deliberately small - unsupported keywords are ignored.
"""
from __future__ import annotations

from typing import Any

_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def _is(t: str, v: Any) -> bool:
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, _TYPES[t])


def validate(value: Any, schema: dict, path: str = "$") -> list[str]:
    errs: list[str] = []
    t = schema.get("type")
    if t:
        ts = t if isinstance(t, list) else [t]
        if not any(_is(x, value) for x in ts):
            return [f"{path}: expected {t}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {value!r} not in {schema['enum']}")
    if isinstance(value, dict):
        for k in schema.get("required", []):
            if k not in value:
                errs.append(f"{path}: missing '{k}'")
        for k, sub in schema.get("properties", {}).items():
            if k in value:
                errs += validate(value[k], sub, f"{path}.{k}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errs.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errs.append(f"{path}: more than {schema['maxItems']} items")
        if "items" in schema:
            for i, v in enumerate(value):
                errs += validate(v, schema["items"], f"{path}[{i}]")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errs.append(f"{path}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errs.append(f"{path}: longer than {schema['maxLength']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errs.append(f"{path}: below {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errs.append(f"{path}: above {schema['maximum']}")
    return errs
