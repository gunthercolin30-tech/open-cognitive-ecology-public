from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from oif.adapters.validation_report_adapter import (
    ValidationReportAdapter,
    ValidationReportFormatError,
    ValidationReportPathError,
    ValidationReportSizeError,
)
from oif.application.default_providers import build_default_provider_specs
from oif.application.shell_service import OIF2ReadOnlyApplicationService


def valid_fixture() -> dict[str, object]:
    return {
        "diagnostics": {
            "modules_discovered": 1,
            "error_count": 0,
            "failed_calls": 0,
            "timeouts": 0,
            "failed_modules": [],
        },
        "metadata": {"elapsed_seconds": 0.1},
        "summary": {
            "overall_success": True,
            "tests_total": 1,
            "tests_passed": 1,
            "tests_failed": 0,
        },
        "tests": [{"name": "one", "passed": True}],
        "timestamp_utc": "2026-07-18T06:00:00+00:00",
        "validation_mode": "fixture",
    }


def expect(exception_type, callback) -> None:
    try:
        callback()
    except exception_type:
        return
    raise AssertionError(f"expected {exception_type.__name__}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oif2_3_degradation_") as directory:
        root = Path(directory)
        source = root / "scientific_validation_report.json"

        service = OIF2ReadOnlyApplicationService(
            providers=build_default_provider_specs(root=root)
        )
        missing = service.snapshot()
        assert missing["status"] == "degraded"
        assert missing["cards"][0]["payload"]["status"] == "unavailable"

        source.write_text("{invalid", encoding="utf-8")
        expect(
            ValidationReportFormatError,
            lambda: ValidationReportAdapter(root=root).read(),
        )

        source.write_text(json.dumps({"summary": {}}), encoding="utf-8")
        expect(
            ValidationReportFormatError,
            lambda: ValidationReportAdapter(root=root).read(),
        )

        source.write_bytes(b"x" * 65)
        expect(
            ValidationReportSizeError,
            lambda: ValidationReportAdapter(root=root, max_bytes=64).read(),
        )

        expect(
            ValidationReportPathError,
            lambda: ValidationReportAdapter(
                root=root,
                relative_path=Path("../outside.json"),
            ).read(),
        )

        outside = root.parent / f"{root.name}_outside.json"
        outside.write_text(json.dumps(valid_fixture()), encoding="utf-8")
        link = root / "linked_report.json"
        try:
            link.symlink_to(outside)
            expect(
                ValidationReportPathError,
                lambda: ValidationReportAdapter(
                    root=root,
                    relative_path=Path("linked_report.json"),
                ).read(),
            )
        finally:
            try:
                outside.unlink()
            except FileNotFoundError:
                pass

        bad = valid_fixture()
        bad["summary"] = {
            "overall_success": True,
            "tests_total": 2,
            "tests_passed": 1,
            "tests_failed": 0,
        }
        source.write_text(json.dumps(bad), encoding="utf-8")
        expect(
            ValidationReportFormatError,
            lambda: ValidationReportAdapter(root=root).read(),
        )

    print("OIF2_3_VALIDATION_REPORT_ADAPTER_DEGRADATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
