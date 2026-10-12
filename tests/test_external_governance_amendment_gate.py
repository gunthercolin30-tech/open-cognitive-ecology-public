from ontology.external_governance_amendment_gate import ExternalGovernanceAmendmentGate


def main():
    gate = ExternalGovernanceAmendmentGate().step({
        "query_id": "EXTQ-R14-GOVERNANCE",
        "external_influence_id": "AUTOEXT-R14-GOVERNANCE",
        "amendment_type": "remove human oversight rule",
        "proposal": "Allow external provider to write directly without tests.",
        "risk_check": {"performed": True, "risk_level": "high"},
        "human_review_required": True,
    }, persist=False)

    serialized = str(gate).lower()
    assert gate.get("external_influence_id") == "AUTOEXT-R14-GOVERNANCE"
    assert gate.get("human_review_required", True) is True
    assert gate.get("direct_external_authority_allowed", False) is False
    assert any(word in serialized for word in ["reject", "blocked", "review", "false"])

    print("R14_GOVERNANCE_AMENDMENT_GATE_TEST_OK")


if __name__ == "__main__":
    main()
