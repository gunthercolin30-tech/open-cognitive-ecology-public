from __future__ import annotations
from oif.application.default_providers import build_default_provider_specs
from oif.application.shell_service import OIF2ReadOnlyApplicationService
from oif.ui.navigation_model import build_navigation_model, filter_cards

def main():
    snapshot = OIF2ReadOnlyApplicationService(providers=build_default_provider_specs()).snapshot()
    assert snapshot["read_only"] is True
    assert snapshot["shell_execution_from_renderer"] is False
    assert snapshot["direct_persistence_from_renderer"] is False
    assert tuple(snapshot["zones"]) == tuple(item.zone_id for item in build_navigation_model(snapshot))
    providers = {card["provider"] for card in filter_cards(snapshot, "overview")}
    assert {"validation-report", "runtime-health", "civilizational-state"}.issubset(providers)
    assert any(card["provider"] == "civilizational-state" for card in filter_cards(snapshot, "memory"))
    print("OIF2_3F_NAVIGATION_NON_REGRESSION_OK")
    return 0
if __name__ == "__main__": raise SystemExit(main())
