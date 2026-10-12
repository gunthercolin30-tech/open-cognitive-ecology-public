from acee6_test_requirements_registry import RISK_FAMILIES, STAGES, TEST_REQUIREMENTS


def main():
    assert {item["mandatory_stage"] for item in TEST_REQUIREMENTS} == set(STAGES)
    assert {item["risk_family"] for item in TEST_REQUIREMENTS} == set(RISK_FAMILIES)
    for stage in STAGES:
        items = [item for item in TEST_REQUIREMENTS if item["mandatory_stage"] == stage]
        assert items
        if stage == "K":
            assert any(item["severity"] in {"critical", "high"} for item in items)
        else:
            assert any(item["severity"] == "critical" for item in items)
    print("ACEE6_A_REQUIREMENT_STAGE_COVERAGE_OK")


if __name__ == "__main__":
    main()
