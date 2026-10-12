from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "oif2_3e_nicegui_civilizational_cards_final_lock_report.json"

def main():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["status"] == "locked"
    assert report["provider_name"] == "civilizational-state"
    assert report["zone"] == "memory"
    for rel, expected in report["sha256"].items():
        actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        assert actual == expected, rel
    assert report["direct_adapter_import_absent"] is True
    assert report["direct_persistent_state_read_absent"] is True
    assert report["business_logic_in_renderer_absent"] is True
    assert report["consciousness_proven"] is False
    assert report["phenomenology_undetermined"] is True
    print("OIF2_3E_FINAL_LOCK_REPORT_CONSISTENCY_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
