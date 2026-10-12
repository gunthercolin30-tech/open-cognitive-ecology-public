from __future__ import annotations

import json
import tempfile
from pathlib import Path

from oif.adapters.validation_report_adapter import ValidationReportAdapter
from oif.application.default_providers import build_default_provider_specs
from oif.application.shell_service import OIF2ReadOnlyApplicationService


def fixture() -> dict[str, object]:
    return {
        "diagnostics": {
            "modules_discovered": 1269,
            "error_count": 0,
            "failed_calls": 0,
            "timeouts": 0,
            "failed_modules": [],
        },
        "metadata": {
            "elapsed_seconds": 12.5,
        },
        "summary": {
            "overall_success": True,
            "tests_total": 2,
            "tests_passed": 2,
            "tests_failed": 0,
        },
        "tests": [
            {"name": "module_discovery", "passed": True},
            {"name": "error_free_execution", "passed": True},
        ],
        "timestamp_utc": "2026-07-18T06:00:00+00:00",
        "validation_mode": "full_isolated",
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oif2_3_functional_") as directory:
        root = Path(directory)
        source = root / "scientific_validation_report.json"
        source.write_text(
            json.dumps(fixture(), sort_keys=True),
            encoding="utf-8",
        )

        adapter = ValidationReportAdapter(root=root)
        first = adapter.read()
        second = adapter.read()
        assert first == second
        assert first["status"] == "ok"
        assert first["overall_success"] is True
        assert first["modules_discovered"] == 1269
        assert first["functional_conclusion_only"] is True
        assert first["consciousness_proven"] is False
        assert first["read_only"] is True

        providers = build_default_provider_specs(root=root)
        service = OIF2ReadOnlyApplicationService(providers=providers)
        snapshot = service.snapshot()
        assert snapshot["status"] in {"ready", "degraded"}
        cards = {card["provider"]: card for card in snapshot["cards"]}
        assert "validation-report" in cards
        validation_card = cards["validation-report"]
        assert validation_card["zone"] == "science"
        assert validation_card["payload"]["overall_success"] is True

    print("OIF2_3_VALIDATION_REPORT_ADAPTER_FUNCTIONAL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
