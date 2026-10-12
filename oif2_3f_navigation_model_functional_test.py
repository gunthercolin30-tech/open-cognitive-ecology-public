from __future__ import annotations
from copy import deepcopy
from oif.ui.navigation_model import build_navigation_model, filter_cards, resolve_active_zone

SNAPSHOT = {
    "zones": {
        "overview": {"access": "read_only", "purpose": "summary"},
        "runtime": {"access": "governed_action", "purpose": "runtime supervision"},
        "memory": {"access": "read_only", "purpose": "continuity"},
    },
    "cards": [
        {"provider": "runtime-health", "zone": "runtime", "access": "governed_action", "payload": {"secret": "not indexed"}},
        {"provider": "civilizational-state", "zone": "memory", "access": "read_only", "payload": {}},
    ],
    "degraded_providers": [],
}

def main():
    before = deepcopy(SNAPSHOT)
    model = build_navigation_model(SNAPSHOT)
    assert [item.zone_id for item in model] == ["overview", "runtime", "memory"]
    assert model[0].provider_count == 0 and model[0].empty is True
    assert model[1].provider_count == 1 and model[1].empty is False
    assert resolve_active_zone(SNAPSHOT, "invalid") == "overview"
    assert [c["provider"] for c in filter_cards(SNAPSHOT, "runtime")] == ["runtime-health"]
    assert len(filter_cards(SNAPSHOT, "overview")) == 2
    assert filter_cards(SNAPSHOT, "overview", "runtime supervision")[0]["provider"] == "runtime-health"
    assert filter_cards(SNAPSHOT, "overview", "not indexed") == ()
    assert SNAPSHOT == before
    print("OIF2_3F_NAVIGATION_MODEL_FUNCTIONAL_OK")
    return 0
if __name__ == "__main__": raise SystemExit(main())
