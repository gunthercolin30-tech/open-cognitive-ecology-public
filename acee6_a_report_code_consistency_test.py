import json
from pathlib import Path

from acee6_a_hardening_contract import BOUNDED_LOOP_POLICY, INTERNAL_SUBSTAGES, PROHIBITED_LOOPS

ROOT = Path.home() / "open-cognitive-ecology"


def main():
    report = json.loads((ROOT / "acee6_a_hardening_report.json").read_text(encoding="utf-8"))
    assert report["runtime_executor_created"] is False
    assert report["bounded_loops_only"] is True
    assert report["automatic_code_repair"] is False
    assert report["automatic_candidate_regeneration"] is False
    assert report["semantic_failure_retry"] is False
    assert report["rollback_failure_leads_to_quarantine"] is True
    assert set(report["internal_substages"]) == set(INTERNAL_SUBSTAGES)
    assert "automatic_code_repair" in PROHIBITED_LOOPS
    assert all(policy["max_attempts"] <= 2 for policy in BOUNDED_LOOP_POLICY.values())
    print("ACEE6_A_REPORT_CODE_CONSISTENCY_OK")


if __name__ == "__main__":
    main()
