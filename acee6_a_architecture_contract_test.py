from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"


def main():
    report_path = ROOT / "acee6_non_redundancy_report.json"
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["decision"] == "ACEE6_NON_REDUNDANCY_CONFIRMED"
    assert data["implementation_deferred"] is True
    assert data["current_stage"] == "ACEE6-A"
    reviewed = data["reviewed_primitives"]
    for name in (
        "acee_governed_code_generation_gate",
        "acee_validation_runner",
        "acee_rollback_engine",
        "controlled_execution_layer",
        "governed_execution_dispatcher",
    ):
        assert name in reviewed
    forbidden = set(data["forbidden_responsibilities"])
    assert "generate candidate code" in forbidden
    assert "select the improvement candidate" in forbidden
    assert data["functional_conclusion_only"] is True
    assert data["phenomenology_undetermined"] is True
    print("ACEE6_A_ARCHITECTURE_CONTRACT_OK")


if __name__ == "__main__":
    main()
