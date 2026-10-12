from __future__ import annotations

from pathlib import Path

from oif.adapters.validation_report_adapter import ValidationReportAdapter
from oif.application.default_providers import build_default_provider_specs
from oif.application.shell_service import OIF2ReadOnlyApplicationService

ROOT = Path.home() / "open-cognitive-ecology"
EXPECTED_SCHEMA = "oif2.validation-report-adapter.v2"


def main() -> int:
    adapter = ValidationReportAdapter(root=ROOT)
    payload = adapter.read()

    assert payload["adapter_schema_version"] == EXPECTED_SCHEMA
    assert payload["modules_discovered"] > 0
    assert payload["error_count"] >= 0
    assert payload["failed_calls"] >= 0
    assert payload["timeouts"] >= 0
    assert payload["elapsed_seconds"] >= 0
    assert payload["read_only"] is True
    assert payload["functional_conclusion_only"] is True
    assert payload["phenomenology_undetermined"] is True

    snapshot = OIF2ReadOnlyApplicationService(
        providers=build_default_provider_specs(root=ROOT)
    ).snapshot()

    cards = {
        card["provider"]: card
        for card in snapshot["cards"]
    }
    assert "validation-report" in cards
    validation_card = cards["validation-report"]
    assert validation_card["zone"] == "science"
    assert validation_card["payload"]["adapter_schema_version"] == (
        EXPECTED_SCHEMA
    )

    print("OIF2_3_VALIDATION_REPORT_REAL_SOURCE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
