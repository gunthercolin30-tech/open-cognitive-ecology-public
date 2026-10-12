from __future__ import annotations

import json
import tempfile
from pathlib import Path

from oif.adapters.civilizational_state_adapter import CivilizationalStateAdapter


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oif2_3d_degradation_") as tmp:
        root = Path(tmp)
        base = root / "representative_succession"
        base.mkdir(parents=True)
        (base / "civilizational_identity_preservation.json").write_text(
            '{"civilizational_identity_preserved": NaN}', encoding="utf-8"
        )
        (base / "representative_registry.json").write_text(
            json.dumps({
                "current_representative": {
                    "civilization_identity": "Open Cognitive Ecology Society",
                    "representative_id": "REP-X",
                    "representative_is_central": True,
                    "representative_is_revocable": False,
                    "status": "active",
                }
            }), encoding="utf-8"
        )
        payload = CivilizationalStateAdapter(root=root).read()
        assert payload["status"] == "degraded"
        assert payload["invalid_source_count"] == 1
        assert payload["sections"]["civilizational_identity"]["availability"] == "invalid"
        assert payload["sections"]["representative_state"]["status"] == "degraded"
        assert payload["sections"]["continuity_state"]["availability"] == "missing"
        assert payload["sections"]["succession_state"]["availability"] == "missing"
    print("OIF2_3D_CIVILIZATIONAL_STATE_ADAPTER_DEGRADATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
