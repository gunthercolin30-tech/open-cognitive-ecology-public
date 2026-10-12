from __future__ import annotations

import json
import tempfile
from pathlib import Path

from oif.adapters.validation_report_adapter import (
    ValidationReportAdapter,
    ValidationReportFormatError,
)


def base_fixture() -> dict[str, object]:
    return {
        "diagnostics": {
            "modules_discovered": 2,
            "error_count": 0,
            "failed_calls": 0,
            "timeouts": 0,
            "failed_modules": [],
        },
        "metadata": {"elapsed_seconds": 0.25},
        "summary": {
            "overall_success": True,
            "tests_total": 2,
            "tests_passed": 2,
            "tests_failed": 0,
        },
        "tests": [
            {"name": "test-one", "passed": True},
            {"name": "test-two", "passed": True},
        ],
        "timestamp_utc": "2026-07-18T06:00:00+00:00",
        "validation_mode": "consistency-fixture",
    }


def expect_rejected(root: Path, document: dict[str, object]) -> None:
    path = root / "scientific_validation_report.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    try:
        ValidationReportAdapter(root=root).read()
    except ValidationReportFormatError:
        return
    raise AssertionError("inconsistent report was accepted")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oif2_3_consistency_") as tmp:
        root = Path(tmp)
        source = root / "scientific_validation_report.json"

        for token in ("NaN", "Infinity", "-Infinity"):
            raw = json.dumps(base_fixture()).replace(
                '"elapsed_seconds": 0.25',
                f'"elapsed_seconds": {token}',
            )
            source.write_text(raw, encoding="utf-8")
            try:
                ValidationReportAdapter(root=root).read()
            except ValidationReportFormatError:
                pass
            else:
                raise AssertionError(f"{token} was accepted")

        for field in ("error_count", "failed_calls", "timeouts"):
            fixture = base_fixture()
            diagnostics = fixture["diagnostics"]
            assert isinstance(diagnostics, dict)
            diagnostics[field] = 1
            expect_rejected(root, fixture)

        fixture = base_fixture()
        diagnostics = fixture["diagnostics"]
        assert isinstance(diagnostics, dict)
        diagnostics["failed_modules"] = ["module-a"]
        expect_rejected(root, fixture)

        fixture = base_fixture()
        summary = fixture["summary"]
        tests = fixture["tests"]
        assert isinstance(summary, dict)
        assert isinstance(tests, list)
        assert isinstance(tests[1], dict)
        summary["tests_failed"] = 1
        summary["tests_passed"] = 1
        summary["overall_success"] = True
        tests[1]["passed"] = False
        expect_rejected(root, fixture)

        fixture = base_fixture()
        tests = fixture["tests"]
        assert isinstance(tests, list)
        assert isinstance(tests[1], dict)
        tests[1]["passed"] = False
        expect_rejected(root, fixture)

        fixture = base_fixture()
        tests = fixture["tests"]
        assert isinstance(tests, list)
        assert isinstance(tests[1], dict)
        tests[1]["name"] = " test-one "
        expect_rejected(root, fixture)

        fixture = base_fixture()
        metadata = fixture["metadata"]
        assert isinstance(metadata, dict)
        metadata["elapsed_seconds"] = -1
        expect_rejected(root, fixture)

        fixture = base_fixture()
        metadata = fixture["metadata"]
        assert isinstance(metadata, dict)
        metadata["elapsed_seconds"] = True
        expect_rejected(root, fixture)

        fixture = base_fixture()
        diagnostics = fixture["diagnostics"]
        assert isinstance(diagnostics, dict)
        diagnostics["error_count"] = True
        expect_rejected(root, fixture)

        fixture = base_fixture()
        diagnostics = fixture["diagnostics"]
        assert isinstance(diagnostics, dict)
        diagnostics["failed_modules"] = ["module-a", " module-a "]
        expect_rejected(root, fixture)

        source.write_text(json.dumps(base_fixture()), encoding="utf-8")
        payload = ValidationReportAdapter(root=root).read()
        assert payload["adapter_schema_version"] == (
            "oif2.validation-report-adapter.v2"
        )
        assert payload["elapsed_seconds"] == 0.25

    print("OIF2_3_VALIDATION_REPORT_CONSISTENCY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
