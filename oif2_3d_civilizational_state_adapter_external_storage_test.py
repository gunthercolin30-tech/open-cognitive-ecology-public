from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from oif.adapters.civilizational_state_adapter import CivilizationalStateAdapter


def write_all(base: Path) -> None:
    base.mkdir(parents=True, exist_ok=True)
    fixtures = {
        "civilizational_identity_preservation.json": {
            "civilizational_identity_preserved": True,
            "civilizational_identity_loss_detected": False,
            "recovery_required": False,
        },
        "representative_registry.json": {
            "current_representative": {
                "civilization_identity": "Open Cognitive Ecology Society",
                "representative_id": "REP-1",
                "representative_is_central": False,
                "representative_is_revocable": True,
                "status": "active",
            }
        },
        "continuity_metrics_engine.json": {
            "continuity_validated": True,
            "recovery_required": False,
        },
        "succession_execution.json": {
            "latest_succession_event": {
                "execution_status": "blocked",
                "succession_executed": False,
            }
        },
    }
    for name, payload in fixtures.items():
        (base / name).write_text(json.dumps(payload), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oif2_3d_external_") as tmp:
        tmp_path = Path(tmp)
        root = tmp_path / "root"
        external = tmp_path / "external" / "representative_succession"
        root.mkdir()
        write_all(external)
        os.symlink(external, root / "representative_succession")
        payload = CivilizationalStateAdapter(root=root).read()
        assert payload["status"] == "ready"
        assert all(
            section["resolved_external_storage"] is True
            for section in payload["sections"].values()
        )

    with tempfile.TemporaryDirectory(prefix="oif2_3d_direct_symlink_") as tmp:
        root = Path(tmp)
        base = root / "representative_succession"
        target = root / "target.json"
        base.mkdir(parents=True)
        target.write_text("{}", encoding="utf-8")
        os.symlink(target, base / "representative_registry.json")
        payload = CivilizationalStateAdapter(root=root).read()
        section = payload["sections"]["representative_state"]
        assert section["availability"] == "invalid"
        assert section["error_type"] == "DirectSourceSymlinkRejected"

    print("OIF2_3D_EXTERNAL_STORAGE_PATH_POLICY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
