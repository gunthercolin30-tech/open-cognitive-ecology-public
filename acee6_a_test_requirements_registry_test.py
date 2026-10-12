from __future__ import annotations

from acee6_test_requirements_registry import (
    RISK_FAMILIES,
    STAGES,
    TEST_REQUIREMENTS,
    registry_summary,
)


def main():
    assert len(TEST_REQUIREMENTS) >= 120
    ids = [item["test_id"] for item in TEST_REQUIREMENTS]
    assert len(ids) == len(set(ids))
    assert {item["risk_family"] for item in TEST_REQUIREMENTS} == set(RISK_FAMILIES)
    assert set(STAGES) <= {item["mandatory_stage"] for item in TEST_REQUIREMENTS}
    assert all(item["expected_marker"].startswith("ACEE6_") for item in TEST_REQUIREMENTS)
    assert all(item["timeout_seconds"] > 0 for item in TEST_REQUIREMENTS)
    critical = [item for item in TEST_REQUIREMENTS if item["severity"] == "critical"]
    assert len(critical) >= 80
    assert all(item["eligible_for_full_validation"] for item in TEST_REQUIREMENTS)
    summary = registry_summary()
    assert summary["requirement_count"] == len(TEST_REQUIREMENTS)
    assert summary["risk_family_count"] == 20
    assert summary["stage_count"] == 11
    assert summary["functional_conclusion_only"] is True
    assert summary["phenomenology_undetermined"] is True
    print("ACEE6_A_TEST_REQUIREMENTS_REGISTRY_OK")


if __name__ == "__main__":
    main()
