from __future__ import annotations

from pathlib import Path

from oif.adapters.runtime_health_adapter import RuntimeHealthAdapter
from oif.application.default_providers import build_default_provider_specs
from oif.application.shell_service import OIF2ReadOnlyApplicationService

ROOT = Path.home() / "open-cognitive-ecology"


def main() -> int:
    payload = RuntimeHealthAdapter(root=ROOT).read()
    assert payload["adapter_schema_version"] == (
        "oif2.runtime-health-adapter.v1"
    )
    assert payload["source_count"] == 3
    assert payload["read_only"] is True
    assert payload["producer_execution"] is False
    assert payload["synthetic_cross_source_score"] is False

    snapshot = OIF2ReadOnlyApplicationService(
        providers=build_default_provider_specs(root=ROOT)
    ).snapshot()
    cards = {card["provider"]: card for card in snapshot["cards"]}
    assert "validation-report" in cards
    assert "runtime-health" in cards
    assert cards["runtime-health"]["zone"] == "runtime"
    assert cards["runtime-health"]["payload"]["adapter_schema_version"] == (
        "oif2.runtime-health-adapter.v1"
    )

    print("OIF2_3C_RUNTIME_HEALTH_REAL_SOURCE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
