"""Typed deterministic diagnostics for OIF-2D manifest validation."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Tuple


@dataclass(frozen=True, order=True)
class ManifestValidationError:
    phase: str
    code: str
    path: str
    message: str
    suggestion: str = ""

    def as_mapping(self) -> Mapping[str, str]:
        return MappingProxyType({
            "phase": self.phase,
            "code": self.code,
            "path": self.path,
            "message": self.message,
            "suggestion": self.suggestion,
        })


@dataclass(frozen=True)
class ManifestValidationReport:
    valid: bool
    manifest: Any
    errors: Tuple[ManifestValidationError, ...]
    phases_completed: Tuple[str, ...]

    @property
    def error_count(self) -> int:
        return len(self.errors)

    def as_mapping(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "valid": self.valid,
            "manifest": self.manifest,
            "errors": tuple(error.as_mapping() for error in self.errors),
            "error_count": self.error_count,
            "phases_completed": self.phases_completed,
        })
