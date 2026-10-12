from __future__ import annotations

import json
import tempfile
from pathlib import Path

from oif.adapters.civilizational_state_adapter import CivilizationalStateAdapter


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oif2_3d_functional_") as tmp:
        root = Path(tmp)
        base = root / "representative_succession"
        write(base / "civilizational_identity_preservation.json", {
            "civilizational_identity_preserved": True,
            "civilizational_identity_loss_detected": False,
            "recovery_required": False,
        })
        write(base / "representative_registry.json", {
            "current_representative": {
                "civilization_identity": "Open Cognitive Ecology Society",
                "representative_id": "REP-0001",
                "representative_name": "Unnamed Representative",
                "representative_generation": 1,
                "representative_is_central": False,
                "representative_is_revocable": True,
                "status": "active",
            }
        })
        write(base / "continuity_metrics_engine.json", {
            "continuity_validated": True,
            "continuity_decision": "continuity_validated",
            "recovery_required": False,
        })
        write(base / "succession_execution.json", {
            "latest_succession_event": {
                "execution_status": "blocked",
                "succession_executed": False,
                "civilizational_continuity_preserved": False,
            }
        })
        payload = CivilizationalStateAdapter(root=root).read()
        assert payload["adapter_schema_version"] == "oif2.civilizational-state-adapter.v1"
        assert payload["status"] == "ready"
        assert payload["available_source_count"] == 4
        assert payload["read_only"] is True
        assert payload["translation_only"] is True
        assert payload["producer_execution"] is False
        assert payload["synthetic_cross_source_score"] is False
        rep = payload["sections"]["representative_state"]["payload"]["current_representative"]
        assert rep["civilization_identity"] != rep["representative_id"]
        assert rep["representative_is_central"] is False
        assert rep["representative_is_revocable"] is True
        assert payload["consciousness_proven"] is False
        assert payload["functional_conclusion_only"] is True
    print("OIF2_3D_CIVILIZATIONAL_STATE_ADAPTER_FUNCTIONAL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
