from acee6_a_contract_snapshot import EMPIRICAL_TRACEABILITY
from acee6_test_requirements_registry import RISK_FAMILIES, TEST_REQUIREMENTS


def main():
    assert set(EMPIRICAL_TRACEABILITY) == set(RISK_FAMILIES)
    for family, trace in EMPIRICAL_TRACEABILITY.items():
        assert isinstance(trace["origin"], str) and trace["origin"].strip()
        assert isinstance(trace["evidence"], tuple) and trace["evidence"]
        assert all(isinstance(item, str) and item.strip() for item in trace["evidence"])
        assert any(req["risk_family"] == family for req in TEST_REQUIREMENTS)
    assert any("specific" not in trace["origin"].lower() for trace in EMPIRICAL_TRACEABILITY.values())
    print("ACEE6_A_EMPIRICAL_TRACEABILITY_OK")


if __name__ == "__main__":
    main()
