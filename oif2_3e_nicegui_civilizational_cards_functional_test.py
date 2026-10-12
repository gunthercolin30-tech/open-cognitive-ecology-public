from __future__ import annotations
from copy import deepcopy
from oif.ui.civilizational_state_cards import build_civilizational_state_view


def fixture():
    return {
        "provider": "civilizational-state",
        "zone": "memory",
        "access": "read_only",
        "payload": {
            "status": "ready",
            "available_source_count": 4,
            "invalid_source_count": 0,
            "read_only": True,
            "translation_only": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "sections": {
                "civilizational_identity": {"availability": "available", "status": "ready", "payload": {"civilizational_identity_preserved": True}},
                "representative_state": {"availability": "available", "status": "ready", "payload": {"current_representative": {"civilization_identity": "Open Cognitive Ecology Society", "representative_id": "REP-0001", "representative_name": "Unnamed Representative", "representative_is_central": False, "representative_is_revocable": True, "status": "active"}}},
                "continuity_state": {"availability": "available", "status": "ready", "payload": {"continuity_validated": True, "continuity_decision": "continuity_preserved"}},
                "succession_state": {"availability": "available", "status": "ready", "payload": {"latest_succession_event": {"execution_status": "blocked", "succession_executed": False}}},
            },
        },
    }


def main():
    source = fixture()
    before = deepcopy(source)
    view = build_civilizational_state_view(source)
    assert source == before
    assert view["civilization_identity"] == "Open Cognitive Ecology Society"
    assert view["representative_id"] == "REP-0001"
    assert view["representative_is_central"] == "non"
    assert view["representative_is_revocable"] == "oui"
    assert [s["name"] for s in view["sections"]] == ["civilizational_identity", "representative_state", "continuity_state", "succession_state"]
    assert view["consciousness_proven"] is False
    assert view["phenomenology_undetermined"] is True
    print("OIF2_3E_NICEGUI_CIVILIZATIONAL_CARDS_FUNCTIONAL_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
