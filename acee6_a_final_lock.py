from __future__ import annotations

import json
from pathlib import Path

from acee6_test_requirements_registry import RISK_FAMILIES, STAGES, TEST_REQUIREMENTS
from acee6_transaction_state_contract import SUCCESS_MARKER, TERMINAL_STATES

ROOT = Path.home() / "open-cognitive-ecology"


def main():
    report = json.loads((ROOT / "acee6_non_redundancy_report.json").read_text(encoding="utf-8"))
    assert report["decision"] == "ACEE6_NON_REDUNDANCY_CONFIRMED"
    assert report["implementation_deferred"] is True
    assert len(TEST_REQUIREMENTS) >= 120
    assert len(RISK_FAMILIES) == 20
    assert tuple(STAGES) == tuple("ABCDEFGHIJK")
    assert "COMMITTED" in TERMINAL_STATES
    assert SUCCESS_MARKER == "ACEE_INSTALLATION_EXECUTION_COMPLETE"
    print("ACEE6_A_AUDIT_REQUIREMENTS_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
