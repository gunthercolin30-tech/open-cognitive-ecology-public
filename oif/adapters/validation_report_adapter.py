"""Governed read-only adapter for scientific_validation_report.json."""
from __future__ import annotations

import json
import math
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

DEFAULT_ROOT = Path.home() / "open-cognitive-ecology"
DEFAULT_RELATIVE_PATH = Path("scientific_validation_report.json")
DEFAULT_MAX_BYTES = 1024 * 1024
ADAPTER_SCHEMA_VERSION = "oif2.validation-report-adapter.v2"
REQUIRED_ROOT_KEYS = frozenset({
    "diagnostics",
    "metadata",
    "summary",
    "tests",
    "timestamp_utc",
    "validation_mode",
})


class ValidationReportAdapterError(RuntimeError):
    """Base class for controlled adapter failures."""


class ValidationReportPathError(ValidationReportAdapterError):
    """Raised when the governed source path escapes the repository root."""


class ValidationReportSizeError(ValidationReportAdapterError):
    """Raised when the report is empty or larger than the configured limit."""


class ValidationReportFormatError(ValidationReportAdapterError):
    """Raised when JSON decoding or structural validation fails."""


def _reject_non_finite_json_constant(token: str) -> None:
    raise ValidationReportFormatError(
        f"non-finite JSON constant is forbidden: {token}"
    )


def _is_within(candidate: Path, root: Path) -> bool:
    return candidate == root or root in candidate.parents


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationReportFormatError(f"{label} must be a mapping")
    return value


def _require_bool(value: Any, label: str) -> bool:
    if type(value) is not bool:
        raise ValidationReportFormatError(f"{label} must be a boolean")
    return value


def _require_non_negative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValidationReportFormatError(
            f"{label} must be a non-negative integer"
        )
    return value


def _require_non_negative_finite_number(value: Any, label: str) -> float:
    if type(value) not in (int, float):
        raise ValidationReportFormatError(
            f"{label} must be a finite non-negative number"
        )
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0:
        raise ValidationReportFormatError(
            f"{label} must be a finite non-negative number"
        )
    return numeric


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationReportFormatError(f"{label} must be a non-empty string")
    return value.strip()


def _validate_timestamp(value: Any) -> str:
    timestamp = _require_string(value, "timestamp_utc")
    normalized = timestamp.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValidationReportFormatError(
            "timestamp_utc must be ISO-8601"
        ) from exc
    if parsed.tzinfo is None:
        raise ValidationReportFormatError(
            "timestamp_utc must include a timezone"
        )
    return timestamp


