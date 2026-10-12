"""Pure JSON/YAML representation helpers for OIF-2C.

No rendering, provider resolution, persistence, dynamic import, execution,
authorization, or governance action is performed here.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Union

from .specification import InterfaceSpecification

MAX_TEXT_BYTES = 4 * 1024 * 1024


class SerializationViolation(ValueError):
    pass


def _validate_plain(value: Any, depth: int = 0) -> Any:
    if depth > 32:
        raise SerializationViolation("maximum representation nesting depth exceeded")
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise SerializationViolation("non-finite numbers are forbidden")
        return value
    if isinstance(value, list):
        return [_validate_plain(item, depth + 1) for item in value]
    if isinstance(value, tuple):
        return [_validate_plain(item, depth + 1) for item in value]
    if isinstance(value, Mapping):
        result = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise SerializationViolation("mapping keys must be strings")
            result[key] = _validate_plain(item, depth + 1)
        return result
    raise SerializationViolation("unsupported representation type: %s" % type(value).__name__)


def specification_to_mapping(specification: InterfaceSpecification) -> Mapping[str, Any]:
    if not isinstance(specification, InterfaceSpecification):
        raise SerializationViolation("expected InterfaceSpecification")
    return _validate_plain(dict(specification.as_dict()))


def mapping_to_canonical_json(mapping: Mapping[str, Any]) -> str:
    plain = _validate_plain(mapping)
    return json.dumps(
        plain, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    )


def specification_to_json(specification: InterfaceSpecification, pretty: bool = False) -> str:
    mapping = specification_to_mapping(specification)
    if pretty:
        return json.dumps(
            mapping, ensure_ascii=False, sort_keys=True, indent=2,
            allow_nan=False,
        ) + "\n"
    return mapping_to_canonical_json(mapping)


def _yaml_module():
    try:
        import yaml
    except ImportError as exc:
        raise SerializationViolation("PyYAML is required for YAML representation") from exc
    return yaml


def specification_to_yaml(specification: InterfaceSpecification) -> str:
    yaml = _yaml_module()
    mapping = specification_to_mapping(specification)
    return yaml.safe_dump(
        mapping, allow_unicode=True, sort_keys=True, default_flow_style=False,
    )


def load_json_mapping(source: Union[str, Path]) -> Mapping[str, Any]:
    text = _read_source(source)
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SerializationViolation("invalid JSON: %s" % exc) from exc
    if not isinstance(value, Mapping):
        raise SerializationViolation("manifest root must be an object")
    return _validate_plain(value)


def load_yaml_mapping(source: Union[str, Path]) -> Mapping[str, Any]:
    yaml = _yaml_module()
    text = _read_source(source)
    try:
        value = yaml.safe_load(text)
    except Exception as exc:
        raise SerializationViolation("invalid or unsafe YAML: %s" % exc) from exc
    if not isinstance(value, Mapping):
        raise SerializationViolation("manifest root must be a mapping")
    return _validate_plain(value)


def _read_source(source: Union[str, Path]) -> str:
    if isinstance(source, Path):
        data = source.read_bytes()
        if len(data) > MAX_TEXT_BYTES:
            raise SerializationViolation("manifest exceeds maximum size")
        return data.decode("utf-8")
    if not isinstance(source, str):
        raise SerializationViolation("source must be text or Path")
    if len(source.encode("utf-8")) > MAX_TEXT_BYTES:
        raise SerializationViolation("manifest exceeds maximum size")
    return source
