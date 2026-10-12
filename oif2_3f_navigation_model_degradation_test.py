from __future__ import annotations
from oif.ui.navigation_model import build_navigation_model, filter_cards

def main():
    snapshot = {
        "zones": {"overview": {"access": "read_only", "purpose": "summary"}, "science": {"access": "read_only", "purpose": "science"}},
        "cards": [{"provider": "validation-report", "zone": "science", "access": "read_only", "payload": {"status": "unavailable"}}],
        "degraded_providers": [{"provider": "validation-report", "zone": "science", "error_type": "ValueError"}],
    }
    model = build_navigation_model(snapshot)
    science = next(item for item in model if item.zone_id == "science")
    assert science.degraded_count == 1
    assert filter_cards({}, "overview") == ()
    assert build_navigation_model({}) == ()
    print("OIF2_3F_NAVIGATION_MODEL_DEGRADATION_OK")
    return 0
if __name__ == "__main__": raise SystemExit(main())