class ValidationReportAdapter:
    """Read, validate, and normalize the official validation report."""

    def __init__(
        self,
        root: Path = DEFAULT_ROOT,
        relative_path: Path = DEFAULT_RELATIVE_PATH,
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> None:
        self._root = Path(root).expanduser().resolve(strict=False)
        self._relative_path = Path(relative_path)
        if self._relative_path.is_absolute():
            raise ValidationReportPathError(
                "relative_path must not be absolute"
            )
        if type(max_bytes) is not int or max_bytes <= 0:
            raise ValueError("max_bytes must be a positive integer")
        self._max_bytes = max_bytes

    @property
    def source_path(self) -> Path:
        unresolved = self._root / self._relative_path
        candidate = unresolved.resolve(strict=False)
        if not _is_within(candidate, self._root):
            raise ValidationReportPathError(
                "validation report path escapes repository root"
            )
        return candidate

    def _read_document(self) -> Mapping[str, Any]:
        path = self.source_path
        try:
            stat_result = path.stat()
        except FileNotFoundError as exc:
            raise ValidationReportAdapterError(
                f"validation report missing: {self._relative_path.as_posix()}"
            ) from exc
        if not path.is_file():
            raise ValidationReportAdapterError(
                "validation report source is not a regular file"
            )
        if stat_result.st_size <= 0:
            raise ValidationReportSizeError(
                "validation report must not be empty"
            )
        if stat_result.st_size > self._max_bytes:
            raise ValidationReportSizeError(
                f"validation report exceeds {self._max_bytes} bytes"
            )

        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise ValidationReportAdapterError(
                "validation report cannot be read"
            ) from exc

        if len(raw) > self._max_bytes:
            raise ValidationReportSizeError(
                f"validation report exceeds {self._max_bytes} bytes"
            )
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ValidationReportFormatError(
                "validation report must be UTF-8"
            ) from exc
        try:
            document = json.loads(
                text,
                parse_constant=_reject_non_finite_json_constant,
            )
        except ValidationReportFormatError:
            raise
        except json.JSONDecodeError as exc:
            raise ValidationReportFormatError(
                "validation report contains invalid JSON"
            ) from exc
        return _require_mapping(document, "report")

    def read(self) -> dict[str, Any]:
        document = self._read_document()
        missing = sorted(REQUIRED_ROOT_KEYS.difference(document))
        if missing:
            raise ValidationReportFormatError(
                "validation report missing keys: " + ", ".join(missing)
            )

        diagnostics = _require_mapping(
            document["diagnostics"], "diagnostics"
        )
        metadata = _require_mapping(document["metadata"], "metadata")
        summary = _require_mapping(document["summary"], "summary")
        tests = document["tests"]
        if not isinstance(tests, list):
            raise ValidationReportFormatError("tests must be a list")

        modules_discovered = _require_non_negative_int(
            diagnostics.get("modules_discovered"),
            "diagnostics.modules_discovered",
        )
        error_count = _require_non_negative_int(
            diagnostics.get("error_count"),
            "diagnostics.error_count",
        )
        failed_calls = _require_non_negative_int(
            diagnostics.get("failed_calls"),
            "diagnostics.failed_calls",
        )
        timeouts = _require_non_negative_int(
            diagnostics.get("timeouts"),
            "diagnostics.timeouts",
        )
        failed_modules = diagnostics.get("failed_modules")
        if not isinstance(failed_modules, list) or not all(
            isinstance(item, str) and item.strip()
            for item in failed_modules
        ):
            raise ValidationReportFormatError(
                "diagnostics.failed_modules must be a list of non-empty strings"
            )
        normalized_failed_modules = [item.strip() for item in failed_modules]
        if len(normalized_failed_modules) != len(set(normalized_failed_modules)):
            raise ValidationReportFormatError(
                "diagnostics.failed_modules contains duplicates"
            )

        overall_success = _require_bool(
            summary.get("overall_success"),
            "summary.overall_success",
        )
        tests_total = _require_non_negative_int(
            summary.get("tests_total"),
            "summary.tests_total",
        )
        tests_passed = _require_non_negative_int(
            summary.get("tests_passed"),
            "summary.tests_passed",
        )
        tests_failed = _require_non_negative_int(
            summary.get("tests_failed"),
            "summary.tests_failed",
        )
        if tests_passed + tests_failed != tests_total:
            raise ValidationReportFormatError(
                "summary test counts are inconsistent"
            )
        if len(tests) != tests_total:
            raise ValidationReportFormatError(
                "tests length differs from summary.tests_total"
            )

        observed_passed = 0
        observed_failed = 0
        names: list[str] = []
        for index, test in enumerate(tests):
            entry = _require_mapping(test, f"tests[{index}]")
            name = _require_string(entry.get("name"), f"tests[{index}].name")
            passed = _require_bool(
                entry.get("passed"), f"tests[{index}].passed"
            )
            names.append(name)
            if passed:
                observed_passed += 1
            else:
                observed_failed += 1

        if len(names) != len(set(names)):
            raise ValidationReportFormatError(
                "tests contains duplicate normalized names"
            )
        if observed_passed != tests_passed:
            raise ValidationReportFormatError(
                "summary.tests_passed differs from observed test entries"
            )
        if observed_failed != tests_failed:
            raise ValidationReportFormatError(
                "summary.tests_failed differs from observed test entries"
            )

        elapsed_seconds = _require_non_negative_finite_number(
            metadata.get("elapsed_seconds"),
            "metadata.elapsed_seconds",
        )
        validation_mode = _require_string(
            document["validation_mode"], "validation_mode"
        )
        timestamp_utc = _validate_timestamp(document["timestamp_utc"])

        if overall_success:
            contradictions = {
                "error_count": error_count,
                "failed_calls": failed_calls,
                "timeouts": timeouts,
                "failed_modules": len(normalized_failed_modules),
                "tests_failed": tests_failed,
            }
            active = [
                f"{name}={value}"
                for name, value in contradictions.items()
                if value != 0
            ]
            if active:
                raise ValidationReportFormatError(
                    "overall_success contradicts failure diagnostics: "
                    + ", ".join(active)
                )

        normalized = {
            "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
            "status": "ok" if overall_success else "validation_failed",
            "overall_success": overall_success,
            "validation_mode": validation_mode,
            "timestamp_utc": timestamp_utc,
            "modules_discovered": modules_discovered,
            "error_count": error_count,
            "failed_calls": failed_calls,
            "timeouts": timeouts,
            "failed_modules": normalized_failed_modules,
            "tests_total": tests_total,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "elapsed_seconds": elapsed_seconds,
            "source": {
                "relative_path": self._relative_path.as_posix(),
                "max_bytes": self._max_bytes,
            },
            "read_only": True,
            "functional_conclusion_only": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
        }
        return deepcopy(normalized)

    def __call__(self) -> Mapping[str, Any]:
        return self.read()
