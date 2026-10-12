from __future__ import annotations

from pathlib import Path

from oif.adapters.civilizational_state_adapter import CivilizationalStateAdapter

ROOT = Path.home() / "open-cognitive-ecology"


def main() -> int:
    payload = CivilizationalStateAdapter(root=ROOT).read()
    assert payload["source_count"] == 4
    assert payload["available_source_count"] >= 1
    assert payload["read_only"] is True
    assert payload["producer_execution"] is False
    rep_section = payload["sections"]["representative_state"]
    if rep_section["availability"] == "available":
        current = rep_section["payload"].get("current_representative", {})
        assert current.get("civilization_identity") != current.get("representative_id")
        assert current.get("representative_is_central") is False
        assert current.get("representative_is_revocable") is True
    print("OIF2_3D_CIVILIZATIONAL_STATE_REAL_SOURCE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
