"""P162-G6.5c7d2 — minimal production script identity registry.

This registry binds opaque production identities to immutable script evidence.
It grants no execution authority and deliberately contains no test-harness entries.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Mapping

@dataclass(frozen=True)
class ProductionScriptIdentity:
    script_id: str
    relative_path: str
    sha256: str
    operation: str = "PYTHON_SCRIPT"

def _valid_hex_digest(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)

def validate_registry(registry: Mapping[str, ProductionScriptIdentity]) -> None:
    if not isinstance(registry, Mapping):
        raise ValueError("registry_mapping_required")
    for key, entry in registry.items():
        if not isinstance(key, str) or not key or "/" in key or "\\" in key or key.endswith(".py"):
            raise ValueError("opaque_script_id_required")
        if not isinstance(entry, ProductionScriptIdentity) or entry.script_id != key:
            raise ValueError("registry_identity_mismatch")
        rel = Path(entry.relative_path)
        if rel.is_absolute() or ".." in rel.parts or rel.suffix != ".py":
            raise ValueError("canonical_relative_python_path_required")
        if not _valid_hex_digest(entry.sha256):
            raise ValueError("sha256_required")
        if entry.operation != "PYTHON_SCRIPT":
            raise ValueError("unsupported_operation")

def resolve_registered_script(
    root: Path,
    script_id: str,
    registry: Mapping[str, ProductionScriptIdentity],
) -> Path:
    validate_registry(registry)
    entry = registry.get(script_id)
    if entry is None:
        raise ValueError("unresolved_registered_script")
    root = root.resolve()
    candidate = root / entry.relative_path
    if candidate.is_symlink():
        raise ValueError("registered_script_symlink_forbidden")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError):
        raise ValueError("registered_script_outside_root_or_missing")
    if not resolved.is_file():
        raise ValueError("registered_script_regular_file_required")
    actual = sha256(resolved.read_bytes()).hexdigest()
    if actual != entry.sha256:
        raise ValueError("registered_script_hash_drift")
    return resolved

# Intentionally empty at c7d2: no production REGISTERED_SCRIPT need has been proven.
# VALIDATION_MAIN is a separate closed command kind and requires no script-registry entry.
PRODUCTION_SCRIPT_REGISTRY: dict[str, ProductionScriptIdentity] = {}
validate_registry(PRODUCTION_SCRIPT_REGISTRY)
