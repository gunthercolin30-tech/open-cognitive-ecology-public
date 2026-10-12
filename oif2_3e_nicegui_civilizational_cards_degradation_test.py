from __future__ import annotations
from oif.ui.civilizational_state_cards import build_civilizational_state_view


def main():
    cases = [
        {},
        {"provider": "civilizational-state", "payload": None},
        {"provider": "civilizational-state", "payload": {"status": "degraded", "sections": {"representative_state": {"availability": "invalid", "status": "unavailable", "error_type": "ValueError", "payload": None}}}},
    ]
    for card in cases:
        view = build_civilizational_state_view(card)
        assert len(view["sections"]) == 4
        assert isinstance(view["technical_payload"], dict)
        assert view["civilization_identity"]
        assert view["representative_name"]
    print("OIF2_3E_NICEGUI_CIVILIZATIONAL_CARDS_DEGRADATION_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
