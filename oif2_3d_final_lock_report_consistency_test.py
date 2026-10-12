from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "oif2_3d_civilizational_state_adapter_final_lock_report.json"
REQUIRED_TRUE = (
    "controlled_degradation_validated",
    "external_storage_path_policy_validated",
    "direct_source_symlink_rejection_validated",
    "real_source_validated",
    "species_representative_distinction_validated",
    "renderer_direct_read_absent",
    "renderer_direct_write_absent",
    "source_immutability_validated",
)


def main() -> int:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["status"] == "locked"
    assert report["primitive"] == "oif2_civilizational_state_adapter"
    assert report["adapter_schema_version"] == "oif2.civilizational-state-adapter.v1"
    assert report["read_only"] is True
    assert report["translation_only"] is True
    assert report["producer_execution"] is False
    assert report["synthetic_cross_source_score"] is False
    assert report["functional_conclusion_only"] is True
    assert report["consciousness_proven"] is False
    assert report["phenomenology_undetermined"] is True
    for key in REQUIRED_TRUE:
        assert report.get(key) is True, key
    assert report["separate_source_sections"] == [
        "civilizational_identity", "representative_state",
        "continuity_state", "succession_state",
    ]
    for relative, expected in report["hashes"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert actual == expected, relative
    print("OIF2_3D_FINAL_LOCK_REPORT_CONSISTENCY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
